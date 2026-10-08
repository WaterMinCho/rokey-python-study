# -*- coding: utf-8 -*-
"""메인 창. 시작 순서(ID → 새 문제 받기 → 풀이 기록 열기), 화면 전환, 워커, 제출 흐름, 테마를 맡음."""
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices, QKeySequence, QShortcut
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QProgressBar, QPushButton, QStackedWidget, QVBoxLayout, QWidget

import session
import study
from gui import errors, motion, theme
from gui.dialogs import IdDialog, MessageDialog
from gui.guard import Guard
from gui.home_page import HomePage
from gui.result_page import ResultPage
from gui.round_page import RoundPage
from gui.team_page import TeamPage
from gui.worker import Job
from session import SessionError


def load_gitflow(root, user):
    """제출 모듈을 불러와 (GitFlow | None, 못 쓰는 이유)를 돌려줌. 모듈이 없거나 깨져도 풀이와 채점은 돼야 해서 예외를 삼킴."""
    try:
        import gitflow
        return gitflow.GitFlow(root, user), ""
    except Exception as error:
        return None, "제출 모듈(gitflow.py)을 불러오지 못했습니다: %s" % error


class StartPage(QWidget):
    """시작 화면. 새 문제를 확인하는 동안과 풀이 기록을 열지 못했을 때 보임."""

    def __init__(self, win):
        super().__init__()
        self.setObjectName("page")
        box = QVBoxLayout(self)
        box.setSpacing(14)
        title = QLabel("ROKEY 파이썬 스터디")
        title.setObjectName("h1")
        self.status = QLabel("")
        self.status.setObjectName("muted")
        self.busy_bar = QProgressBar()
        self.busy_bar.setRange(0, 0)
        self.busy_bar.setTextVisible(False)
        self.busy_bar.setFixedWidth(260)
        self.busy_bar.hide()
        self.error = QLabel("")
        self.error.setObjectName("error")
        self.error.setWordWrap(True)
        self.error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.retry = QPushButton("다시 시도")
        self.retry.hide()
        self.retry.clicked.connect(win.open_session)
        box.addStretch(2)
        for widget in (title, self.status, self.busy_bar):
            box.addWidget(widget, 0, Qt.AlignmentFlag.AlignHCenter)
        box.addWidget(self.error)  # 정렬 플래그를 주면 줄바꿈한 글이 제 높이를 받지 못해 잘림
        box.addWidget(self.retry, 0, Qt.AlignmentFlag.AlignHCenter)
        box.addStretch(3)

    def set_busy(self, busy, text=""):
        self.status.setText(text if busy else "")
        self.busy_bar.setVisible(busy)

    def show_error(self, text):
        self.error.setText(text)
        self.retry.setVisible(bool(text))


