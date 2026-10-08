# -*- coding: utf-8 -*-
"""시험처럼 복사·잘라내기·붙여넣기와 우클릭 메뉴를 막음. 대화상자(오류 내용 복사, ID 입력)는 막지 않음."""
from PyQt6.QtCore import QEvent, QObject, pyqtSignal
from PyQt6.QtGui import QKeySequence
from PyQt6.QtWidgets import QWidget

NOTE = "복사와 붙여넣기는 막아 두었습니다. 시험처럼 직접 입력해 주세요."
KEYS = (QKeySequence.StandardKey.Copy, QKeySequence.StandardKey.Cut, QKeySequence.StandardKey.Paste)


class Guard(QObject):
    blocked = pyqtSignal()  # 단축키를 막았을 때

    def __init__(self, window):
        super().__init__(window)
        self.window = window

    def eventFilter(self, target, event):
        kind = event.type()
        if kind not in (QEvent.Type.ContextMenu, QEvent.Type.KeyPress):
            return False
        if not isinstance(target, QWidget) or target.window() is not self.window:
            return False
        if kind == QEvent.Type.ContextMenu:
            return True
        if any(event.matches(key) for key in KEYS):
            self.blocked.emit()
            return True
        return False
