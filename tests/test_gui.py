# -*- coding: utf-8 -*-
"""화면 테스트. 창을 화면에 내보내지 않고(offscreen) 위젯을 직접 눌러 처음 실행부터 다시 채점까지 돌려 봄.

실제 문제 은행을 쓰되 풀이 폴더는 임시 폴더로 돌리고, 제출 모듈은 가짜를 끼움. PyQt6 가 없으면 전부 건너뜀.
실행: python -m unittest discover -s tests
"""
import contextlib
import io
import itertools
import os
import re
import shutil
import sys
import tempfile
import time
import unittest
from unittest import mock

try:
    from PyQt6.QtCore import QEvent, QEventLoop, QMimeData, QPoint, QPointF, QSettings, Qt, QTimer, qInstallMessageHandler
    from PyQt6.QtGui import QColor, QContextMenuEvent, QDragEnterEvent, QDropEvent, QGuiApplication, QKeyEvent, QTextCursor, qGray
    from PyQt6.QtTest import QTest
    from PyQt6.QtWidgets import QApplication, QLabel, QPushButton
except ImportError:
    raise unittest.SkipTest("PyQt6 가 설치돼 있지 않아 화면 테스트를 건너뜁니다")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import adaptive  # noqa: E402
import mdlite  # noqa: E402
import session  # noqa: E402
import study  # noqa: E402
from gui import app, dialogs, errors, icon, motion, theme  # noqa: E402
from gui.mascot import Mascot  # noqa: E402
from gui.guard import NOTE as PASTE_NOTE  # noqa: E402
from gui.team_page import Avatar, EmptyCard, MemberCard  # noqa: E402
from gui.widgets import ChoiceCard, ChoicePanel, CodeEditor, content_height  # noqa: E402
from gui.window import MainWindow  # noqa: E402

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
NOISE = ("propagateSizeHints", "Populating font family aliases")  # offscreen 플랫폼이 창을 띄울 때마다 찍는 안내
qInstallMessageHandler(lambda mode, context, text: None if any(n in text for n in NOISE) else print(text, file=sys.stderr))
APP = QApplication.instance() or QApplication(sys.argv[:1])
theme.apply(APP)
motion.enabled = False  # 움직임은 MotionTest 에서만 켬
LEFT = Qt.MouseButton.LeftButton
SHIFT = Qt.KeyboardModifier.ShiftModifier
CTRL = Qt.KeyboardModifier.ControlModifier


def pump(ms=30):
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec()


def wait_until(predicate, timeout=30.0):
    start = time.monotonic()
    while not predicate():
        if time.monotonic() - start > timeout:
            raise TimeoutError("화면이 기다리던 상태가 되지 않았습니다")
        pump(20)


def click(widget):
    QTest.mouseClick(widget, LEFT)
    pump()


def gray(value):
    """색의 밝기(0~255)."""
    return qGray(QColor(value).rgb())


def contrast(ink, back):
    """글자색과 바탕색의 대비(WCAG 2 의 계산식)."""
    def luminance(value):
        color = QColor(value)
        red, green, blue = (v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in (color.redF(), color.greenF(), color.blueF()))
        return 0.2126 * red + 0.7152 * green + 0.0722 * blue
    low, high = sorted((luminance(ink), luminance(back)))
    return (high + 0.05) / (low + 0.05)


def backgrounds(text):
    """스타일시트나 HTML 에 적힌 바탕색. Qt 는 표 칸의 바탕색을 bgcolor 속성으로 내보냄."""
    return re.findall(r"(?:background(?:-color)?:\s*|bgcolor=\")(#[0-9a-fA-F]{6})", text)


def bright_share(widget):
    """위젯에서 밝은 바탕이 차지하는 비율. 찍은 그림을 가로세로 8분의 1로 줄여 밝은 칸이 가로로 6칸(48px) 넘게 이어진 곳만 셈.
    글자는 줄어들며 바탕과 섞이고 굵은 획도 그만큼 이어지지 않아서, 밝은 글자는 빠지고 밝은 바탕만 남음."""
    image = widget.grab().toImage()
    step = int(8 * image.devicePixelRatio())
    small = image.scaled(image.width() // step, image.height() // step, Qt.AspectRatioMode.IgnoreAspectRatio,
                         Qt.TransformationMode.SmoothTransformation)
    found = 0
    for y in range(small.height()):
        row = "".join("1" if qGray(small.pixel(x, y)) > 215 else "0" for x in range(small.width()))
        found += sum(len(run) for run in re.findall("1{6,}", row))
    return found / (small.width() * small.height())


class FakeGitFlow:
    """제출 모듈처럼 예외 없이 dict 를 돌려주는 가짜. replies 에 메서드별 응답을 넣어 상황을 만듦."""

    def __init__(self):
        self.calls, self.replies, self.delay = [], {}, 0

    def _reply(self, name):
        self.calls.append(name)
        time.sleep(self.delay)
        base = {"status": "nothing", "message": "", "detail": "", "pr_url": None, "restart": False, "changed": False, "backup": None}
        return dict(base, **self.replies.get(name.split(":")[0], {}))

    def sync(self):
        return self._reply("sync")

    def submit(self):
        return self._reply("submit")

    def resolve(self, choice):
        return self._reply("resolve:" + choice)


def right_answer(sess, view):
    it = sess.cat[view["key"]]
    if it["kind"] == "quiz":
        q = it["q"]
        return q["answer"] if q["type"] != "short" else q["answer"][0]
    return it["set"]["secrets"][it["spec"]["id"] + "/solution.py"]


class GuiTest(unittest.TestCase):
    user = "tester"  # None 이면 처음 실행이라 ID 를 물음
    git_reason = ""  # 채우면 제출 모듈을 불러오지 못한 상황
    expect_error = False  # 오류 대화상자가 뜨는 것이 정상인 테스트

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="study_gui_")
        self._saved = (study.SUBMISSIONS_DIR, study.USER_FILE, os.environ.pop("STUDY_USER", None), sys.excepthook)
        study.SUBMISSIONS_DIR = os.path.join(self.tmp, "submissions")
        study.USER_FILE = os.path.join(self.tmp, ".study_user")
        self.logs = os.path.join(self.tmp, ".study_logs")
        errors.install(self.logs)
        if self.user:
            session.save_user(self.user)
        self.git, self.opened = FakeGitFlow(), []
        self.settings = QSettings(os.path.join(self.tmp, "settings.ini"), QSettings.Format.IniFormat)
        self.win = MainWindow(self.settings, lambda root, user: (None if self.git_reason else self.git, self.git_reason))
        self.win.open_url = self.opened.append
        self.win.show()

    def tearDown(self):
        wait_until(lambda: self.win.job is None)
        self.win.close()
        self.win.deleteLater()
        pump()
        crashed = os.path.isdir(self.logs) and not self.expect_error  # 슬롯 안의 예외는 테스트로 올라오지 않고 기록만 남음
        report = "".join(study.read_text(os.path.join(self.logs, name)) for name in os.listdir(self.logs)) if crashed else ""
        if errors.state["dialog"] is not None:
            errors.state["dialog"].close()
        study.SUBMISSIONS_DIR, study.USER_FILE, user, sys.excepthook = self._saved
        if user is not None:
            os.environ["STUDY_USER"] = user
        shutil.rmtree(self.tmp, ignore_errors=True)
        self.assertFalse(crashed, report)

    # 도우미

    def idle(self):
        pump()
        wait_until(lambda: self.win.job is None)
        pump()

    def boot(self):
        self.win.boot()
        self.idle()

    def page(self):
        return self.win.pages.currentWidget()

    def choose(self, key):
        """떠 있는 대화상자에서 버튼을 누름."""
        dialog = self.win.dialog
        self.assertTrue(dialog.isVisible())
        click(dialog.buttons[key])
        return dialog

    def select(self, predicate):
        """회차 화면에서 조건에 맞는 첫 문항으로 감."""
        page = self.win.round_page
        item = next(it for it in page.view["items"] if predicate(it))
        page.listw.setCurrentRow(item["no"] - 1)
        pump()
        self.assertIs(page.current, item)
        return item

    def fill(self, item, value):
        """지금 보이는 문항에 위젯으로 답을 넣음."""
        page = self.win.round_page
        if item["kind"] == "code":
            page.code_panel.editor.setPlainText(value)
        elif item["type"] == "choice":
            for number, button in enumerate(page.choice_panel.buttons, 1):
                if button.isChecked() != (number in value):
                    click(button)
        elif item["type"] == "output":
            page.text_panel.multi.setPlainText(value)
        else:
            page.text_panel.single.setText(value)

    def answer_round(self, skip=()):
        """정답을 위젯으로 넣음. skip 의 번호는 비워 둠."""
        page = self.win.round_page
        for item in list(page.view["items"]):
            if item["no"] not in skip:
                self.select(lambda it: it is item)
                self.fill(item, right_answer(self.win.session, item))

    def make_round(self, rid, keys, completed=False):
        """진단·회차는 무작위라 유형이 빠질 수 있어, 고른 문항으로 회차를 직접 만듦."""
        sess = self.win.session
        rnd = {"id": rid, "kind": "round", "focus": [], "items": keys, "retest": [], "shortages": [], "created": adaptive.now(),
               "tries": 0, "avg_level": 1}
        if completed:
            rnd.update(completed_at=adaptive.now(), score="0/0", first_score="0/0", results={key: "skipped" for key in keys})
        sess.prof["rounds"].append(rnd)
        adaptive.write_round("tester", rnd, sess.cat)
        adaptive.save_profile(sess.prof)

    def saved_quiz(self, rid):
        return study.parse_quiz_answers(os.path.join(self.win.session.folder(rid), "quiz.py"))[0]

    def submit_round(self):
        click(self.win.round_page.submit_btn)
        dialog = self.choose("submit")
        self.idle()
        return dialog

    def attempts(self):
        return adaptive.load_profile("tester")["attempts"]

    def first(self, **want):
        """조건에 맞는 은행의 첫 문항 키."""
        cat = self.win.session.cat
        multi = want.pop("multi", None)
        return next(key for key in sorted(cat, key=study.natural_key)
                    if all(cat[key][name] == value for name, value in want.items())
                    and (multi is None or (len(cat[key]["q"]["answer"]) > 1) == multi))


