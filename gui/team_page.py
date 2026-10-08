# -*- coding: utf-8 -*-
"""팀 현황 화면: 풀이 기록이 있는 사람마다 카드 하나. 준비도가 높은 순으로 두 열에 놓음."""
import re

from PyQt6.QtCore import QRectF, QSize, Qt
from PyQt6.QtGui import QColor, QFont, QPainter
from PyQt6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QProgressBar, QPushButton, QScrollArea, QVBoxLayout, QWidget

from gui import motion, theme
from gui.home_page import muted
from gui.mascot import Mascot
from gui.widgets import UnitStrip, unit_legend

NOTE = "내 카드는 이 컴퓨터의 풀이 기록이고, 다른 사람의 카드는 main 에 머지된 풀이 기준입니다. 홈에서 [문제 받기]를 누르면 새로 받습니다."
COLUMNS = 2


def initials(user):
    """ID 의 머리글자 두 자. gildong-hong 은 GH, tester 는 TE."""
    parts = [part for part in re.split(r"[-_]+", user) if part]
    return (parts[0][0] + parts[1][0] if len(parts) > 1 else user[:2]).upper()


class Avatar(QWidget):
    """머리글자를 넣은 원. tone 은 theme.AVATARS 에서 고를 색의 순번."""

    def __init__(self, user, tone):
        super().__init__()
        self.setFixedSize(40, 40)
        self.text = initials(user)
        self.back = QColor(theme.AVATARS[tone % len(theme.AVATARS)])

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.back)
        painter.drawEllipse(QRectF(self.rect()))
        font = QFont(self.font())
        font.setBold(True)
        font.setPixelSize(round(self.height() * 0.36))
        painter.setFont(font)
        painter.setPen(QColor(theme.BRAND[2]))
        painter.drawText(QRectF(self.rect()), Qt.AlignmentFlag.AlignCenter, self.text)


class ElideLabel(QLabel):
    """한 줄 글. 폭이 모자라면 끝을 줄임표로 줄이고 전체 글은 툴팁으로 보여 줌. 긴 ID 가 카드 폭을 밀어 두 열의 폭이 달라지지 않게 함."""

    def __init__(self, text):
        super().__init__(text)
        self.full = text
        self.setMinimumWidth(48)

    def sizeHint(self):
        hint = super().sizeHint()  # 줄인 글이 아니라 전체 글의 폭을 알려야 자리가 나면 다시 늘어남
        return QSize(self.fontMetrics().horizontalAdvance(self.full) + 2, hint.height())

    def resizeEvent(self, event):
        shown = self.fontMetrics().elidedText(self.full, Qt.TextElideMode.ElideRight, self.width())
        self.setText(shown)
        self.setToolTip("" if shown == self.full else self.full)


class MemberCard(QFrame):
    """한 사람의 현황. row 는 session.team() 의 항목, tone 은 이니셜 원의 색 순번."""

    def __init__(self, row, tone):
        super().__init__()
        self.setObjectName("card")
        self.setProperty("me", row["me"])
        box = QVBoxLayout(self)
        box.setContentsMargins(18, 14, 18, 14)
        box.setSpacing(10)

        head = QHBoxLayout()
        head.setSpacing(12)
        name = QHBoxLayout()
        name.setSpacing(8)
        self.user = ElideLabel(row["user"])
        self.user.setObjectName("h2")
        name.addWidget(self.user)
        if row["me"]:
            self.me = QLabel("나")
            self.me.setObjectName("me")
            name.addWidget(self.me)
        name.addStretch(1)
        accuracy = "-" if row["accuracy"] is None else "%d%%" % round(row["accuracy"] * 100)
        self.facts = muted("회차 %d · 정답률 %s · 마지막 풀이 %s" % (row["rounds"], accuracy, row["last"] or "-"))
        who = QVBoxLayout()
        who.setSpacing(2)
        who.addLayout(name)
        who.addWidget(self.facts)
        ready_name = QLabel("준비도")
        ready_name.setObjectName("muted")
        self.ready = QLabel("%d%%" % row["readiness"])
        self.ready.setObjectName("ready")
        head.addWidget(Avatar(row["user"], tone))
        head.addLayout(who, 1)
        head.addWidget(ready_name, 0, Qt.AlignmentFlag.AlignBottom)
        head.addWidget(self.ready, 0, Qt.AlignmentFlag.AlignBottom)
        box.addLayout(head)

        line = QHBoxLayout()
        line.setSpacing(12)
        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setTextVisible(False)
        self.mastered = QLabel("숙달한 단원 %d / %d" % (row["mastered"], row["total"]))
        line.addWidget(self.bar, 1)
        line.addWidget(self.mastered)
        box.addLayout(line)

        self.strip = UnitStrip(compact=True)
        self.strip.set_units(row["units"])
        box.addWidget(self.strip)
        titles = {unit["unit"]: unit["title"] for unit in row["units"]}
        self.weak = muted("약한 단원: " + (", ".join(titles[unit] for unit in row["weak"]) or "-"))
        self.strong = muted("능숙한 단원: " + (", ".join(titles[unit] for unit in row["strong"]) or "-"))
        box.addWidget(self.weak)
        box.addWidget(self.strong)
        box.addStretch(1)
        motion.count(self.bar, row["readiness"], self.bar.setValue)


