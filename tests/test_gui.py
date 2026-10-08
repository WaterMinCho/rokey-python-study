# -*- coding: utf-8 -*-
"""화면 테스트. 창을 화면에 내보내지 않고(offscreen) 위젯을 직접 눌러 처음 실행부터 다시 채점까지 돌려 봄.

실제 문제 은행을 쓰되 풀이 폴더는 임시 폴더로 돌리고, 제출 모듈은 가짜를 끼움. PyQt6 가 없으면 전부 건너뜀.
실행: python -m unittest discover -s tests
"""
import contextlib
import io
import os
import shutil
import sys
import tempfile
import time
import unittest
from unittest import mock

try:
    from PyQt6.QtCore import QEventLoop, QMimeData, QSettings, Qt, QTimer, qInstallMessageHandler
    from PyQt6.QtGui import QGuiApplication, QTextCursor
    from PyQt6.QtTest import QTest
    from PyQt6.QtWidgets import QApplication, QPushButton
except ImportError:
    raise unittest.SkipTest("PyQt6 가 설치돼 있지 않아 화면 테스트를 건너뜁니다")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import adaptive  # noqa: E402
import session  # noqa: E402
import study  # noqa: E402
from gui import errors, theme  # noqa: E402
from gui.widgets import ChoicePanel, CodeEditor  # noqa: E402
from gui.window import MainWindow  # noqa: E402

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
NOISE = ("propagateSizeHints", "Populating font family aliases")  # offscreen 플랫폼이 창을 띄울 때마다 찍는 안내
qInstallMessageHandler(lambda mode, context, text: None if any(n in text for n in NOISE) else print(text, file=sys.stderr))
APP = QApplication.instance() or QApplication(sys.argv[:1])
theme.apply(APP)
LEFT = Qt.MouseButton.LeftButton
SHIFT = Qt.KeyboardModifier.ShiftModifier


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
        self.assertIn("작성함", page.listw.item(choice["no"] - 1).text())
        click(buttons[1])
        self.assertFalse(any(b.isChecked() for b in buttons))
        self.assertIn("안 풂", page.listw.item(choice["no"] - 1).text())
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

    def test_font_size_is_adjustable_and_remembered(self):
        self.boot()
        page = self.win.round_page
        self.assertEqual(page.code_panel.editor.font().pixelSize(), theme.CODE_PX)
        self.assertTrue(page.code_panel.editor.font().fixedPitch())
        self.win.set_zoom(2)
        self.assertEqual(page.code_panel.editor.font().pixelSize(), theme.CODE_PX + 2)
        self.assertEqual(page.text_panel.multi.font().pixelSize(), theme.CODE_PX + 2)
        self.assertIn("font-size: 16px", page.body.document().defaultStyleSheet())
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
        self.assertTrue(start.retry.isVisible())
        os.remove(adaptive.profile_path("tester"))
        click(start.retry)
        self.assertIs(self.page(), self.win.home)


class BankTest(GuiTest):
    def first(self, **want):
        """조건에 맞는 은행의 첫 문항 키."""
        cat = self.win.session.cat
        multi = want.pop("multi", None)
        return next(key for key in sorted(cat, key=study.natural_key)
                    if all(cat[key][name] == value for name, value in want.items())
                    and (multi is None or (len(cat[key]["q"]["answer"]) > 1) == multi))

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
                self.assertEqual(len(page.choice_panel.buttons), item["choices"], item["id"])
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
        panel.set_item({"choices": 4, "multi": False, "answer": 2})
        self.assertTrue(panel.entry.isHidden())
        self.assertEqual([b.isChecked() for b in panel.buttons], [False, True, False, False])


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

    def test_paste_is_plain_text_with_tabs_as_spaces(self):
        data = QMimeData()
        data.setText("if x:\r\n\treturn 1")
        data.setHtml("<b>굵게</b>")
        self.ed.insertFromMimeData(data)
        self.assertEqual(self.ed.toPlainText(), "if x:\n    return 1")

    def test_fixed_pitch_font_and_no_completer(self):
        self.assertTrue(self.ed.font().fixedPitch())
        self.assertFalse(hasattr(self.ed, "completer"))
        self.ed.setReadOnly(True)
        self.assertEqual(self.keys(Qt.Key.Key_Tab, Qt.Key.Key_Return), "")  # 잠겨 있을 때는 키로도 바뀌지 않음


def save_delay():
    """자동 저장이 돌 만큼의 시간(ms)."""
    from gui.round_page import SAVE_DELAY_MS
    return SAVE_DELAY_MS + 250


if __name__ == "__main__":
    unittest.main()