class FirstRunTest(GuiTest):
    user = None

    def test_from_first_run_to_regrade(self):
        win, home, page, result = self.win, self.win.home, self.win.round_page, self.win.result_page

        # 처음 실행: ID 를 묻고 형식을 검사한 뒤 새 문제부터 받음
        win.boot()
        dialog = win.dialog
        self.assertTrue(dialog.isVisible())
        self.assertFalse(dialog.ok.isEnabled())
        QTest.keyClicks(dialog.edit, "a b")
        self.assertFalse(dialog.ok.isEnabled())
        self.assertIn("영문", dialog.error.text())
        dialog.edit.clear()
        QTest.keyClicks(dialog.edit, "tester")
        click(dialog.ok)
        self.idle()
        self.assertEqual(session.saved_user(), "tester")
        self.assertEqual(self.git.calls, ["sync"])
        self.assertIs(self.page(), home)
        self.assertEqual(home.action_btn.text(), "진단 테스트 시작")
        self.assertEqual(home.ready.text(), "0%")
        self.assertEqual(home.strip.cells.count(), len(adaptive.units()))
        first_unit = adaptive.units()[0]
        self.assertEqual(home.strip.cells.itemAt(0).widget().toolTip(),
                         "%s %s\n미진단" % (first_unit["id"], adaptive.short_title(first_unit)))

        # 진단 시작 → 문항 목록
        click(home.action_btn)
        self.assertIs(self.page(), page)
        self.assertEqual(page.view["id"], "d1")
        self.assertEqual(page.listw.count(), len(page.view["items"]))
        self.assertFalse(page.run_btn.isVisible())
        self.assertFalse(page.banner.isVisible())

        # 객관식: 하나만 선택되고 다시 누르면 풀림
        choice = self.select(lambda it: it["type"] == "choice" and not it["multi"])
        buttons = page.choice_panel.buttons
        self.assertEqual(len(buttons), choice["choices"])
        click(buttons[0])
        click(buttons[1])
        self.assertEqual([b.isChecked() for b in buttons[:2]], [False, True])
        self.assertTrue(page.listw.item(choice["no"] - 1).data(Qt.ItemDataRole.UserRole))  # 목록의 동그라미가 채워짐
        click(buttons[1])
        self.assertFalse(any(b.isChecked() for b in buttons))
        self.assertFalse(page.listw.item(choice["no"] - 1).data(Qt.ItemDataRole.UserRole))
        click(buttons[1])
        pump(save_delay())  # 다른 문항으로 가지 않아도 잠시 뒤 저장됨
        self.assertEqual(self.saved_quiz("d1")[choice["id"]], 2)

        # 정답으로 채우되 두 문항은 비워 둠 → 확인 대화상자가 번호를 보여 줌
        self.answer_round(skip={2, 5})
        self.select(lambda it: it["no"] == 2)
        self.fill(page.current, [] if page.current["type"] == "choice" else "")
        self.select(lambda it: it["no"] == 5)
        self.fill(page.current, [] if page.current["type"] == "choice" else "")
        click(page.submit_btn)
        self.assertIn("미응답 문항: 2, 5번", win.dialog.text.text())
        self.assertIn("미응답은 오답으로 처리됩니다", win.dialog.text.text())
        self.choose("")  # 계속 풀기
        self.idle()
        self.assertIs(self.page(), page)
        self.assertEqual(self.attempts(), [])
        self.submit_round()

        # 결과: 점수 · 준비도 · 문항별 결과 · 해설
        size = len(page.view["items"])
        self.assertIs(self.page(), result)
        self.assertEqual(len(self.attempts()), size)
        self.assertEqual(sum(1 for a in self.attempts() if a["ok"]), size - 2)
        self.assertEqual(result.listw.count(), size + 1)
        self.assertIn("진단 테스트 결과", result.title.text())
        self.assertNotEqual(result.ready.text(), "시험 준비도 0%")
        self.assertIn("미응답 2문항", result.detail.toPlainText())
        self.assertFalse(result.explain_btn.isEnabled())
        result.listw.setCurrentRow(2)  # 비워 둔 2번
        self.assertIn("미응답", result.listw.item(2).text())
        self.assertIn("내 답", result.detail.toPlainText())
        self.assertNotIn("해설", result.detail.toPlainText())
        self.assertTrue(result.retry_btn.isEnabled())
        click(result.explain_btn)
        quiz = result.selected()
        info = win.session.explain("d1", quiz["id"])
        self.assertIn("정답", result.detail.toPlainText())
        self.assertIn(info["explain"].replace("`", "").replace("**", "")[:12], result.detail.toPlainText())
        result.listw.setCurrentRow(1)
        self.assertFalse(result.retry_btn.isEnabled())  # 맞힌 문항

        # 다음 회차: 코드 문항에서 코드 입력 → 코드 실행(기록 없음)
        self.assertEqual(result.next_btn.text(), "1회차 시작")
        click(result.next_btn)
        self.assertEqual(page.view["id"], "r01")
        code = self.select(lambda it: it["kind"] == "code")
        self.assertTrue(page.run_btn.isVisible())
        self.assertEqual(page.code_panel.editor.toPlainText(), code["starter"])
        before = len(self.attempts())
        self.fill(code, right_answer(win.session, code))
        click(page.run_btn)
        self.assertFalse(page.stack.isEnabled())  # 실행 중에는 입력을 잠금
        self.idle()
        self.assertTrue(page.stack.isEnabled())
        self.assertIn("통과", page.code_panel.console.toPlainText())
        self.assertIn("기록되지 않습니다", page.code_panel.console.toPlainText())
        self.assertEqual(study.read_text(os.path.join(win.session.folder("r01"), code["id"] + ".py")).rstrip("\n"),
                         right_answer(win.session, code).rstrip("\n"))
        self.assertEqual(len(self.attempts()), before)

        # 1회차 제출 → 단원별 판정과 코드 문제 해설(모범 답안)
        self.answer_round(skip={1})
        self.submit_round()
        self.assertIs(self.page(), result)
        self.assertIn("1회차", result.title.text())
        self.assertIn("판정", result.detail.toPlainText())
        self.assertIn("레벨", result.detail.toPlainText())
        result.listw.setCurrentRow(code["no"])
        click(result.explain_btn)
        self.assertIn("모범 답안", result.detail.toPlainText())
        self.assertIn(win.session.explain("r01", code["id"])["solution"].split("\n")[0], result.detail.toPlainText())

        # 홈: 준비도와 지난 회차 목록
        click(result.home_btn)
        self.assertIs(self.page(), home)
        self.assertEqual(home.rounds.count(), 2)
        self.assertIn("진단 테스트", home.rounds.item(1).text())
        self.assertEqual(home.action_btn.text(), "2회차 시작")
        self.assertNotEqual(home.ready.text(), "0%")
        self.assertIn("정답률", home.strip.cells.itemAt(0).widget().toolTip())

        # 지난 회차를 눌러 결과 보기 → 틀린 문항 다시 풀기 → 다시 채점(연습)
        QTest.mouseClick(home.rounds.viewport(), LEFT, pos=home.rounds.visualItemRect(home.rounds.item(1)).center())
        pump()
        self.assertIs(self.page(), result)
        self.assertEqual(result.view["id"], "d1")
        old_score = result.score.text()
        result.listw.setCurrentRow(2)
        click(result.retry_btn)
        self.assertIs(self.page(), page)
        self.assertTrue(page.banner.isVisible())
        self.assertIn("첫 제출만 반영", page.banner.text())
        self.assertEqual(page.submit_btn.text(), "다시 채점")
        self.assertEqual(page.current["no"], 2)
        tried = len(self.attempts())
        self.fill(page.current, right_answer(win.session, page.current))
        click(page.submit_btn)
        self.idle()
        self.assertIs(self.page(), result)
        self.assertNotEqual(result.score.text(), old_score)
        self.assertIn("첫 제출", result.note.text())
        again = self.attempts()[tried:]
        self.assertEqual([(a["round"], a["try"], a["ok"]) for a in again], [("d1", 2, True)])
        rnd = adaptive.find_round(adaptive.load_profile("tester"), "d1")
        self.assertNotEqual(rnd["score"], rnd["first_score"])

    def test_id_box_accepts_paste(self):
        self.win.boot()
        dialog = self.win.dialog
        QGuiApplication.clipboard().setText("tester")
        QTest.keyClick(dialog.edit, Qt.Key.Key_V, CTRL)
        self.assertEqual(dialog.edit.text(), "tester")
        click(dialog.ok)
        self.idle()
        self.assertEqual(session.saved_user(), "tester")

    def test_id_that_already_has_a_record_is_confirmed_once(self):
        """이미 풀이 기록이 있는 ID 를 넣으면 한 번 확인받고, 대소문자가 달라도 그 폴더의 철자로 이어 감."""
        session.Session("Tester").ensure_round()
        self.win.boot()
        dialog = self.win.dialog
        self.assertNotIn("WaterMinCho", dialog.edit.placeholderText())  # 예시가 실제 ID 면 그대로 넣는 사람이 생김
        QTest.keyClicks(dialog.edit, "tester")
        click(dialog.ok)
        self.assertTrue(dialog.isVisible())  # 아직 저장하지 않음
        self.assertIsNone(session.saved_user())
        self.assertIn("Tester 의 풀이 기록", dialog.error.text())
        self.assertEqual(dialog.ok.text(), "이 기록으로 시작")
        for label in dialog.findChildren(QLabel):  # 안내가 두 줄로 늘어도 위의 설명이 눌려 잘리지 않음
            self.assertGreaterEqual(label.height(), label.heightForWidth(label.width()), label.text())
        click(dialog.ok)
        self.idle()
        self.assertEqual(session.saved_user(), "Tester")
        self.assertEqual(self.win.home.user.text(), "ID: Tester")
        self.assertEqual(self.win.home.action_btn.text(), "진단 테스트 시작")
        self.assertEqual(os.listdir(study.SUBMISSIONS_DIR), ["Tester"])