class EmptyCard(QFrame):
    """다른 사람의 풀이가 아직 없을 때 카드 자리에 놓는 안내. alone 이 False 면 내 카드도 아직 없음."""

    def __init__(self, alone):
        super().__init__()
        self.setObjectName("card")
        box = QVBoxLayout(self)
        box.setContentsMargins(18, 22, 18, 22)
        box.setSpacing(10)
        self.title = QLabel("아직 다른 사람의 풀이가 없습니다")
        self.title.setObjectName("h2")
        text = "팀원의 PR 이 main 에 머지된 뒤 홈에서 [문제 받기]를 누르면 여기에 카드가 생깁니다."
        self.text = muted(text if alone else text + "\n내 카드는 진단 테스트를 시작하면 생깁니다.")
        self.text.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        box.addStretch(1)
        box.addWidget(Mascot(88), 0, Qt.AlignmentFlag.AlignHCenter)
        box.addWidget(self.title, 0, Qt.AlignmentFlag.AlignHCenter)
        box.addWidget(self.text)
        box.addStretch(1)


class TeamPage(QWidget):
    def __init__(self, win):
        super().__init__()
        self.setObjectName("page")
        self.win = win
        self.cards, self.empty = [], None
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 12, 24, 12)
        root.setSpacing(10)
        head = QHBoxLayout()
        self.home_btn = QPushButton("홈으로")
        title = QLabel("팀 현황")
        title.setObjectName("h1")
        head.addWidget(self.home_btn)
        head.addSpacing(8)
        head.addWidget(title)
        head.addStretch(1)
        root.addLayout(head)
        root.addWidget(muted(NOTE))
        root.addLayout(unit_legend())

        inner = QWidget()
        inner.setObjectName("page")
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(inner)
        column = QVBoxLayout(inner)
        column.setContentsMargins(0, 0, 0, 0)
        self.grid = QGridLayout()
        self.grid.setSpacing(12)
        for n in range(COLUMNS):
            self.grid.setColumnStretch(n, 1)
        column.addLayout(self.grid)
        column.addStretch(1)
        root.addWidget(scroll, 1)
        self.home_btn.clicked.connect(win.go_home)

    def refresh(self):
        """풀이 기록을 다시 읽어 카드를 새로 놓음. 다른 사람의 카드가 하나도 없으면 빈 자리 안내를 덧붙임."""
        while self.grid.count():
            self.grid.takeAt(0).widget().deleteLater()
        rows = self.win.session.team()
        order = sorted(row["user"].lower() for row in rows)  # 색은 ID 순으로 돌려 써서 옆 사람과 겹치지 않게 함
        self.cards = [MemberCard(row, order.index(row["user"].lower())) for row in rows]
        for n, card in enumerate(self.cards):
            self.grid.addWidget(card, n // COLUMNS, n % COLUMNS)
        self.empty = None if any(not row["me"] for row in rows) else EmptyCard(alone=bool(rows))
        if self.empty:
            self.grid.addWidget(self.empty, len(rows) // COLUMNS, len(rows) % COLUMNS, 1, 1 if rows else COLUMNS)