class MainWindow(QMainWindow):
    def __init__(self, settings, gitflow_factory=load_gitflow):
        super().__init__()
        self.setWindowTitle("ROKEY 파이썬 스터디")
        self.settings, self.gitflow_factory = settings, gitflow_factory
        self.user, self.session, self.gitflow, self.git_reason = None, None, None, ""
        self.job = None  # 도는 중인 워커 (Job, 잠근 화면, 끝났을 때, 실패했을 때)
        self.dialog = None  # 가장 최근에 띄운 대화상자
        self.notice = None  # 홈 위쪽에 한 줄로 보여 줄 제출 모듈의 결과
        self.restart, self.close_pending = False, False
        self.open_url = lambda url: QDesktopServices.openUrl(QUrl(url))
        self.zoom = settings.value("zoom", 0, type=int)
        theme.set_mode(settings.value("theme", "system", type=str))

        self.pages = QStackedWidget()
        self.start, self.home, self.round_page, self.result_page = StartPage(self), HomePage(self), RoundPage(self), ResultPage(self)
        self.team_page = TeamPage(self)
        for page in (self.start, self.home, self.round_page, self.result_page, self.team_page):
            self.pages.addWidget(page)
        self.setCentralWidget(self.pages)
        self.restyle()  # 스타일시트가 있으면 부모가 바뀔 때 위젯 글꼴이 초기화되므로 창에 붙인 뒤에 글꼴을 줌
        theme.signals.changed.connect(self.restyle)
        room = self.screen().availableGeometry()  # 작은 노트북 화면에서 아래쪽 버튼이 화면 밖으로 나가지 않게
        self.resize(min(1280, room.width() - 40), min(800, room.height() - 60))
        if settings.value("geometry"):
            self.restoreGeometry(settings.value("geometry"))
        for keys, step in ((QKeySequence.StandardKey.ZoomIn, 1), ("Ctrl+=", 1), (QKeySequence.StandardKey.ZoomOut, -1)):
            QShortcut(QKeySequence(keys), self, lambda step=step: self.set_zoom(self.zoom + step))
        QShortcut(QKeySequence("Ctrl+0"), self, lambda: self.set_zoom(0))
        self.guard = Guard(self)
        QApplication.instance().installEventFilter(self.guard)
        self.guard.blocked.connect(self.round_page.note_blocked)

    # 시작 순서

    def boot(self):
        user = session.saved_user()
        if user:
            self.sync_first(user)
            return
        self.dialog = IdDialog(self, self.sync_first)
        self.dialog.rejected.connect(self.close)  # ID 없이는 진행할 수 없음
        self.dialog.show()

    def sync_first(self, user):
        """새 컴퓨터에서 빈 기록이 먼저 생기지 않게, 풀이 기록을 열기 전에 새 문제부터 받음."""
        self.user = user
        self.gitflow, self.git_reason = self.gitflow_factory(study.ROOT, user)
        if self.gitflow is None:
            self.open_session()
            return
        self.run_job("새 문제 확인 중입니다.", self.gitflow.sync, self._synced_first, on_fail=self.open_session)

    def _synced_first(self, result):
        if result.get("restart"):
            self._restart(result)
            return
        diverged = result.get("status") == "diverged"
        if not diverged and (result.get("status") not in ("ok", "nothing") or result.get("changed") or result.get("backup")):
            self.notice = result  # 오프라인·git 없음 같은 결과는 홈에 한 줄로만 알리고 계속 진행함
        if self.open_session() and diverged:
            self._git_done("문제 받기", dict(result, changed=False))

    def open_session(self):
        """풀이 기록과 문제 은행을 새로 읽고 홈으로 감. 읽지 못하면 시작 화면에 이유를 보여 주고 False 를 돌려줌."""
        try:
            self.session = session.Session(self.user)
        except SessionError as error:
            self.start.show_error("%s\n파일을 고친 뒤 '다시 시도'를 눌러 주세요. 고치기 어려우면 스터디장에게 알려 주세요." % error)
            motion.switch(self.pages, self.start)
            return False
        self.start.show_error("")
        self.go_home()
        return True

    # 화면 전환

    def go_home(self):
        if not self.leave_round(self.go_home, "저장하지 않고 나가기"):
            return
        self.home.refresh()
        motion.switch(self.pages, self.home)

    def leave_round(self, then, leave):
        """회차 화면을 떠나기 전에 쓰던 답을 저장하고 True 를 돌려줌. 저장하지 못하면 알리고 False 를 돌려줌.
        leave 는 그 답을 버리고 떠나는 버튼의 글자. 그 버튼을 고르면 then() 을 부름."""
        page = self.round_page
        if page.flush(offer=False):
            return True

        def drop(_):
            page.dirty.clear()
            then()

        self.ask("저장하지 못한 답", "%s\n\n쓰던 답 %d개가 파일에 저장되지 않았습니다. [돌아가기]를 누르면 회차 화면으로 돌아가고 쓰던 답은 화면에 남습니다. "
                 "풀이 폴더의 파일을 다른 프로그램에서 열어 두었다면 닫고 다시 나가 보세요.\n"
                 "[%s]를 누르면 저장되지 않은 답은 지워집니다." % (page.status.text(), len(page.dirty), leave),
                 (("돌아가기", ""), (leave, "drop")), drop)
        return False

    def next_action(self, overview):
        """'지금 할 일' 버튼의 글자와 설명."""
        current = overview["current"]
        if not overview["rounds"]:
            return "진단 테스트 시작", "단원마다 몇 문항씩 풀어 출발 레벨을 정합니다. 모르는 문항은 비워 두고 제출하면 됩니다."
        if current is None:
            return "다음 회차 시작", "지난 회차를 모두 제출했습니다."
        name = "진단 테스트" if current["kind"] == "diag" else "%d회차" % int(current["id"][1:])
        try:
            pending = self.session.pending(current["id"])
            written = pending["total"] - len(pending["blank"])
        except SessionError:  # 답안지를 읽지 못한 경우. 회차를 열 때 복구를 제안함
            written = 1
        desc = "%s · %d문항" % (current["title"], current["size"])
        if written:
            desc += " · 작성한 문항 %d개" % written
        if current["size_reason"]:
            desc += "\n문항 수 기준: %s" % current["size_reason"]
        return "%s %s" % (name, "이어 풀기" if written else "시작"), desc

    def start_next(self):
        """풀던 회차가 있으면 그 회차를, 없으면 다음 회차(처음이면 진단)를 만들어 띄움."""
        try:
            rnd, _ = self.session.ensure_round()
        except SessionError as error:
            self.ask("알림", str(error))
            return
        if rnd is None:
            self.ask("알림", "전 단원을 심화까지 끝내 더 낼 문항이 없습니다.\n터미널에서 python study.py start m1 (2회는 m2)로 모의고사를 볼 수 있습니다.")
            return
        self.open_round(rnd["id"])

    def open_round(self, rid, review=False, select=None):
        try:
            self.round_page.load(rid, review, select)
        except SessionError as error:
            self._session_error(error, rid, lambda: self.open_round(rid, review, select))
            return
        motion.switch(self.pages, self.round_page)

    def show_result(self, rid, result=None):
        try:
            self.result_page.load(rid, result)
        except SessionError as error:
            self._session_error(error, rid, lambda: self.show_result(rid, result))
            return
        motion.switch(self.pages, self.result_page)

    def show_team(self):
        self.team_page.refresh()
        motion.switch(self.pages, self.team_page)

    # 대화상자

    def ask(self, title, text, buttons=(("확인", "ok"),), on_choice=None, detail="", link=""):
        """대화상자를 띄움. 빈 키("")가 아닌 버튼을 고르면 on_choice(키)를 부름."""
        if self.dialog is not None and not self.dialog.isVisible():
            self.dialog.deleteLater()  # 닫힌 대화상자가 창에 쌓이지 않게
        self.dialog = MessageDialog(self, title, text, buttons, lambda key: key and on_choice and on_choice(key), detail, link)
        self.dialog.show()
        return self.dialog

    def show_notice_detail(self):
        self.ask("자세히", self.notice.get("message") or "", detail=self.notice.get("detail") or "")

    def _session_error(self, error, rid, retry):
        """SessionError 의 문구를 대화상자로 보여 줌. 답안지가 깨진 경우에는 복구를 제안함."""
        if self.session.quiz_problem(rid):
            self.offer_repair(rid, retry)
        else:
            self.ask("알림", str(error))

    def offer_repair(self, rid, then):
        """깨진 답안지(quiz.py)의 복구를 제안하고, 복구한 뒤 then() 을 부름."""
        if self.dialog is not None and self.dialog.isVisible():  # 자동 저장이 거듭 실패해도 대화상자는 하나만
            return
        problem = self.session.quiz_problem(rid)
        if not problem:
            return

        def repair(_):
            kept = self.session.repair_quiz(rid)
            then()
            self.ask("답안지 복구", "답안지를 복구했습니다. 읽을 수 있던 답 %d개를 남겼습니다.\n원본은 같은 폴더의 quiz.py.bak 에 있습니다." % kept)

        self.ask("답안지 복구", "%s\n\n복구하면 읽을 수 있는 답만 남기고 답안지를 새로 씁니다. 원본은 같은 폴더에 quiz.py.bak 으로 보관합니다." % problem,
                 (("답안지 복구", "repair"), ("닫기", "")), repair)

    # 워커

    def run_job(self, text, fn, on_done, on_fail=None):
        """fn 을 워커 스레드에서 돌리고, 끝나면 화면 스레드에서 on_done(결과)을 부름. 도는 동안 지금 화면을 잠금."""
        if self.job is not None:
            return
        page = self.pages.currentWidget()
        page.set_busy(True, text)
        job = Job(fn)
        self.job = (job, page, on_done, on_fail)
        job.done.connect(self._job_done)
        job.failed.connect(self._job_failed)
        job.start()

    def _job_end(self):
        job, page, on_done, on_fail = self.job
        job.wait()
        self.job = None
        page.set_busy(False)
        return on_done, on_fail

    def _job_done(self, result):
        on_done, _ = self._job_end()
        on_done(result)
        if self.close_pending:
            self.close()

    def _job_failed(self, message, trace):
        _, on_fail = self._job_end()
        if trace:
            errors.report(trace)
        else:
            self.ask("알림", message)
        if on_fail:
            on_fail()
        if self.close_pending:
            self.close()

    # 제출 · 문제 받기

    def submit_pr(self):
        if self.round_page.flush():  # 쓰다 만 답이 빠진 채 올라가지 않게
            self.run_job("제출하는 중입니다.", self.gitflow.submit, lambda result: self._git_done("제출", result))

    def fetch_problems(self):
        if self.round_page.flush():
            self.run_job("새 문제 확인 중입니다.", self.gitflow.sync, self._fetched)

    def _fetched(self, result):
        self.notice = None  # 시작할 때 받지 못했다는 알림은 방금 결과가 대신함
        self.home.refresh()
        self._git_done("문제 받기", result)

    def _git_done(self, title, result):
        if result.get("restart"):
            self._restart(result)
            return
        if result.get("changed") and not self.open_session():  # 문제나 내 풀이 폴더가 바뀌었으면 새로 읽음
            return
        message = result.get("message") or "(안내 문구가 없습니다)"
        if result.get("backup"):
            message += "\n보관한 사본: %s" % result["backup"]
        detail = result.get("detail") or ""
        if result.get("status") == "diverged":
            self.ask(title, message, (("다른 컴퓨터의 풀이 가져오기", "remote"), ("이 컴퓨터 풀이로 올리기", "local"), ("나중에 정하기", "")),
                     lambda choice: self.run_job("처리하는 중입니다.", lambda: self._resolve(title, choice),
                                                 lambda done: self._git_done(title, done)), detail)
            return
        url = result.get("pr_url") if result.get("status") == "ok" else None
        if url:
            self.open_url(url)
            message += "\n\n브라우저에서 PR 페이지를 열었습니다. 열리지 않았으면 아래 주소를 누르세요."
        self.ask(title, message, detail=detail, link=url or "")

    def _resolve(self, title, choice):
        """갈라진 풀이를 정함. 문제 받기 도중이었으면 그 전에는 새 문제가 들어오지 않았으므로 받기를 마저 함."""
        done = self.gitflow.resolve(choice)
        if title == "문제 받기" and done.get("status") in ("ok", "nothing"):
            again = self.gitflow.sync()
            again["changed"] = again.get("changed") or done.get("changed")
            again["backup"] = again.get("backup") or done.get("backup")
            return again
        return done

    def _restart(self, result):
        """도구 파일이 바뀌었으면 옛 코드로 새 파일을 다루지 않게, 대화상자를 어떻게 닫든 다시 시작함."""
        dialog = self.ask("프로그램 갱신", result.get("message") or "프로그램이 새 버전으로 바뀌었습니다. 다시 시작합니다.", (("다시 시작", "ok"),))
        dialog.finished.connect(self._quit_for_restart)

    def _quit_for_restart(self):
        self.restart = True
        self.close()

    # 글자 크기 · 테마 · 닫기

    def set_zoom(self, zoom):
        low, high = theme.ZOOM_RANGE
        self.zoom = max(low, min(high, zoom))
        self.settings.setValue("zoom", self.zoom)
        self.restyle()

    def cycle_theme(self):
        """시스템 → 밝게 → 어둡게 순서로 다음 테마를 고르고 기억함."""
        modes = list(theme.MODES)
        mode = modes[(modes.index(theme.state["mode"]) + 1) % len(modes)]
        self.settings.setValue("theme", mode)

        def change():
            theme.set_mode(mode)
            self.home.restyle()  # 밝기가 그대로여도 단추의 글자는 바뀜

        motion.fade_over(self, change)

    def restyle(self):
        """글자 크기나 테마가 바뀌면 화면마다 본문과 색을 다시 넣음."""
        for page in (self.home, self.round_page, self.result_page):
            page.restyle()

    def closeEvent(self, event):
        if self.job is not None:  # 스레드를 도중에 버리면 프로세스가 죽으므로 채점·제출이 끝난 뒤에 닫음
            self.close_pending = True
            self.job[1].set_busy(True, "하던 작업이 끝나면 창을 닫습니다.")
            event.ignore()
            return
        if not self.leave_round(self.close, "저장하지 않고 닫기"):
            event.ignore()
            return
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()