class HomeAndGitTest(GuiTest):
    def test_offline_at_start_is_one_line_notice_and_work_continues(self):
        self.git.replies["sync"] = {"status": "offline", "message": "인터넷에 연결되지 않아 새 문제를 받지 못했습니다.", "detail": "git fetch 실패"}
        self.boot()
        home = self.win.home
        self.assertIs(self.page(), home)
        self.assertTrue(home.notice.isVisible())
        self.assertIn("인터넷에 연결되지 않아", home.notice.text())
        self.assertTrue(home.action_btn.isEnabled())
        self.assertTrue(home.git_btn.isEnabled())
        self.win.show_notice_detail()
        self.assertEqual(self.win.dialog.detail.toPlainText(), "git fetch 실패")
        self.choose("ok")

    def test_tool_update_at_start_restarts(self):
        self.git.replies["sync"] = {"status": "ok", "message": "프로그램이 새 버전으로 바뀌었습니다. 다시 시작합니다.", "restart": True, "changed": True}
        self.boot()
        self.assertIsNone(self.win.session)  # 옛 코드로 풀이 기록을 열지 않음
        self.assertIn("새 버전", self.win.dialog.text.text())
        self.choose("ok")
        self.assertTrue(self.win.restart)
        self.assertFalse(self.win.isVisible())

    def test_submit_opens_the_pr_page(self):
        self.boot()
        url = "https://github.com/WaterMinCho/rokey-python-study/compare/main...study/tester?quick_pull=1"
        self.git.replies["submit"] = {"status": "ok", "message": "제출했습니다. 브라우저에서 PR 을 확인하세요.", "pr_url": url}
        self.git.delay = 0.3
        click(self.win.home.git_btn)
        self.assertFalse(self.win.home.git_btn.isEnabled())  # 도는 동안 잠금
        self.assertTrue(self.win.home.busy_bar.isVisible())
        self.idle()
        self.git.delay = 0
        self.assertEqual(self.git.calls, ["sync", "submit"])
        self.assertEqual(self.opened, [url])
        self.assertIn("제출했습니다", self.win.dialog.text.text())
        self.assertIn(url, self.win.dialog.link.text())
        self.choose("ok")
        self.assertTrue(self.win.home.git_btn.isEnabled())
        self.git.replies["submit"] = {"status": "auth", "message": "저장소에 올릴 권한이 없습니다.", "pr_url": None, "detail": "git push: 403"}
        click(self.win.home.git_btn)
        self.idle()
        self.assertEqual(self.opened, [url])  # 실패하면 브라우저를 열지 않음
        self.assertIn("권한이 없습니다", self.win.dialog.text.text())
        self.choose("ok")

    def test_diverged_offers_two_choices_and_reloads_after_taking_remote(self):
        self.boot()
        before = self.win.session
        self.git.replies["submit"] = {"status": "diverged", "message": "다른 컴퓨터에서 올린 풀이가 있고, 이 컴퓨터의 풀이와 이어지지 않습니다."}
        self.git.replies["resolve"] = {"status": "ok", "message": "다른 컴퓨터의 풀이를 가져왔습니다.", "changed": True, "backup": "/보관함/사본"}
        click(self.win.home.git_btn)
        self.idle()
        self.assertEqual([b.text() for b in self.win.dialog.buttons.values()][::-1],
                         ["다른 컴퓨터의 풀이 가져오기", "이 컴퓨터 풀이로 올리기", "나중에 정하기"])
        self.choose("remote")
        self.idle()
        self.assertEqual(self.git.calls, ["sync", "submit", "resolve:remote"])
        self.assertIsNot(self.win.session, before)  # 내 풀이 폴더가 바뀌었으므로 새로 읽음
        self.assertIn("가져왔습니다", self.win.dialog.text.text())
        self.assertIn("/보관함/사본", self.win.dialog.text.text())
        self.choose("ok")
        click(self.win.home.git_btn)
        self.idle()
        self.choose("local")
        self.idle()
        self.assertEqual(self.git.calls[-1], "resolve:local")
        self.choose("ok")

    def test_diverged_at_start_still_opens_and_asks(self):
        self.git.replies["sync"] = {"status": "diverged", "message": "다른 컴퓨터에서 올린 풀이가 있고, 이 컴퓨터의 풀이와 이어지지 않습니다."}
        self.boot()
        self.assertIs(self.page(), self.win.home)
        self.assertFalse(self.win.home.notice.isVisible())
        self.assertIn("remote", self.win.dialog.buttons)
        self.choose("")  # 나중에 정하기
        self.idle()
        self.assertEqual(self.git.calls, ["sync"])
        self.assertTrue(self.win.home.action_btn.isEnabled())

    def test_fetching_new_problems_rebuilds_the_session(self):
        self.git.replies["sync"] = {"status": "offline", "message": "인터넷에 연결되지 않아 새 문제를 받지 못했습니다."}
        self.boot()
        self.assertTrue(self.win.home.notice.isVisible())
        before = self.win.session
        self.git.replies["sync"] = {"status": "ok", "message": "새 문제를 받았습니다.", "changed": True}
        click(self.win.home.sync_btn)
        self.idle()
        self.assertIsNot(self.win.session, before)
        self.assertIn("새 문제를 받았습니다", self.win.dialog.text.text())
        self.assertFalse(self.win.home.notice.isVisible())  # 시작할 때의 알림은 지움
        self.choose("ok")

    def test_pending_answers_are_written_before_submitting(self):
        self.boot()
        click(self.win.home.action_btn)
        page = self.win.round_page
        item = self.select(lambda it: it["type"] == "choice")
        click(page.choice_panel.buttons[2])
        self.assertIn(item["id"], page.dirty)  # 아직 저장 전
        click(page.home_btn)
        self.assertEqual(self.saved_quiz("d1")[item["id"]], 3)
        self.assertEqual(self.win.home.action_btn.text(), "진단 테스트 이어 풀기")
        self.assertIn("작성한 문항 1개", self.win.home.action_desc.text())

    def test_closing_the_window_saves_what_was_being_typed(self):
        self.boot()
        click(self.win.home.action_btn)
        item = self.select(lambda it: it["type"] == "choice")
        click(self.win.round_page.choice_panel.buttons[0])
        self.win.close()
        self.assertFalse(self.win.isVisible())
        self.assertEqual(self.saved_quiz("d1")[item["id"]], 1)

    def test_answers_that_could_not_be_saved_are_not_dropped_silently(self):
        """자동 저장이 실패한 답을 화면을 떠나거나 창을 닫을 때 말없이 버리지 않음."""
        self.boot()
        click(self.win.home.action_btn)
        page = self.win.round_page
        item = self.select(lambda it: it["type"] == "choice")
        with mock.patch.object(self.win.session, "set_answer", side_effect=PermissionError(13, "잠김")):
            click(page.choice_panel.buttons[1])
            click(page.home_btn)
            self.assertIs(self.page(), page)  # 홈으로 가지 않음
            self.assertIn("저장되지 않았습니다", self.win.dialog.text.text())
            self.assertNotIn("복사", self.win.dialog.text.text())  # 붙여넣기를 막았으므로 복사해 두라고 안내하지 않음
            self.choose("")
            self.assertFalse(self.win.close())  # 닫히지 않음
            self.assertTrue(self.win.isVisible())
            self.choose("")
            self.assertEqual(list(page.dirty), [item["id"]])
        click(page.home_btn)  # 저장이 되면 그대로 나감
        self.assertIs(self.page(), self.win.home)
        self.assertEqual(self.saved_quiz("d1")[item["id"]], 2)
        click(self.win.home.action_btn)
        self.select(lambda it: it is not None and it["id"] == item["id"])
        with mock.patch.object(self.win.session, "set_answer", side_effect=PermissionError(13, "잠김")):
            click(page.choice_panel.buttons[2])
            click(page.home_btn)
            self.choose("drop")  # 저장하지 않고 나가기
        self.assertIs(self.page(), self.win.home)
        self.assertEqual(self.saved_quiz("d1")[item["id"]], 2)

    def test_broken_answer_sheet_offers_repair(self):
        self.boot()
        click(self.win.home.action_btn)
        page = self.win.round_page
        for number in (1, 2, 3):
            item = self.select(lambda it: it["no"] == number)
            self.fill(item, [1] if item["type"] == "choice" else "x")
        click(page.home_btn)
        path = os.path.join(self.win.session.folder("d1"), "quiz.py")
        good = study.read_text(path)
        study.write_text(path, "<<<<<<< HEAD\n" + good + "=======\n>>>>>>> main\n")
        click(self.win.home.action_btn)
        self.assertIs(self.page(), self.win.home)  # 열지 않고 복구를 제안함
        self.assertIn("quiz.py.bak", self.win.dialog.text.text())
        self.choose("repair")
        self.assertTrue(os.path.isfile(path + ".bak"))
        self.assertIs(self.page(), page)
        self.assertEqual(sum(1 for it in page.view["items"] if it["answered"]), 3)
        self.assertIn("3개", self.win.dialog.text.text())
        self.choose("ok")
        # 풀던 중에 답안지가 깨지면 저장을 거부하고, 복구한 뒤에 방금 답을 다시 씀
        study.write_text(path, study.read_text(path) + "x = (\n")
        item = self.select(lambda it: it["no"] == 4)
        self.fill(item, [2] if item["type"] == "choice" else "y")
        pump(save_delay())
        self.assertIn("저장하지 못했습니다", page.status.text())
        self.choose("repair")
        self.choose("ok")
        self.assertEqual(sum(1 for v in self.saved_quiz("d1").values() if v is not None), 4)

    def test_copy_paste_and_right_click_are_blocked(self):
        self.boot()
        click(self.win.home.action_btn)
        page = self.win.round_page
        clipboard = QApplication.clipboard()
        clipboard.setText("밖에서 복사한 글")
        for box in (page.body, page.text_panel.multi, page.code_panel.editor):
            box.setPlainText("화면의 글")
            box.selectAll()
            for key in (Qt.Key.Key_C, Qt.Key.Key_X, Qt.Key.Key_V):
                QTest.keyClick(box, key, Qt.KeyboardModifier.ControlModifier)
            self.assertEqual((box.toPlainText(), clipboard.text()), ("화면의 글", "밖에서 복사한 글"))
            menu = QContextMenuEvent(QContextMenuEvent.Reason.Mouse, box.rect().center())
            QApplication.sendEvent(box.viewport(), menu)
            self.assertIsNone(QApplication.activePopupWidget())
        self.assertTrue(page.paste_note.isVisible())
        QTest.keyClick(page.code_panel.editor, Qt.Key.Key_A)  # 보통 글자는 그대로 들어감
        self.assertEqual(page.code_panel.editor.toPlainText(), "a")

    def test_font_size_is_adjustable_and_remembered(self):
        self.boot()
        page = self.win.round_page
        self.assertEqual(page.code_panel.editor.font().pixelSize(), theme.CODE_PX)
        self.assertTrue(page.code_panel.editor.font().fixedPitch())
        click(self.win.home.action_btn)
        self.select(lambda it: it["type"] == "choice")
        card = page.choice_panel.buttons[0]
        self.assertIn("font-size: 14px", card.doc.defaultStyleSheet())
        self.win.set_zoom(2)
        self.assertEqual(page.code_panel.editor.font().pixelSize(), theme.CODE_PX + 2)
        self.assertEqual(page.text_panel.multi.font().pixelSize(), theme.CODE_PX + 2)
        self.assertIn("body { font-size: %dpx" % (14 + theme.DOC_PX + 2), page.body.document().defaultStyleSheet())
        self.assertIn("body { font-size: %dpx" % (14 + theme.DOC_PX + 2), card.doc.defaultStyleSheet())  # 떠 있는 보기 카드도 같이 커짐
        page.body.setHtml(mdlite.to_html("## 제목\n\n본문"))
        sizes, block = [], page.body.document().begin()
        while block.isValid():
            sizes += [block.begin().fragment().charFormat().font().pixelSize()] if block.text() else []
            block = block.next()
        self.assertEqual(sizes, [18 + theme.DOC_PX + 2, 14 + theme.DOC_PX + 2])  # 본문의 제목도 본문 글자와 같이 커짐
        click(page.home_btn)
        self.win.set_zoom(99)
        self.assertEqual(self.win.zoom, theme.ZOOM_RANGE[1])
        self.win.activateWindow()
        QTest.keyClick(self.win, Qt.Key.Key_0, Qt.KeyboardModifier.ControlModifier)
        self.assertEqual(self.win.zoom, 0)
        QTest.keyClick(self.win, Qt.Key.Key_Equal, Qt.KeyboardModifier.ControlModifier)
        QTest.keyClick(self.win, Qt.Key.Key_Minus, Qt.KeyboardModifier.ControlModifier)
        QTest.keyClick(self.win, Qt.Key.Key_Minus, Qt.KeyboardModifier.ControlModifier)
        self.assertEqual(self.win.zoom, -1)
        self.win.set_zoom(3)
        self.win.resize(760, 680)
        size = self.win.size()
        self.win.close()
        again = MainWindow(self.settings, lambda root, user: (self.git, ""))
        self.assertEqual(again.zoom, 3)
        self.assertEqual(again.size(), size)
        again.deleteLater()

    def test_closing_while_a_job_runs_waits_for_it(self):
        self.boot()
        self.win.run_job("오래 걸리는 일", lambda: time.sleep(0.4), lambda result: None)
        self.win.close()
        self.assertTrue(self.win.isVisible())
        wait_until(lambda: not self.win.isVisible(), 5)
        self.assertIsNone(self.win.job)


    def test_submitting_an_untouched_round_warns_first(self):
        self.boot()
        click(self.win.home.action_btn)
        click(self.win.round_page.submit_btn)
        dialog = self.win.dialog
        self.assertIn("아직 작성한 문항이 없습니다", dialog.text.text())
        self.assertFalse(any(button.isDefault() or button.autoDefault() for button in dialog.buttons.values()))  # Enter 로 제출되지 않음
        self.choose("")
        self.assertEqual(self.attempts(), [])


class NoGitTest(GuiTest):
    git_reason = "제출 모듈(gitflow.py)을 불러오지 못했습니다: No module named 'gitflow'"

    def test_screen_works_without_the_submit_module(self):
        self.boot()
        home = self.win.home
        self.assertIs(self.page(), home)
        self.assertFalse(home.git_btn.isEnabled())
        self.assertFalse(home.sync_btn.isEnabled())
        self.assertIn("gitflow.py", home.git_hint.text())
        click(home.action_btn)
        self.assertIs(self.page(), self.win.round_page)
        self.submit_round()
        self.assertIs(self.page(), self.win.result_page)
        self.assertFalse(self.win.result_page.git_btn.isEnabled())


