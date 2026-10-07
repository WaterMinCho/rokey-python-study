# -*- coding: utf-8 -*-
"""대화상자. 모두 exec() 없이 show() 로 띄우고 고른 결과를 콜백으로 넘긴다(화면이 멈추지 않고 시험하기 쉽다)."""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QDialog, QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit, QPushButton, QVBoxLayout

import session


class MessageDialog(QDialog):
    """안내·확인. buttons 는 (글자, 키) 목록이고 첫 번째를 강조한다. 창을 그냥 닫으면 고른 키는 "" 이다."""

    def __init__(self, parent, title, text, buttons=(("확인", "ok"),), on_choice=None, detail="", link=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.on_choice, self.choice = on_choice, ""
        box = QVBoxLayout(self)
        box.setContentsMargins(22, 20, 22, 16)
        box.setSpacing(12)
        head = QLabel(title)
        head.setObjectName("h2")
        self.text = QLabel(text)
        self.text.setTextFormat(Qt.TextFormat.PlainText)
        self.text.setWordWrap(True)
        self.text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        box.addWidget(head)
        box.addWidget(self.text)
        if link:
            self.link = QLabel('<a href="%s">%s</a>' % (link, link))
            self.link.setWordWrap(True)
            self.link.linkActivated.connect(lambda url: parent.open_url(url))
            box.addWidget(self.link)
        self.detail = QPlainTextEdit(detail)
        self.detail.setReadOnly(True)
        self.detail.setMinimumHeight(140)
        self.detail.hide()
        box.addWidget(self.detail)
        row = QHBoxLayout()
        if detail:
            more = QPushButton("자세히")
            more.clicked.connect(lambda: (self.detail.setVisible(not self.detail.isVisible()), self.fit()))
            copy = QPushButton("내용 복사")
            copy.clicked.connect(lambda: QGuiApplication.clipboard().setText("%s\n\n%s" % (text, detail)))
            row.addWidget(more)
            row.addWidget(copy)
        row.addStretch(1)
        self.buttons = {}
        for label, key in reversed(buttons):  # 첫 번째 버튼이 오른쪽 끝에 오게
            button = QPushButton(label)
            button.setAutoDefault(False)
            button.clicked.connect(lambda checked=False, k=key: self.choose(k))
            row.addWidget(button)
            self.buttons[key] = button
        first = self.buttons[buttons[0][1]]
        first.setObjectName("primary")
        first.setDefault(len(buttons) == 1)  # 고를 것이 있는 대화상자는 Enter 로 넘어가지 않게 한다(실수로 회차를 제출하지 않게)
        box.addLayout(row)
        self.fit()

    def fit(self):
        """글이 줄바꿈되는 폭에 맞춰 높이를 잡는다(줄바꿈하는 QLabel 의 크기 추정은 좁고 길게 나와 빈 줄이 생긴다)."""
        width = max(480, self.layout().minimumSize().width())
        self.resize(width, self.layout().totalHeightForWidth(width))

    def choose(self, key):
        self.choice = key
        self.accept()
        if self.on_choice:
            self.on_choice(key)


class IdDialog(QDialog):
    """첫 실행: 깃허브 ID 를 받아 저장한다."""

    def __init__(self, parent, on_saved):
        super().__init__(parent)
        self.setWindowTitle("처음 오셨네요")
        self.setModal(True)
        self.setMinimumWidth(480)
        self.on_saved = on_saved
        box = QVBoxLayout(self)
        box.setContentsMargins(22, 20, 22, 16)
        box.setSpacing(10)
        head = QLabel("깃허브 ID 를 입력해 주세요")
        head.setObjectName("h2")
        why = QLabel("내 풀이를 저장하는 폴더 이름(submissions/ID)과 제출할 때 올라가는 브랜치 이름에 쓰입니다. "
                     "한 번만 입력하면 됩니다.")
        why.setWordWrap(True)
        why.setObjectName("muted")
        self.edit = QLineEdit()
        self.edit.setPlaceholderText("예: WaterMinCho")
        self.error = QLabel(" ")
        self.error.setObjectName("error")
        self.error.setWordWrap(True)
        self.ok = QPushButton("시작")
        self.ok.setObjectName("primary")
        self.ok.setDefault(True)
        self.ok.setEnabled(False)
        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(self.ok)
        for widget in (head, why, self.edit, self.error):
            box.addWidget(widget)
        box.addLayout(row)
        self.edit.textChanged.connect(self.check)
        self.ok.clicked.connect(self.save)

    def check(self, text):
        text = text.strip()
        good = session.valid_user(text)
        self.ok.setEnabled(good)
        self.error.setText(" " if good or not text else "영문·숫자·-·_ 만 쓸 수 있고, 첫 글자는 영문이나 숫자여야 합니다.")

    def save(self):
        QGuiApplication.inputMethod().commit()
        try:
            user = session.save_user(self.edit.text())
        except (session.SessionError, OSError) as error:
            self.error.setText(str(error))
            return
        self.accept()
        self.on_saved(user)


class ErrorDialog(QDialog):
    """예상하지 못한 오류. 풀이는 자동 저장돼 있으므로 창은 계속 쓸 수 있다."""

    def __init__(self, text, log_path, issue_url):
        super().__init__()
        self.setWindowTitle("프로그램 오류")
        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, False)  # 이 창이 남아 있어도 본 창을 닫으면 프로그램이 끝나게
        self.resize(640, 420)
        box = QVBoxLayout(self)
        box.setContentsMargins(22, 20, 22, 16)
        box.setSpacing(10)
        head = QLabel("프로그램에서 오류가 났습니다")
        head.setObjectName("h2")
        note = QLabel("작성한 답은 저장돼 있고, 이 창을 닫으면 계속 쓸 수 있습니다. 같은 오류가 반복되면 아래 내용을 복사해 "
                      '<a href="%s">불편 신고 양식</a>에 붙여 주세요.' % issue_url)
        note.setWordWrap(True)
        note.setOpenExternalLinks(True)
        self.view = QPlainTextEdit(text)
        self.view.setReadOnly(True)
        where = QLabel("기록 파일: %s" % log_path if log_path else "기록 파일을 쓰지 못했습니다.")
        where.setObjectName("muted")
        where.setWordWrap(True)
        where.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.copy = QPushButton("오류 내용 복사")
        self.copy.clicked.connect(lambda: QGuiApplication.clipboard().setText(self.view.toPlainText()))
        close = QPushButton("닫기")
        close.setObjectName("primary")
        close.clicked.connect(self.accept)
        row = QHBoxLayout()
        row.addWidget(self.copy)
        row.addStretch(1)
        row.addWidget(close)
        for widget in (head, note, self.view, where):
            box.addWidget(widget)
        box.addLayout(row)

    def append(self, text):
        self.view.appendPlainText("\n" + text)
