# -*- coding: utf-8 -*-
"""홈 화면: 시험 준비도 · 단원 띠 · 지금 할 일 · 지난 회차 · 제출."""
import html

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QFrame, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QProgressBar, QPushButton, QScrollArea,
                             QVBoxLayout, QWidget)

from gui import errors
from gui.widgets import UnitStrip


def card(title):
    frame = QFrame()
    frame.setObjectName("card")
    box = QVBoxLayout(frame)
    box.setContentsMargins(18, 14, 18, 14)
    box.setSpacing(8)
    head = QLabel(title)
    head.setObjectName("h2")
    box.addWidget(head)
    return frame, box


def muted(text=""):
    label = QLabel(text)
    label.setObjectName("muted")
    label.setWordWrap(True)
    return label


class HomePage(QWidget):
    def __init__(self, win):
        super().__init__()
        self.setObjectName("page")
        self.win = win
        inner = QWidget()
        inner.setObjectName("page")
        scroll = QScrollArea()  # 창이 작으면 내용을 찌그러뜨리지 않고 스크롤한다
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(inner)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)
        root = QVBoxLayout(inner)
        root.setContentsMargins(24, 16, 24, 12)
        root.setSpacing(12)

        head = QHBoxLayout()
        title = QLabel("ROKEY 파이썬 스터디")
        title.setObjectName("h1")
        self.user = muted()
        self.user.setWordWrap(False)
        head.addWidget(title)
        head.addStretch(1)
        head.addWidget(self.user)
        root.addLayout(head)
        self.notice = QLabel()
        self.notice.setObjectName("notice")
        self.notice.setWordWrap(True)
        self.notice.linkActivated.connect(lambda _: win.show_notice_detail())
        self.notice.hide()
        root.addWidget(self.notice)

        top = QHBoxLayout()
        top.setSpacing(12)
        ready_card, box = card("시험 준비도")
        line = QHBoxLayout()
        self.ready = QLabel()
        self.ready.setObjectName("big")
        side = QVBoxLayout()
        self.ready_bar = QProgressBar()
        self.ready_bar.setRange(0, 100)
        self.ready_bar.setTextVisible(False)
        self.mastered = QLabel()
        side.addStretch(1)
        side.addWidget(self.ready_bar)
        side.addWidget(self.mastered)
        side.addStretch(1)
        line.addWidget(self.ready)
        line.addSpacing(16)
        line.addLayout(side, 1)
        box.addLayout(line)
        box.addWidget(muted("단원별 준비도를 시험 비중에 맞춰 평균한 값입니다. 회차를 제출할 때마다 바뀝니다."))
        action_card, box = card("지금 할 일")
        self.action_desc = muted()
        self.action_btn = QPushButton()
        self.action_btn.setObjectName("primary")
        self.action_btn.setProperty("big", True)
        self.action_btn.setMinimumHeight(52)
        box.addWidget(self.action_desc)
        box.addStretch(1)
        box.addWidget(self.action_btn)
        top.addWidget(ready_card, 3)
        top.addWidget(action_card, 2)
        root.addLayout(top)

        units_card, box = card("단원별 상태")
        self.strip = UnitStrip()
        self.weak = muted()
        box.addWidget(self.strip)
        box.addWidget(self.weak)
        root.addWidget(units_card)

        bottom = QHBoxLayout()
        bottom.setSpacing(12)
        rounds_card, box = card("지난 회차")
        self.rounds = QListWidget()
        self.rounds.setObjectName("plain")
        self.rounds.setCursor(Qt.CursorShape.PointingHandCursor)
        self.rounds_hint = muted()
        box.addWidget(self.rounds_hint)
        box.addWidget(self.rounds, 1)
        column = QVBoxLayout()
        column.setSpacing(12)
        git_card, box = card("제출")
        row = QHBoxLayout()
        self.git_btn = QPushButton("제출(PR 올리기)")
        self.sync_btn = QPushButton("문제 받기")
        row.addWidget(self.git_btn, 1)
        row.addWidget(self.sync_btn, 1)
        self.git_hint = muted()
        self.status = muted()
        self.busy_bar = QProgressBar()
        self.busy_bar.setRange(0, 0)
        self.busy_bar.setTextVisible(False)
        self.busy_bar.hide()
        box.addLayout(row)
        box.addWidget(self.git_hint)
        box.addWidget(self.status)
        box.addWidget(self.busy_bar)
        guide_card, box = card("사용 순서")
        box.addWidget(muted("1. '지금 할 일'의 버튼을 눌러 문제를 풉니다. 답은 자동으로 저장되므로 창은 언제 닫아도 됩니다.\n"
                            "2. 다 풀면 '회차 제출'을 누릅니다. 채점 결과와 해설이 나오고 다음 회차가 준비됩니다.\n"
                            "3. '제출(PR 올리기)'를 누르면 풀이가 올라가고 브라우저에 PR 페이지가 열립니다."))
        box.addStretch(1)
        column.addWidget(git_card)
        column.addWidget(guide_card, 1)
        bottom.addWidget(rounds_card, 3)
        bottom.addLayout(column, 2)
        root.addLayout(bottom, 1)

        foot = QLabel("모의고사: 전 단원을 숙달한 뒤 터미널에서 <code>python study.py start m1</code> · 글자 크기: Ctrl(맥은 Cmd) 과 +, -, 0 · "
                      '<a href="%s">불편한 점 신고하기</a>' % errors.ISSUE_URL)
        foot.setObjectName("muted")
        foot.setOpenExternalLinks(True)
        root.addWidget(foot)

        self.action_btn.clicked.connect(win.start_next)
        self.git_btn.clicked.connect(win.submit_pr)
        self.sync_btn.clicked.connect(win.fetch_problems)
        self.rounds.itemClicked.connect(lambda item: win.show_result(item.data(Qt.ItemDataRole.UserRole)))

    def refresh(self):
        win = self.win
        overview = win.session.overview()
        self.user.setText("ID: %s" % overview["user"])
        self.ready.setText("%d%%" % overview["readiness"])
        self.ready_bar.setValue(overview["readiness"])
        self.mastered.setText("숙달한 단원 %d / %d" % (overview["mastered"], overview["total_units"]))
        self.strip.set_units(overview["units"])
        tags = overview["weak_tags"]
        self.weak.setText("약한 개념: " + (", ".join(tags) if tags else "아직 틀린 문항이 없습니다."))
        label, desc = win.next_action(overview)
        self.action_btn.setText(label)
        self.action_desc.setText(desc)
        self.rounds.clear()
        done = [r for r in overview["rounds"] if r["completed"]]
        for r in reversed(done):
            earned, total = (int(n) for n in (r["first_score"] or r["score"]).split("/"))
            item = QListWidgetItem("%s    %d / %d점 (%d%%)" % (r["title"], earned, total, round(100 * earned / total) if total else 0))
            item.setData(Qt.ItemDataRole.UserRole, r["id"])
            self.rounds.addItem(item)
        self.rounds_hint.setText("회차를 누르면 결과와 해설을 다시 볼 수 있습니다. 점수는 첫 제출 기준입니다." if done else "아직 제출한 회차가 없습니다.")
        usable = win.gitflow is not None
        self.git_btn.setEnabled(usable)
        self.sync_btn.setEnabled(usable)
        self.git_hint.setText("제출: 내 풀이 폴더를 올리고 브라우저에서 PR 페이지를 엽니다.\n문제 받기: 새로 올라온 문제를 내려받습니다. 내 풀이는 그대로 둡니다."
                              if usable else "지금은 제출과 문제 받기를 쓸 수 없습니다. 풀이와 채점은 그대로 됩니다.\n" + win.git_reason)
        note = win.notice
        self.notice.setVisible(bool(note))
        if note:
            more = ' <a href="detail">자세히</a>' if note.get("detail") else ""
            self.notice.setText(html.escape(note.get("message") or "") + more)

    def set_busy(self, busy, text=""):
        for widget in (self.action_btn, self.rounds):
            widget.setEnabled(not busy)
        for widget in (self.git_btn, self.sync_btn):
            widget.setEnabled(not busy and self.win.gitflow is not None)
        self.busy_bar.setVisible(busy)
        self.status.setText(text if busy else "")