class ErrorTest(GuiTest):
    expect_error = True

    def test_exception_in_a_slot_keeps_the_window_alive(self):
        self.boot()
        boom = QPushButton("boom", self.win)
        boom.clicked.connect(lambda: 1 / 0)
        boom.show()
        with contextlib.redirect_stderr(io.StringIO()):
            click(boom)
        dialog = errors.state["dialog"]
        self.assertTrue(self.win.isVisible())
        self.assertTrue(dialog.isVisible())
        self.assertIn("ZeroDivisionError", dialog.view.toPlainText())
        logs = os.listdir(self.logs)
        self.assertEqual(len(logs), 1)
        self.assertIn("ZeroDivisionError", study.read_text(os.path.join(self.logs, logs[0])))
        click(dialog.copy)
        self.assertIn("ZeroDivisionError", QGuiApplication.clipboard().text())
        dialog.close()
        click(self.win.home.action_btn)  # 오류 뒤에도 계속 쓸 수 있음
        self.assertIs(self.page(), self.win.round_page)

    def test_core_exit_in_the_worker_does_not_kill_the_window(self):
        self.boot()
        done = []
        with contextlib.redirect_stderr(io.StringIO()):
            self.win.run_job("코어가 종료를 부르는 경우", lambda: study.die("없는 세트"), done.append, on_fail=lambda: done.append("fail"))
            self.idle()
        self.assertEqual(done, ["fail"])
        self.assertTrue(self.win.isVisible())
        self.assertIn("SystemExit", errors.state["dialog"].view.toPlainText())
        self.assertTrue(self.win.home.action_btn.isEnabled())  # 잠금이 풀림

    def test_session_error_is_shown_as_is(self):
        self.expect_error = False
        self.boot()

        def fail():
            raise session.SessionError("회차 r99 를 찾을 수 없습니다.")

        self.win.run_job("없는 회차", fail, lambda result: None)
        self.idle()
        self.assertEqual(self.win.dialog.text.text(), "회차 r99 를 찾을 수 없습니다.")
        self.choose("ok")
        self.win.show_result("r99")
        self.assertIn("r99", self.win.dialog.text.text())
        self.choose("ok")

    def test_unreadable_profile_stops_at_the_start_page(self):
        self.expect_error = False
        os.makedirs(os.path.join(study.SUBMISSIONS_DIR, "tester"), exist_ok=True)
        study.write_text(adaptive.profile_path("tester"), '{"rounds": [<<<<<<<')
        self.boot()
        start = self.win.start
        self.assertIs(self.page(), start)
        self.assertIn("profile.json", start.error.text())
        self.assertIn("다시 시도", start.error.text())
        self.assertGreaterEqual(start.error.height(), start.error.heightForWidth(start.error.width()))  # 줄바꿈한 글이 잘리지 않음
        self.assertTrue(start.retry.isVisible())
        os.remove(adaptive.profile_path("tester"))
        click(start.retry)
        self.assertIs(self.page(), self.win.home)


class BankTest(GuiTest):
    def test_each_answer_type_saves_what_the_widgets_show(self):
        self.boot()
        keys = [self.first(type="choice", multi=False), self.first(type="choice", multi=True), self.first(type="short"),
                self.first(type="output"), self.first(type="return"), self.first(type="fill"), self.first(type="print")]
        self.make_round("r90", keys)
        self.win.open_round("r90")
        page = self.win.round_page
        single, multi, short, output, code, fill, _ = page.view["items"]

        # 복수 정답 객관식: 여러 개가 함께 선택됨
        self.select(lambda it: it is multi)
        self.assertIn("모두", page.choice_panel.hint.text())
        click(page.choice_panel.buttons[2])
        click(page.choice_panel.buttons[0])
        self.assertEqual([b.isChecked() for b in page.choice_panel.buttons[:3]], [True, False, True])
        pump(save_delay())  # 다른 문항으로 가지 않아도 입력이 멈추면 저장됨
        self.assertEqual(self.saved_quiz("r90")[multi["id"]], [1, 3])

        # 단답: 한 줄, 한글도 입력한 대로 저장됨
        self.select(lambda it: it is short)
        self.assertIn("따옴표 없이", page.text_panel.hint.text())
        self.assertTrue(page.text_panel.single.isVisible())
        self.assertFalse(page.text_panel.multi.isVisible())
        QTest.keyClicks(page.text_panel.single, "abc 1")
        page.text_panel.single.insert(" 한글")
        pump(save_delay())
        self.assertEqual(self.saved_quiz("r90")[short["id"]], "abc 1 한글")

        # 출력 예측: 여러 줄과 앞 공백이 보이는 대로 저장됨
        self.select(lambda it: it is output)
        self.assertTrue(page.text_panel.multi.isVisible())
        self.assertTrue(page.text_panel.multi.font().fixedPitch())
        QTest.keyClicks(page.text_panel.multi, "line 1")
        QTest.keyClick(page.text_panel.multi, Qt.Key.Key_Return)
        QTest.keyClicks(page.text_panel.multi, "  line 2")
        self.select(lambda it: it is single)  # 문항을 옮기면 기다리지 않고 바로 저장됨
        self.assertEqual(self.saved_quiz("r90")[output["id"]].strip("\n"), "line 1\n  line 2")
        self.assertEqual(self.saved_quiz("r90")[multi["id"]], [1, 3])

        # 코드: 키로 친 내용이 파일에 똑같이 들어가고, 실행 결과에는 함수 안에서 출력한 내용도 보임
        self.select(lambda it: it is code)
        path = os.path.join(self.win.session.folder("r90"), code["id"] + ".py")
        name = self.win.session.cat[code["key"]]["spec"]["cases"][0]["call"].split("(")[0]
        editor = page.code_panel.editor
        editor.clear()
        QTest.keyClicks(editor, "def %s(*args):" % name)
        QTest.keyClick(editor, Qt.Key.Key_Return)
        QTest.keyClicks(editor, "print('debug', len(args))")
        QTest.keyClick(editor, Qt.Key.Key_Return)
        QTest.keyClicks(editor, "return None")
        pump(save_delay())
        self.assertEqual(study.read_text(path), "def %s(*args):\n    print('debug', len(args))\n    return None\n" % name)
        self.assertIn("자동 저장했습니다", page.status.text())
        click(page.run_btn)
        self.idle()
        shown = page.code_panel.console.toPlainText()
        for word in ("실패", "기대한 반환값", "실제 반환값", "None", "함수 안 출력", "debug", "기록되지 않습니다"):
            self.assertIn(word, shown)

        # 무한 루프 코드도 화면을 멈추지 않음
        editor.setPlainText("def %s(*args):\n    while True:\n        pass\n" % name)
        ticks = []
        timer = QTimer()
        timer.setInterval(10)
        timer.timeout.connect(lambda: ticks.append(time.monotonic()))
        timer.start()
        click(page.run_btn)
        self.assertFalse(page.stack.isEnabled())
        self.assertFalse(page.submit_btn.isEnabled())
        self.assertTrue(page.busy_bar.isVisible())
        self.idle()
        timer.stop()
        self.assertIn("시간 초과", page.code_panel.console.toPlainText())
        self.assertGreater(len(ticks), 100)
        self.assertLess(max(b - a for a, b in zip(ticks, ticks[1:])), 0.5)
        self.assertTrue(page.stack.isEnabled())

        # 문법 오류는 줄 번호와 함께
        editor.setPlainText("def broken(:\n")
        click(page.run_btn)
        self.idle()
        self.assertIn("문법 오류", page.code_panel.console.toPlainText())

        # 시작 코드로 되돌리기
        click(page.code_panel.reset_btn)
        self.choose("reset")
        self.assertEqual(editor.toPlainText(), code["starter"])
        self.assertEqual(study.read_text(path), code["starter"])
        self.assertFalse(code["answered"])

        # 빈칸 채우기: 안내가 나오고, 빈칸을 안 채우고 실행하면 이유를 알려 줌
        self.select(lambda it: it is fill)
        self.assertIn("빈칸(____)만", page.code_panel.hint.text())
        click(page.run_btn)
        self.idle()
        self.assertIn("빈칸", page.code_panel.console.toPlainText())
        self.assertEqual(self.attempts(), [])  # 실행은 기록하지 않음

    def test_paste_is_blocked_in_every_answer_box(self):
        self.boot()
        self.make_round("r93", [self.first(type="short"), self.first(type="output"), self.first(type="return")])
        self.win.open_round("r93")
        page, clip = self.win.round_page, QGuiApplication.clipboard()
        boxes = {"short": page.text_panel.single, "output": page.text_panel.multi, "return": page.code_panel.editor, "": page.choice_panel.entry}
        for kind, box in boxes.items():
            if kind:
                self.select(lambda it: it["type"] == kind)
                self.fill(page.current, "")
            else:  # 번호 입력칸은 보기 수를 세지 못한 객관식에서만 보여서 화면 밖에 둔 채로 확인함
                box.blockSignals(True)
            read = box.toPlainText if hasattr(box, "toPlainText") else box.text
            target = box.viewport() if hasattr(box, "viewport") else box  # 마우스 이벤트를 받는 위젯
            tries = {"Ctrl+V": lambda: QTest.keyClick(box, Qt.Key.Key_V, CTRL),
                     "Shift+Insert": lambda: QTest.keyClick(box, Qt.Key.Key_Insert, SHIFT),
                     "가운데 버튼": lambda: QTest.mouseClick(target, Qt.MouseButton.MiddleButton),
                     "끌어다 놓기": lambda: self.assertFalse(self.drop(target, "끌어온 글"))}
            clip.setText("붙여넣을 글")
            for name, attempt in tries.items():
                page.paste_note.hide()
                attempt()
                self.assertEqual(read(), "", "%s %s" % (kind, name))
                self.assertTrue(page.paste_note.isVisible(), "%s %s" % (kind, name))
            QApplication.sendEvent(target, QContextMenuEvent(QContextMenuEvent.Reason.Mouse, QPoint(5, 5), target.mapToGlobal(QPoint(5, 5))))
            self.assertIsNone(QApplication.activePopupWidget(), kind)  # 우클릭 메뉴는 뜨지 않음
            QTest.keyClicks(box, "abc")  # 복사와 잘라내기도 막고, 실행 취소는 그대로 둠
            QTest.keyClick(box, Qt.Key.Key_A, CTRL)
            for key in (Qt.Key.Key_C, Qt.Key.Key_X):
                QTest.keyClick(box, key, CTRL)
            self.assertEqual((read(), clip.text()), ("abc", "붙여넣을 글"), kind)
            QTest.keyClick(box, Qt.Key.Key_Z, CTRL)
            self.assertLess(len(read()), 3, kind)

        # 글자를 친 직후에 붙여넣어도 안내가 자동 저장 문구에 덮이지 않고, 조금 뒤에 스스로 사라짐
        self.select(lambda it: it["type"] == "short")
        page.paste_note.hide()
        QTest.keyClicks(page.text_panel.single, "ab")
        QTest.keyClick(page.text_panel.single, Qt.Key.Key_V, CTRL)
        pump(save_delay())
        self.assertIn("자동 저장했습니다", page.status.text())
        self.assertEqual((page.paste_note.isVisible(), page.paste_note.text()), (True, PASTE_NOTE))
        page.note_timer.setInterval(20)
        QTest.keyClick(page.text_panel.single, Qt.Key.Key_V, CTRL)
        pump(120)
        self.assertFalse(page.paste_note.isVisible())

    def drop(self, target, text):
        """글을 끌어다 놓는 이벤트를 보내고, 받아들였으면 True 를 돌려줌."""
        data = QMimeData()
        data.setText(text)
        events = (QDragEnterEvent(QPoint(5, 5), Qt.DropAction.CopyAction, data, LEFT, Qt.KeyboardModifier.NoModifier),
                  QDropEvent(QPointF(5, 5), Qt.DropAction.CopyAction, data, LEFT, Qt.KeyboardModifier.NoModifier))
        for event in events:
            QApplication.sendEvent(target, event)
        return any(event.isAccepted() for event in events)

    def test_result_page_says_why_a_code_item_is_wrong(self):
        self.boot()
        self.make_round("r91", [self.first(type="return")])
        self.win.open_round("r91")
        result = self.win.result_page
        self.fill(self.select(lambda it: it["kind"] == "code"), "print('오답')\n")
        self.submit_round()
        self.assertIs(self.page(), result)
        result.listw.setCurrentRow(1)
        self.assertIn("틀린 이유", result.detail.toPlainText())
        self.win.show_result("r91")  # 지난 회차를 다시 열면 채점 결과가 없어 다시 채점을 안내함
        result.listw.setCurrentRow(1)
        self.assertIn("다시 채점", result.detail.toPlainText())

    def test_number_written_by_hand_in_the_answer_sheet_opens_in_the_text_box(self):
        """터미널 방식으로 따옴표 없이 적은 숫자 답(Q14 = 3)이 든 답안지를 열어도 입력칸과 저장할 문항이 어긋나지 않음."""
        self.boot()
        self.make_round("r92", [self.first(type="return"), self.first(type="short")])
        path = os.path.join(self.win.session.folder("r92"), "quiz.py")
        name = adaptive.fname_of(self.first(type="short"))
        study.write_text(path, study.read_text(path).replace("%s = None" % name, "%s = 3" % name))
        self.win.open_round("r92")
        page = self.win.round_page
        item = self.select(lambda it: it["type"] == "short")
        self.assertIs(page.stack.currentWidget(), page.text_panel)
        self.assertEqual(page.text_panel.single.text(), "3")
        self.fill(item, "4")
        click(page.home_btn)
        self.assertEqual(self.saved_quiz("r92")[name], "4")

    def test_every_bank_item_shows_without_errors(self):
        self.boot()
        sess = self.win.session
        keys = sorted(sess.cat, key=study.natural_key)
        self.make_round("r99", keys, completed=True)
        self.win.open_round("r99")
        page = self.win.round_page
        self.assertEqual(page.listw.count(), len(keys))
        for row in range(page.listw.count()):
            page.listw.setCurrentRow(row)
            item = page.current
            self.assertEqual(item["key"], keys[row])
            self.assertTrue(page.body.toPlainText().strip(), item["id"])
            if item["type"] == "choice":
                cards = page.choice_panel.buttons
                self.assertEqual((len(cards), len(item["options"])), (item["choices"], item["choices"]), item["id"])
                self.assertTrue(all(card.doc.toPlainText().strip() for card in cards), item["id"])
                self.assertFalse(page.choice_panel.entry.isVisible())
            if item["kind"] == "code":
                self.assertEqual(page.code_panel.editor.toPlainText(), item["starter"])
                self.assertNotIn("\t", item["starter"])
        self.assertEqual(page.dirty, {})  # 보기만 해서는 아무것도 저장하지 않음
        self.win.show_result("r99")
        result = self.win.result_page
        for row in range(1, result.listw.count()):
            result.listw.setCurrentRow(row)
            result.reveal()
            text = result.detail.toPlainText()
            self.assertIn("해설", text, keys[row - 1])
            self.assertIn("모범 답안" if result.selected()["kind"] == "code" else "정답", text, keys[row - 1])


class ChoiceCardTest(GuiTest):
    def open_choices(self):
        """글 보기 · 코드 보기(번호 목록) · 복수 정답 · `**N번**` 문단으로 적은 보기 · 단답 순서의 회차를 띄움."""
        self.boot()
        keys = [self.first(type="choice", multi=False), "s04/Q5", self.first(type="choice", multi=True), "s04/Q20", self.first(type="short")]
        self.make_round("r95", keys)
        self.win.open_round("r95")
        self.win.activateWindow()
        return self.win.round_page

    def test_body_keeps_the_question_and_cards_take_the_options(self):
        page = self.open_choices()
        plain, code, _, labeled, _ = page.view["items"]
        cards = page.choice_panel.buttons
        self.assertEqual(len(cards), plain["choices"])
        self.assertTrue(page.body.toPlainText().strip())
        self.assertNotIn("<ol", page.body.toHtml())
        self.select(lambda it: it is code)
        cards = page.choice_panel.buttons
        self.assertEqual(len(cards), 4)
        self.assertIn("t.insert(0, 'X')", cards[3].doc.toPlainText())
        self.assertIn("출력되는 것은", page.body.toPlainText())
        self.assertNotIn("t.insert", page.body.toPlainText())
        self.assertGreater(cards[3].height(), cards[0].height())  # 코드가 세 줄인 보기가 두 줄인 보기보다 큼
        self.select(lambda it: it is labeled)
        cards = page.choice_panel.buttons
        self.assertEqual(len(cards), 5)
        self.assertIn("a[len(a)] = 4", cards[1].doc.toPlainText())
        self.assertIn("모두 고르세요", page.body.toPlainText())
        self.assertNotRegex(page.body.toPlainText() + "".join(card.doc.toPlainText() for card in cards), r"\d번")
        self.assertEqual(page.dirty, {})

    def test_cards_follow_mouse_and_keyboard_and_save_what_they_show(self):
        page = self.open_choices()
        single, _, multi, _, short = page.view["items"]
        cards = page.choice_panel.buttons

        # 카드 어디를 눌러도 골라지고, 단일 정답은 하나만 남고 다시 누르면 풀림
        QTest.mouseClick(cards[1], LEFT, pos=QPoint(cards[1].width() - 5, cards[1].height() - 5))
        self.assertEqual([card.isChecked() for card in cards[:3]], [False, True, False])
        click(cards[3])
        self.assertEqual((single["answer"], [card.isChecked() for card in cards].count(True)), ([4], 1))
        click(cards[3])
        self.assertEqual(single["answer"], [])

        # 숫자 키는 포커스가 문항 목록이나 다른 버튼에 있어도 듣고, 없는 번호는 넘김
        page.listw.setFocus()
        QTest.keyClick(page.listw, Qt.Key.Key_3)
        self.assertEqual((single["answer"], page.listw.currentRow()), ([3], single["no"] - 1))
        QTest.keyClick(page.next_btn, Qt.Key.Key_9)
        self.assertEqual(single["answer"], [3])
        pump(save_delay())
        self.assertEqual(self.saved_quiz("r95")[single["id"]], 3)

        # 위·아래 키로 옮기고 Space 로 고름. 끝에서는 더 가지 않음
        cards[0].setFocus(Qt.FocusReason.TabFocusReason)
        QTest.keyClick(cards[0], Qt.Key.Key_Down)
        self.assertIs(QApplication.focusWidget(), cards[1])
        self.assertTrue(cards[1].ring)
        QTest.keyClick(cards[1], Qt.Key.Key_Space)
        self.assertEqual(single["answer"], [2])
        QTest.keyClick(cards[1], Qt.Key.Key_Up)
        QTest.keyClick(cards[0], Qt.Key.Key_Up)
        self.assertIs(QApplication.focusWidget(), cards[0])

        # 복수 정답은 여러 개가 남고, 다시 누른 것만 풀림
        self.select(lambda it: it is multi)
        self.assertEqual(self.saved_quiz("r95")[single["id"]], 2)  # 문항을 옮기면 바로 저장됨
        cards = page.choice_panel.buttons
        QTest.keyClick(page.listw, Qt.Key.Key_3)
        QTest.keyClick(page.listw, Qt.Key.Key_1)
        click(cards[1])
        click(cards[1])
        self.assertEqual((multi["answer"], [card.isChecked() for card in cards[:3]]), ([1, 3], [True, False, True]))

        # 잠겨 있을 때와 다른 유형의 문항에서는 숫자 키가 답을 바꾸지 않음
        page.set_busy(True, "채점하는 중입니다.")
        QTest.keyClick(self.win, Qt.Key.Key_2)
        page.set_busy(False)
        self.assertEqual(multi["answer"], [1, 3])
        self.select(lambda it: it is short)
        QTest.keyClicks(page.text_panel.single, "12")
        QTest.keyClick(page.listw, Qt.Key.Key_2)
        self.assertEqual((page.text_panel.single.text(), multi["answer"]), ("12", [1, 3]))
        self.assertEqual(self.saved_quiz("r95")[multi["id"]], [1, 3])

        # 제출한 뒤 다시 풀기로 열어도 고른 보기가 그대로 보이고, 결과 화면에는 보기까지 든 문제 전체가 나옴
        self.submit_round()
        result = self.win.result_page
        result.listw.setCurrentRow(single["no"])
        self.assertIn(cards_text(self.win.session, single)[1], result.detail.toPlainText())
        self.assertIn("2번", result.detail.toPlainText())
        self.win.open_round("r95", review=True, select=single["id"])
        cards = page.choice_panel.buttons
        self.assertEqual([card.isChecked() for card in cards[:3]], [False, True, False])
        click(cards[0])
        click(page.home_btn)
        self.assertEqual(self.saved_quiz("r95")[single["id"]], 1)

    def test_double_click_and_held_keys_pick_only_once(self):
        """버튼을 두 번 누른 것이 같은 자리의 카드로 들어와 답이 바뀌지 않고, 카드를 더블클릭하거나 키를 누르고 있어도 한 번만 고름."""
        self.boot()
        win, page = self.win, self.win.round_page
        button = win.home.action_btn
        QTest.mouseDClick(win.windowHandle(), LEFT, pos=button.mapTo(win, button.rect().center()))
        pump()
        self.assertIs(self.page(), page)
        self.assertTrue(all(it["answer"] is None for it in page.view["items"] if it["type"] == "choice"))
        single = self.select(lambda it: it["type"] == "choice" and not it["multi"])
        cards = page.choice_panel.buttons
        QTest.mouseDClick(cards[0], LEFT)  # 더블클릭의 뒷부분(더블클릭 · 뗌)만 이 카드로 들어온 경우
        QTest.mouseRelease(cards[0], LEFT)
        self.assertEqual((single["answer"], cards[0].isChecked()), (None, False))
        click(cards[1])  # 카드를 더블클릭하면 누름 · 뗌 · 더블클릭 · 뗌 순서로 들어옴
        QTest.mouseDClick(cards[1], LEFT)
        QTest.mouseRelease(cards[1], LEFT)
        self.assertEqual((single["answer"], cards[1].isChecked()), ([2], True))  # 골랐다가 바로 풀리지 않음

        self.assertFalse(any(key.autoRepeat() for key in page.choice_panel.keys))
        cards[2].setFocus(Qt.FocusReason.TabFocusReason)
        QTest.keyClick(cards[2], Qt.Key.Key_Space)
        for _ in range(3):  # 누르고 있을 때 운영체제가 되풀이해 보내는 키
            QApplication.sendEvent(cards[2], QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Space, Qt.KeyboardModifier.NoModifier, " ", True))
        self.assertEqual(single["answer"], [3])
        click(page.home_btn)
        self.assertEqual(self.saved_quiz("d1")[single["id"]], 3)

    def test_hand_written_value_that_matches_no_card_is_pointed_out(self):
        """답안지에 손으로 적은 값이 카드와 맞지 않으면(따옴표로 감싼 번호, 없는 번호) 고른 카드가 없는 까닭을 알리고, 다시 고르면 안내가 사라짐."""
        self.boot()
        keys = [self.first(type="choice", multi=False), "s04/Q5", "s04/Q20"]
        self.make_round("r96", keys)
        path = os.path.join(self.win.session.folder("r96"), "quiz.py")
        text = study.read_text(path)
        for key, value in zip(keys, ('"2"', "9", "[2, 9]")):
            text = text.replace("%s = None" % adaptive.fname_of(key), "%s = %s" % (adaptive.fname_of(key), value))
        study.write_text(path, text)
        self.win.open_round("r96")
        page, panel = self.win.round_page, self.win.round_page.choice_panel
        for row, (stray, checked) in enumerate((("'2'", []), ("9", []), ("9", [2]))):
            page.listw.setCurrentRow(row)
            self.assertTrue(panel.stray.isVisible(), row)
            self.assertIn("(%s)" % stray, panel.stray.text())
            self.assertEqual([number for number, card in enumerate(panel.buttons, 1) if card.isChecked()], checked)
        click(panel.buttons[0])
        self.assertFalse(panel.stray.isVisible())
        click(page.home_btn)
        self.assertEqual(self.saved_quiz("r96")[adaptive.fname_of("s04/Q20")], [1, 2])
        self.win.open_round("r96", select=adaptive.fname_of("s04/Q20"))  # 카드와 맞는 값만 남으면 안내가 없음
        self.assertEqual((panel.stray.isVisible(), [card.isChecked() for card in panel.buttons[:3]]), (False, [True, True, False]))

    def test_question_that_cannot_be_split_keeps_the_whole_body_and_number_cards(self):
        with mock.patch.object(session, "split_choices", return_value=([], [])):
            page = self.open_choices()
        code = self.select(lambda it: it["key"] == "s04/Q5")
        cards = page.choice_panel.buttons
        self.assertEqual([card.doc.toPlainText() for card in cards], ["1번", "2번", "3번", "4번"])
        self.assertIn("t.insert(0, 'X')", page.body.toPlainText())
        click(cards[3])
        click(page.home_btn)
        self.assertEqual(self.saved_quiz("r95")[code["id"]], 4)


def cards_text(sess, item):
    """문항의 보기를 은행의 본문에서 읽어 글자로 돌려줌."""
    body = adaptive.quiz_section(sess.cat[item["key"]]["set"], sess.cat[item["key"]]["q"]["id"])
    return [mdlite.inline_plain(option[0]["text"]) for option in session.split_choices(body)[1]]


class TeamTest(GuiTest):
    def add_member(self, user, correct):
        """풀이 기록을 만듦. 진단에서 앞의 correct 문항만 맞히고 제출함."""
        sess = session.Session(user)
        sess.ensure_round()
        for view in sess.open_round("d1")["items"][:correct]:
            sess.set_answer("d1", view["id"], right_answer(sess, view))
        sess.grade("d1", finalize=True)

    def test_team_page_shows_a_card_per_member_in_readiness_order(self):
        for user, correct in (("tester", 16), ("alpha-kim", 30), ("beta_lee", 3)):
            self.add_member(user, correct)
        study.write_text(adaptive.profile_path("broken"), '{"rounds": [<<<<<<<')  # 읽을 수 없는 기록은 건너뜀
        self.boot()
        win, team = self.win, self.win.team_page
        click(win.home.team_btn)
        self.assertIs(self.page(), team)
        rows = win.session.team()
        self.assertEqual([row["user"] for row in rows], ["alpha-kim", "tester", "beta_lee"])
        self.assertEqual([card.user.text() for card in team.cards], [row["user"] for row in rows])
        self.assertEqual([hasattr(card, "me") for card in team.cards], [False, True, False])
        self.assertEqual([avatar.text for avatar in team.findChildren(Avatar)], ["AK", "TE", "BL"])
        self.assertEqual(len({avatar.back.name() for avatar in team.findChildren(Avatar)}), 3)
        self.assertIsNone(team.empty)
        for card, row in zip(team.cards, rows):
            self.assertEqual((card.ready.text(), card.bar.value()), ("%d%%" % row["readiness"], row["readiness"]))
            self.assertEqual(card.mastered.text(), "숙달한 단원 %d / %d" % (row["mastered"], len(adaptive.units())))
            self.assertEqual(card.facts.text(), "회차 %d · 정답률 %d%% · 마지막 풀이 %s" % (row["rounds"], round(row["accuracy"] * 100), row["last"]))
            self.assertEqual(card.strip.cells.count(), len(adaptive.units()))
            self.assertIn("정답률", card.strip.cells.itemAt(0).widget().toolTip())
            titles = {unit["unit"]: unit["title"] for unit in row["units"]}  # 단원은 이름으로 보여 줌
            self.assertEqual(card.weak.text(), "약한 단원: " + (", ".join(titles[unit] for unit in row["weak"]) or "-"))
            self.assertEqual(card.strong.text(), "능숙한 단원: " + (", ".join(titles[unit] for unit in row["strong"]) or "-"))
        self.assertEqual(len(rows[2]["weak"]), 3)
        self.assertEqual(team.cards[1].ready.text(), win.home.ready.text())
        click(team.home_btn)
        self.assertIs(self.page(), win.home)

    def test_long_id_is_cut_short_and_both_columns_stay_the_same_width(self):
        long = "a" * 20 + "-" + "b" * 18  # 깃허브 ID 의 최대 길이(39자)
        for user, correct in ((long, 30), ("tester", 16)):
            self.add_member(user, correct)
        self.win.resize(1024, 700)
        self.boot()
        click(self.win.home.team_btn)
        first, second = self.win.team_page.cards
        self.assertEqual(first.width(), second.width())
        self.assertTrue(first.user.text().endswith("…") and len(first.user.text()) < len(long), first.user.text())
        self.assertEqual((first.user.full, first.user.toolTip()), (long, long))  # 전체 ID 는 툴팁으로
        self.assertEqual((second.user.text(), second.user.toolTip()), ("tester", ""))

    def test_team_page_explains_when_nobody_else_has_a_record(self):
        self.boot()
        win, team = self.win, self.win.team_page
        click(win.home.team_btn)
        self.assertEqual(team.cards, [])
        self.assertIn("다른 사람의 풀이가 없습니다", team.empty.title.text())
        self.assertIn("진단 테스트를 시작하면", team.empty.text.text())
        self.assertIsNotNone(team.empty.findChild(Mascot))
        click(team.home_btn)
        click(win.home.action_btn)  # 진단을 시작하면 내 카드가 생김
        click(win.round_page.home_btn)
        click(win.home.team_btn)
        self.assertEqual([hasattr(card, "me") for card in team.cards], [True])
        self.assertEqual(team.cards[0].facts.text(), "회차 1 · 정답률 - · 마지막 풀이 -")
        self.assertNotIn("진단 테스트를 시작하면", team.empty.text.text())
        self.add_member("other", 5)
        click(team.home_btn)
        click(win.home.team_btn)
        self.assertEqual((len(team.cards), team.empty), (2, None))
        self.assertEqual((len(team.findChildren(MemberCard)), team.findChildren(EmptyCard)), (2, []))  # 앞서 놓았던 카드는 남지 않음


class WidgetTest(unittest.TestCase):
    def test_choice_falls_back_to_a_number_box_when_options_cannot_be_counted(self):
        panel, seen = ChoicePanel(), []
        panel.changed.connect(seen.append)
        panel.set_item({"choices": 0, "multi": False, "answer": [3, 1]})
        self.assertEqual(panel.buttons, [])
        self.assertFalse(panel.entry.isHidden())
        self.assertEqual(panel.entry.text(), "3, 1")
        panel.entry.clear()
        QTest.keyClicks(panel.entry, "2, 4")
        self.assertEqual(seen[-1], [2, 4])
        panel.set_item({"choices": 4, "multi": False, "answer": 2})  # 보기 수만 아는 문항은 번호만 든 카드
        self.assertTrue(panel.entry.isHidden())
        self.assertEqual([b.isChecked() for b in panel.buttons], [False, True, False, False])
        self.assertEqual([b.doc.toPlainText() for b in panel.buttons], ["1번", "2번", "3번", "4번"])
        click(panel.buttons[3])
        self.assertEqual(seen[-1], [4])

    def test_choice_card_is_as_tall_as_its_content_and_wraps_long_code(self):
        short = ChoiceCard(1, mdlite.to_html("`a`"), theme.doc_css(), False)
        code = ChoiceCard(2, mdlite.to_html("```python\n%s\n```" % "\n".join("x%d = %d" % (n, n) for n in range(6))), theme.doc_css(), False)
        long = ChoiceCard(3, mdlite.to_html("```python\nprint(%s)\n```" % ", ".join("'값 %d'" % n for n in range(40))), theme.doc_css(), True)
        for card in (short, code, long):
            card.resize(440, card.height())
            card.arrange()
            self.assertGreaterEqual(card.height(), card.top + content_height(card.doc) + card.PAD - 1)
            self.assertLessEqual(card.height(), card.top + content_height(card.doc) + 2 * card.PAD + card.BADGE)
        self.assertEqual(short.height(), short.BADGE + 2 * short.PAD)  # 한 줄짜리는 번호 배지 높이에 맞춤
        self.assertEqual((content_height(short.doc), content_height(code.doc)), (short.doc.size().height(), code.doc.size().height() - 10))  # 코드 상자 아래 여백은 뺌
        self.assertGreater(code.height(), 4 * short.height() // 2)
        narrow = long.height()
        long.resize(1600, narrow)
        long.arrange()
        self.assertGreater(narrow, long.height())  # 좁으면 긴 코드 줄을 잘라 내지 않고 줄바꿈함

    def test_corner_between_two_scroll_bars_is_not_drawn_as_a_box(self):
        edit = CodeEditor()
        edit.setPlainText("\n".join("x" * 200 for _ in range(60)))
        edit.resize(260, 180)
        edit.show()
        self.addCleanup(edit.close)
        pump()
        across, down = edit.horizontalScrollBar(), edit.verticalScrollBar()
        self.assertTrue(across.isVisible() and down.isVisible())
        left, top = down.mapTo(edit, QPoint(0, 0)).x(), across.mapTo(edit, QPoint(0, 0)).y()
        image = edit.grab().toImage()
        colors = {image.pixelColor(left + x, top + y).name() for x in range(8) for y in range(8)}  # 바깥쪽은 입력칸의 둥근 테두리와 겹침
        self.assertEqual(colors, {theme.color("surface")})

    def test_standard_menu_of_an_answer_box_is_in_korean(self):
        translator = app.korean(APP)
        self.addCleanup(APP.removeTranslator, translator)
        if translator.isEmpty():
            self.skipTest("이 PyQt6 에는 한글 번역 파일이 없습니다")
        editor = CodeEditor()
        menu = editor.createStandardContextMenu()
        self.assertTrue(any("복사" in action.text() for action in menu.actions()), [action.text() for action in menu.actions()])

    def test_mascot_changes_face_and_blinks_only_while_shown(self):
        bot = Mascot(96)
        plain = bot.grab().toImage()
        bot.set_happy(True)
        self.assertNotEqual(bot.grab().toImage(), plain)
        bot.set_happy(False)
        self.assertEqual(bot.grab().toImage(), plain)
        bot.open = 0.0
        self.assertNotEqual(bot.grab().toImage(), plain)  # 감은 눈
        self.assertFalse(bot.timer.isActive())
        bot.show()
        self.assertTrue(bot.timer.isActive() and bot.timer.interval() >= 2000)
        bot.hide()
        self.assertFalse(bot.timer.isActive())


class EditorTest(unittest.TestCase):
    def setUp(self):
        self.ed = CodeEditor()
        self.ed.setFont(theme.code_font())

    def keys(self, *steps):
        for step in steps:
            if isinstance(step, str):
                QTest.keyClicks(self.ed, step)
            else:
                QTest.keyClick(self.ed, *(step if isinstance(step, tuple) else (step,)))
        return self.ed.toPlainText()

    def test_tab_inserts_spaces_up_to_the_next_stop(self):
        self.assertEqual(self.keys(Qt.Key.Key_Tab, "x", Qt.Key.Key_Tab, "# t"), "    x   # t")
        self.assertNotIn("\t", self.ed.toPlainText())

    def test_enter_keeps_indent_and_adds_a_level_after_colon(self):
        typed = self.keys("def f(x):", Qt.Key.Key_Return, "if x:  ", Qt.Key.Key_Return, "return 1", Qt.Key.Key_Return, "y = 2")
        self.assertEqual(typed, "def f(x):\n    if x:  \n        return 1\n        y = 2")

    def test_backspace_in_indent_removes_one_level(self):
        typed = self.keys("if x:", Qt.Key.Key_Return, "if y:", Qt.Key.Key_Return, Qt.Key.Key_Backspace, "a", Qt.Key.Key_Return,
                          "  ", Qt.Key.Key_Backspace, "b", Qt.Key.Key_Backspace, "c", Qt.Key.Key_Return, Qt.Key.Key_Backspace, "d")
        self.assertEqual(typed, "if x:\n    if y:\n    a\n    c\nd")

    def test_shift_tab_outdents_and_tab_indents_selected_lines(self):
        self.ed.setPlainText("a\n    b\n      c")
        cursor = self.ed.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.ed.setTextCursor(cursor)
        self.assertEqual(self.keys(Qt.Key.Key_Backtab), "a\n    b\n  c")
        self.assertEqual(self.keys((Qt.Key.Key_Tab, SHIFT)), "a\n    b\nc")
        self.ed.selectAll()
        self.assertEqual(self.keys(Qt.Key.Key_Tab), "    a\n        b\n    c")
        self.assertEqual(self.keys(Qt.Key.Key_Backtab), "a\n    b\nc")

    def test_paste_is_blocked(self):
        data = QMimeData()
        data.setText("if x:\r\n\treturn 1")
        self.assertFalse(self.ed.canInsertFromMimeData(data))
        self.ed.insertFromMimeData(data)
        QGuiApplication.clipboard().setText("붙여넣을 글")
        self.ed.paste()
        self.assertEqual(self.ed.toPlainText(), "")

    def test_fixed_pitch_font_and_no_completer(self):
        self.assertTrue(self.ed.font().fixedPitch())
        self.assertFalse(hasattr(self.ed, "completer"))
        self.ed.setReadOnly(True)
        self.assertEqual(self.keys(Qt.Key.Key_Tab, Qt.Key.Key_Return), "")  # 잠겨 있을 때는 키로도 바뀌지 않음


class ThemeTest(GuiTest):
    def setUp(self):
        self.system = "light"  # 운영체제 설정을 흉내 냄
        patch = mock.patch.object(theme, "system_scheme", lambda: self.system)
        patch.start()
        self.addCleanup(patch.stop)
        super().setUp()

    def test_text_is_readable_and_unit_colors_differ_in_both_themes(self):
        self.assertEqual(set(theme.LIGHT), set(theme.DARK))
        pairs = [("ink", "bg"), ("ink", "surface"), ("ink", "surface_alt"), ("ink", "hover"), ("heading", "bg"), ("heading", "surface"),
                 ("muted", "bg"), ("muted", "surface"), ("primary_ink", "primary"), ("primary_ink", "primary_hover"),
                 ("selection_ink", "selection"), ("ink", "text_selection"), ("ink", "notice_bg"), ("link", "notice_bg"), ("ink", "code_bg"),
                 ("ink", "codebox_bg"), ("ink", "table_head"), ("doc_heading", "surface"), ("link", "surface"), ("link", "bg"),
                 ("ink", "selection"), ("muted", "surface_alt"),  # 고른 보기 카드의 글, 번호 배지의 숫자
                 ("placeholder", "surface")]  # 입력칸의 예시와 실행 결과 칸의 안내
        pairs += [(name, "surface") for name in ("ok", "wrong", "blank", "up", "retry")]
        pairs += [("unit_%s_ink" % name, "unit_" + name) for name in theme.UNIT]
        for scheme, tokens in theme.TOKENS.items():
            for ink, back in pairs:
                self.assertGreaterEqual(contrast(tokens[ink], tokens[back]), 4.5, "%s: %s / %s" % (scheme, ink, back))
            groups = (["unit_" + name for name in theme.UNIT], ["ok", "wrong", "blank"], ["up", "ok", "muted", "retry"])
            for group in groups:  # 단원 상태색, 결과색, 판정색은 같은 묶음 안에서 서로 구분됨
                for one, other in itertools.combinations([QColor(tokens[name]) for name in group], 2):
                    gap = abs(one.red() - other.red()) + abs(one.green() - other.green()) + abs(one.blue() - other.blue())
                    self.assertGreater(gap, 90, "%s: %s / %s" % (scheme, one.name(), other.name()))
            for back in ("bg", "surface"):  # 미진단 칸은 바탕과 색이 비슷해 테두리로 구분함
                self.assertGreaterEqual(contrast(tokens["unit_none_edge"], tokens[back]), 3, "%s: unit_none_edge / %s" % (scheme, back))
        self.assertIn("QLabel#unit_none { border: 1px solid %s; }" % theme.color("unit_none_edge"), APP.styleSheet())
        for back in theme.AVATARS:  # 이니셜 원의 글자
            self.assertGreaterEqual(contrast(theme.BRAND[2], back), 4.5, back)

    def test_button_cycles_system_light_dark_and_the_choice_is_remembered(self):
        self.boot()
        home = self.win.home
        self.assertEqual((home.theme_btn.text(), theme.state["scheme"]), ("테마: 시스템", "light"))
        click(home.theme_btn)
        self.assertEqual((home.theme_btn.text(), theme.state["scheme"]), ("테마: 밝게", "light"))
        click(home.theme_btn)
        self.assertEqual((home.theme_btn.text(), theme.state["scheme"]), ("테마: 어둡게", "dark"))
        self.assertEqual(self.settings.value("theme"), "dark")
        self.assertIn(theme.DARK["bg"], APP.styleSheet())
        again = MainWindow(self.settings, lambda root, user: (self.git, ""))  # 다시 켜면 고른 테마로 열림
        self.assertEqual((again.home.theme_btn.text(), theme.state["scheme"]), ("테마: 어둡게", "dark"))
        again.deleteLater()
        click(home.theme_btn)
        self.assertEqual((home.theme_btn.text(), theme.state["scheme"]), ("테마: 시스템", "light"))
        self.assertIn(theme.LIGHT["bg"], APP.styleSheet())

    def test_system_mode_follows_the_os_setting(self):
        hints = APP.styleHints()
        if not hasattr(hints, "colorSchemeChanged"):
            self.skipTest("Qt 6.5 미만은 운영체제 설정이 바뀐 것을 알려 주지 않습니다")
        self.boot()
        self.system = "dark"
        hints.colorSchemeChanged.emit(Qt.ColorScheme.Dark)
        self.assertEqual((theme.state["mode"], theme.state["scheme"]), ("system", "dark"))
        self.assertIn(theme.DARK["ink"], self.win.round_page.body.document().defaultStyleSheet())
        click(self.win.home.theme_btn)  # 밝게로 정해 두면 따라가지 않음
        self.assertEqual(theme.state["scheme"], "light")
        hints.colorSchemeChanged.emit(Qt.ColorScheme.Dark)
        self.assertEqual((theme.state["mode"], theme.state["scheme"]), ("light", "light"))

    def test_result_buttons_stay_locked_when_restyled_while_a_job_runs(self):
        """제출이 도는 중에 글자 크기나 테마가 바뀌어 결과 화면을 다시 그려도, 잠근 [해설 보기]·[다시 풀기]는 켜지지 않음."""
        self.boot()
        win, result = self.win, self.win.result_page
        click(win.home.action_btn)
        self.submit_round()
        result.listw.setCurrentRow(1)
        buttons = (result.explain_btn, result.retry_btn)
        self.assertTrue(all(button.isEnabled() for button in buttons))
        self.git.delay = 0.5
        click(result.git_btn)
        self.assertIsNotNone(win.job)
        for change in (lambda: win.set_zoom(1), lambda: theme.set_mode("dark")):
            change()
            self.assertFalse(any(button.isEnabled() for button in buttons))
        self.idle()
        self.git.delay = 0
        self.choose("ok")
        self.assertTrue(all(button.isEnabled() for button in buttons))

    def test_dark_theme_reaches_open_screens_and_leaves_no_light_patches(self):
        self.boot()
        win, page, result = self.win, self.win.round_page, self.win.result_page
        self.make_round("r94", [self.first(type="choice", multi=False), self.first(type="output"), self.first(type="return")])
        win.open_round("r94")
        self.fill(self.select(lambda it: it["kind"] == "code"), "def solution(*args):\n    return None\n")
        click(page.run_btn)
        self.idle()
        self.assertGreater(bright_share(win), 0.5)  # 밝은 테마에서는 화면 대부분이 밝음
        cards = page.choice_panel.buttons  # 밝은 테마에서 만든 보기 카드
        self.assertIn(theme.LIGHT["ink"], cards[0].doc.defaultStyleSheet())
        page.body.setFixedHeight(120)  # 본문을 반쯤 내려 둠
        pump()
        bar = page.body.verticalScrollBar()
        bar.setValue(bar.maximum() // 2)
        place = bar.value()
        self.assertGreater(place, 0)
        theme.set_mode("dark")  # 화면을 띄워 둔 채로 바꿈
        pump()
        self.assertEqual(bar.value(), place)  # 읽던 자리는 남음
        page.body.setMaximumHeight(16777215)
        pump()
        for card in cards:  # 이미 만들어 둔 카드도 어두운 테마의 글자색으로 다시 칠함
            self.assertIn(theme.DARK["ink"], card.doc.defaultStyleSheet())
            self.assertNotIn(theme.LIGHT["ink"], card.doc.defaultStyleSheet())

        sheet = APP.styleSheet() + page.body.document().defaultStyleSheet()
        self.assertIn(theme.DARK["ink"], page.body.document().defaultStyleSheet())
        self.assertTrue(all(gray(value) <= 200 for value in backgrounds(sheet)), backgrounds(sheet))
        for name in ("bg", "surface", "surface_alt", "hover", "notice_bg", "code_bg", "codebox_bg", "table_head", "selection", "track"):
            self.assertNotIn(theme.LIGHT[name], sheet, name)

        def check(widget, *browsers):
            """밝은 조각이 없는지 봄. browsers 는 바탕색을 가진 조각(표 머리, 구역 띠, 코드 상자)이 든 본문."""
            self.assertEqual(bright_share(widget), 0, widget)
            for browser in browsers:
                shown = backgrounds(browser.document().toHtml())
                self.assertTrue(shown and all(gray(value) <= 200 for value in shown), shown)

        check(win, page.body, page.code_panel.console)  # 코드 문항: 본문의 표와 인라인 코드, 실행 결과 표
        editor = page.code_panel.editor.grab().toImage()
        self.assertEqual(editor.pixelColor(editor.width() // 2, editor.height() - 12).name(), theme.DARK["surface"])
        for kind in ("choice", "output"):
            self.select(lambda it: it["type"] == kind)
            check(win)
        self.submit_round()
        self.assertIs(self.page(), result)
        check(win)
        for row, item in enumerate(result.view["items"], 1):
            self.assertEqual(result.listw.item(row).foreground().color().name(), theme.DARK[theme.result_label(item["state"])[1]])
            result.listw.setCurrentRow(row)
            result.reveal()
            check(win, result.detail)  # 구역 띠, 코드 상자, 해설
        click(result.home_btn)
        check(win)
        click(win.home.team_btn)  # 팀 현황: 내 카드와 빈 자리 안내
        self.assertEqual((len(win.team_page.cards), win.team_page.empty is not None), (1, True))
        check(win)
        click(win.team_page.home_btn)
        big = win.home.foot.font()  # 획이 굵어야 가장자리가 섞이지 않은 링크 색 픽셀이 글꼴과 플랫폼에 상관없이 생김
        big.setPixelSize(40)
        win.home.foot.setFont(big)
        win.home.foot.resize(win.home.foot.sizeHint())
        foot = win.home.foot.grab().toImage()  # 링크 색은 글을 넣을 때 굳으므로 테마가 바뀌면 다시 넣어야 함
        colors = {foot.pixelColor(x, y).name() for x in range(foot.width()) for y in range(foot.height())}
        self.assertIn(theme.DARK["link"], colors)
        self.assertNotIn(theme.LIGHT["link"], colors)
        boxes = [win.ask("알림", "글", (("확인", "ok"), ("닫기", "")), detail="자세한 내용", link="https://example.com/pr"),
                 dialogs.IdDialog(win, lambda user: None), dialogs.ErrorDialog("오류 내용", None, errors.ISSUE_URL)]
        for box in boxes:
            box.show()
            pump()
            check(box)
            box.close()

        win.show_result("r94")
        result.listw.setCurrentRow(result.listw.count() - 1)
        result.reveal()
        result.detail.setFixedHeight(120)
        pump()
        bar = result.detail.verticalScrollBar()
        bar.setValue(bar.maximum() // 2)
        place = bar.value()
        self.assertGreater(place, 0)
        theme.set_mode("light")  # 되돌리면 밝은 색으로 돌아오고 읽던 자리는 남음
        pump()
        self.assertEqual(bar.value(), place)
        result.detail.setMaximumHeight(16777215)
        pump()
        self.assertGreater(bright_share(win), 0.5)
        self.assertIn(theme.LIGHT["ink"], result.detail.document().defaultStyleSheet())
        self.assertEqual(result.listw.item(1).foreground().color().name(), theme.LIGHT[theme.result_label(result.view["items"][0]["state"])[1]])


class IconTest(unittest.TestCase):
    def test_icon_draws_a_readable_r_at_every_size(self):
        for size in icon.SIZES:
            image = icon.pixmap(size).toImage()
            self.assertEqual((image.width(), image.height()), (size, size))
            self.assertEqual(image.pixelColor(0, 0).alpha(), 0, size)  # 둥근 모서리 밖은 비어 있음

            def at(x, y):
                return image.pixelColor(int(x * size / 100), int(y * size / 100))

            self.assertGreater(at(35, 50).lightness(), 240, size)  # 세로 기둥은 흰색
            self.assertLess(at(12, 88).lightness(), 200, size)  # 바탕은 그라데이션
            eye = at(icon.EYE[0], icon.EYE[1])
            if size >= 32:
                self.assertGreater(eye.lightness(), 240, size)  # 눈동자
            else:
                self.assertLess(eye.lightness(), 225, size)  # 작은 크기에서는 구멍을 비워 R 로 읽히게 함

    def test_install_sets_the_window_icon_and_survives_without_the_windows_api(self):
        with mock.patch.object(icon.sys, "platform", "win32"), mock.patch("ctypes.windll", None, create=True):
            icon.install(APP)
        self.assertEqual(sorted(size.width() for size in APP.windowIcon().availableSizes()), list(icon.SIZES))


class MotionTest(GuiTest):
    def setUp(self):
        super().setUp()
        motion.enabled = True
        self.addCleanup(setattr, motion, "enabled", False)

    def covers(self, widget):
        return widget.findChildren(motion.Cover)

    def test_page_change_fades_without_holding_up_input(self):
        self.assertTrue(150 <= motion.FADE_MS <= 200)
        self.boot()
        win, page = self.win, self.win.round_page
        wait_until(lambda: not self.covers(win), 5)
        QTest.mouseClick(win.home.action_btn, LEFT)
        self.assertIs(self.page(), page)  # 화면은 바로 바뀌고 앞 화면을 찍은 그림만 위에서 옅어짐
        self.assertEqual(len(self.covers(win.pages)), 1)
        self.assertIsNone(page.body.graphicsEffect())
        self.assertIsNone(page.code_panel.editor.graphicsEffect())
        self.assertIs(win.childAt(page.submit_btn.mapTo(win, page.submit_btn.rect().center())), page.submit_btn)  # 그림이 마우스를 가로채지 않음
        item = self.select(lambda it: it["type"] == "choice")
        click(page.choice_panel.buttons[0])
        self.assertEqual(item["answer"], [1])
        wait_until(lambda: not self.covers(win), 5)
        win.cycle_theme()  # 테마를 바꿀 때도 같은 방식으로 넘어감
        self.assertEqual(len(self.covers(win)), 1)
        wait_until(lambda: not self.covers(win), 5)

    def test_numbers_count_up_and_stop_at_the_final_value(self):
        self.assertTrue(500 <= motion.COUNT_MS <= 700)
        self.boot()
        label, seen = self.win.home.ready, []
        motion.count(label, 73, seen.append)
        wait_until(lambda: seen and seen[-1] == 73, 5)
        self.assertEqual(seen, sorted(seen))
        self.assertLess(seen[0], 73)
        motion.count_text(label, "%d%%", 45)
        self.assertGreaterEqual(label.minimumWidth(), label.fontMetrics().horizontalAdvance("45%"))  # 끝 글자의 폭을 미리 잡음
        early, late = [], []
        motion.count(self.win.home.ready_bar, 90, early.append)
        motion.count(self.win.home.ready_bar, 20, late.append)  # 다시 부르면 앞의 것은 멈춤
        wait_until(lambda: label.text() == "45%" and late and late[-1] == 20, 5)
        pump(motion.COUNT_MS)
        self.assertNotIn(90, early)

    def test_switched_off_everything_lands_on_the_final_state_at_once(self):
        self.boot()
        wait_until(lambda: not self.covers(self.win), 5)
        motion.enabled = False
        seen = []
        motion.count(self.win.home.ready, 73, seen.append)
        motion.count_text(self.win.home.ready, "%d%%", 88)
        click(self.win.home.action_btn)
        self.assertEqual((seen, self.win.home.ready.text(), self.covers(self.win)), ([73], "88%", []))

    def test_check_mark_blink_and_team_bars_end_the_same_with_or_without_motion(self):
        self.assertTrue(120 <= motion.CHECK_MS <= 150)
        self.assertLessEqual(motion.BLINK_MS, 400)
        self.boot()
        win, page = self.win, self.win.round_page
        bot, lids = win.home.findChild(Mascot), []
        with mock.patch.object(bot, "_lid", side_effect=lambda t, real=bot._lid: (lids.append(t), real(t))):
            bot.blink()
            wait_until(lambda: lids and lids[-1] == 1.0, 5)
        self.assertTrue(len(lids) > 2 and bot.open == 1.0)  # 감았다가 다시 뜬 눈으로 끝남
        click(win.home.action_btn)
        item = self.select(lambda it: it["type"] == "choice")
        cards = page.choice_panel.buttons
        QTest.mouseClick(cards[0], LEFT)
        self.assertEqual((item["answer"], cards[0].isChecked()), ([1], True))  # 답은 체크가 그려지기를 기다리지 않음
        self.assertLess(cards[0].tick, 1.0)
        wait_until(lambda: cards[0].tick == 1.0, 5)
        click(page.home_btn)
        click(win.home.team_btn)
        wait_until(lambda: not self.covers(win), 5)
        card = win.team_page.cards[0]
        wait_until(lambda: getattr(card.bar, "_motion", None) is None, 5)
        moving = card.bar.value()

        motion.enabled = False
        bot.blink()
        self.assertEqual(bot.open, 1.0)
        click(win.team_page.home_btn)
        click(win.home.team_btn)
        self.assertEqual(win.team_page.cards[0].bar.value(), moving)
        click(win.team_page.home_btn)
        click(win.home.action_btn)
        self.select(lambda it: it is not None and it["id"] == item["id"])
        cards = page.choice_panel.buttons
        self.assertEqual((cards[0].isChecked(), cards[0].tick), (True, 1.0))
        click(cards[1])
        self.assertEqual((cards[1].tick, [card.isChecked() for card in cards[:2]]), (1.0, [False, True]))

    def test_confetti_falls_after_a_good_round_lets_clicks_through_and_removes_itself(self):
        self.assertTrue(1200 <= motion.CONFETTI_MS <= 1800)
        self.boot()
        win, result = self.win, self.win.result_page
        click(win.home.action_btn)
        self.answer_round(skip={1})
        self.submit_round()
        self.assertIs(self.page(), result)
        papers = result.findChildren(motion.Confetti)
        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0].geometry(), result.rect())
        self.assertTrue(result.mascot.happy)
        earned = sum(it["points"] for it in result.view["items"][1:])
        wait_until(lambda: result.score.text().split(" / ")[0] == str(earned), 5)  # 점수는 색종이와 상관없이 끝 값까지 올라감
        wait_until(lambda: not self.covers(win), 5)
        self.assertEqual(len(result.findChildren(motion.Confetti)), 1)
        row = result.listw.visualItemRect(result.listw.item(2)).center()
        QTest.mouseClick(win.windowHandle(), LEFT, pos=result.listw.viewport().mapTo(win, row))  # 색종이 아래의 목록이 그대로 눌림
        self.assertEqual(result.listw.currentRow(), 2)
        self.assertIs(win.childAt(result.next_btn.mapTo(win, result.next_btn.rect().center())), result.next_btn)
        wait_until(lambda: not result.findChildren(motion.Confetti), 5)
        win.show_result("d1")  # 지난 회차를 다시 열 때는 떨어지지 않음
        self.assertEqual(result.findChildren(motion.Confetti), [])
        self.assertTrue(result.mascot.happy)
        motion.confetti(result)  # 떨어지는 동안 다른 결과를 열면 그 화면 위에 남지 않음
        win.show_result("d1")
        pump()
        self.assertEqual(result.findChildren(motion.Confetti), [])

    def test_no_confetti_for_a_poor_round_or_with_motion_off(self):
        self.boot()
        win, result = self.win, self.win.result_page
        click(win.home.action_btn)
        self.submit_round()  # 전부 미응답
        self.assertIs(self.page(), result)
        self.assertEqual((result.findChildren(motion.Confetti), result.mascot.happy), ([], False))
        motion.enabled = False
        click(result.next_btn)
        self.answer_round()
        self.submit_round()
        self.assertEqual((result.findChildren(motion.Confetti), result.mascot.happy), ([], True))


def save_delay():
    """자동 저장이 돌 만큼의 시간(ms)."""
    from gui.round_page import SAVE_DELAY_MS
    return SAVE_DELAY_MS + 250


if __name__ == "__main__":
    unittest.main()
