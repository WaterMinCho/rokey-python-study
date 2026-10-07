# -*- coding: utf-8 -*-
"""답안 입력 위젯과 단원 띠."""
import re

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import (QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit, QPushButton, QSplitter, QTextBrowser,
                             QVBoxLayout, QWidget)

from gui import theme

INDENT = 4


class CodeEditor(QPlainTextEdit):
    """시험 화면과 같은 편집기: 고정폭, 자동완성·문법 강조 없음. 들여쓰기만 돕는다(탭 문자는 넣지 않는다)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

    def keyPressEvent(self, event):
        key, cur = event.key(), self.textCursor()
        back = key == Qt.Key.Key_Backtab or (key == Qt.Key.Key_Tab and bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier))
        if self.isReadOnly():
            super().keyPressEvent(event)
        elif back or (key == Qt.Key.Key_Tab and cur.hasSelection()):
            self._shift_lines(-1 if back else 1)
        elif key == Qt.Key.Key_Tab:
            cur.insertText(" " * (INDENT - cur.positionInBlock() % INDENT))
        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            cur.beginEditBlock()
            cur.removeSelectedText()
            before = cur.block().text()[:cur.positionInBlock()]
            pad = before[:len(before) - len(before.lstrip(" "))]
            if before.rstrip().endswith(":"):
                pad += " " * INDENT
            cur.insertText("\n" + pad)
            cur.endEditBlock()
            self.ensureCursorVisible()
        elif key == Qt.Key.Key_Backspace and not cur.hasSelection() and self._in_indent(cur):
            cur.beginEditBlock()
            for _ in range((cur.positionInBlock() - 1) % INDENT + 1):  # 들여쓰기 한 단계(최대 4칸)
                cur.deletePreviousChar()
            cur.endEditBlock()
        else:
            super().keyPressEvent(event)

    @staticmethod
    def _in_indent(cur):
        before = cur.block().text()[:cur.positionInBlock()]
        return bool(before) and not before.strip(" ")

    def _shift_lines(self, direction):
        cur, doc = self.textCursor(), self.document()
        first = doc.findBlock(cur.selectionStart()).blockNumber()
        last = doc.findBlock(max(cur.selectionStart(), cur.selectionEnd() - 1)).blockNumber()
        cur.beginEditBlock()
        for number in range(first, last + 1):
            block = doc.findBlockByNumber(number)
            edit = QTextCursor(block)
            if direction > 0:
                edit.insertText(" " * INDENT)
            else:
                text = block.text()
                drop = min(INDENT, len(text) - len(text.lstrip(" ")))
                edit.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, drop)
                edit.removeSelectedText()
        cur.endEditBlock()

    def insertFromMimeData(self, source):  # 붙여넣기: 서식 없이, 탭은 공백 4칸으로
        if source.hasText():
            self.insertPlainText(source.text().replace("\r\n", "\n").replace("\r", "\n").replace("\t", " " * INDENT))


def hint_label():
    label = QLabel()
    label.setObjectName("muted")
    label.setWordWrap(True)
    return label


class ChoicePanel(QWidget):
    """객관식: 보기 수만큼 번호 버튼. 보기 수를 세지 못한 문항은 번호 입력칸."""
    changed = pyqtSignal(object)  # 고른 번호 목록

    def __init__(self, parent=None):
        super().__init__(parent)
        self.box = QVBoxLayout(self)
        self.box.setContentsMargins(0, 0, 0, 0)
        self.hint = hint_label()
        self.entry = QLineEdit()
        self.entry.setPlaceholderText("예: 2   (여러 개면 1, 3)")
        self.entry.textChanged.connect(lambda text: self.changed.emit(sorted({int(n) for n in re.findall(r"\d+", text)})))
        self.box.addWidget(self.hint)
        self.box.addWidget(self.entry)
        self.box.addStretch(1)
        self.buttons, self.multi = [], False

    def set_item(self, item):
        for button in self.buttons:
            self.box.removeWidget(button)
            button.deleteLater()
        self.buttons, self.multi = [], item["multi"]
        answer = item["answer"]
        picked = [] if answer is None else (list(answer) if isinstance(answer, (list, tuple)) else [answer])
        many = "정답을 모두 고르세요. 여러 개를 선택할 수 있습니다." if item["multi"] else "보기 번호를 고르세요. 다시 누르면 선택이 풀립니다."
        self.hint.setText(many if item["choices"] else "보기 번호를 숫자로 적으세요.")
        self.entry.setVisible(not item["choices"])
        self.entry.blockSignals(True)
        self.entry.setText(", ".join(str(n) for n in picked))
        self.entry.blockSignals(False)
        for number in range(1, item["choices"] + 1):
            button = QPushButton("%d번" % number)
            button.setObjectName("choice")
            button.setCheckable(True)
            button.setChecked(number in picked)
            button.clicked.connect(lambda checked, n=number: self._clicked(n, checked))
            self.box.insertWidget(self.box.count() - 1, button)
            self.buttons.append(button)

    def _clicked(self, number, checked):
        if checked and not self.multi:  # 단일 정답: 하나만 남긴다
            for other, button in enumerate(self.buttons, 1):
                if other != number:
                    button.setChecked(False)
        self.changed.emit([n for n, button in enumerate(self.buttons, 1) if button.isChecked()])

    def focus_input(self):
        pass


class TextPanel(QWidget):
    """출력 예측(여러 줄) · 단답(한 줄). 고정폭이라 공백과 줄바꿈이 보이는 그대로 저장된다."""
    changed = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        box = QVBoxLayout(self)
        box.setContentsMargins(0, 0, 0, 0)
        self.hint = hint_label()
        self.multi = QPlainTextEdit()
        self.multi.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.multi.setTabChangesFocus(True)
        self.single = QLineEdit()
        self.single.setMinimumHeight(38)
        box.addWidget(self.hint)
        box.addWidget(self.multi, 1)
        box.addWidget(self.single)
        self.pad = QWidget()
        box.addWidget(self.pad, 1)
        self.multi.textChanged.connect(lambda: self.changed.emit(self.multi.toPlainText()))
        self.single.textChanged.connect(self.changed.emit)

    def set_item(self, item):
        is_output = item["type"] == "output"
        for widget in (self.multi, self.single):
            widget.blockSignals(True)
        self.multi.setVisible(is_output)
        self.single.setVisible(not is_output)
        self.pad.setVisible(not is_output)
        self.hint.setText("따옴표 없이, 화면에 나올 그대로 적으세요." + (" 여러 줄이면 줄을 바꿔 적습니다." if is_output else ""))
        text = item["answer"] or ""
        self.multi.setPlainText(text if is_output else "")
        self.single.setText("" if is_output else text)
        for widget in (self.multi, self.single):
            widget.blockSignals(False)

    def focus_input(self):
        (self.multi if self.multi.isVisible() else self.single).setFocus()


class CodePanel(QWidget):
    changed = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        box = QVBoxLayout(self)
        box.setContentsMargins(0, 0, 0, 0)
        top = QHBoxLayout()
        self.hint = hint_label()
        self.reset_btn = QPushButton("시작 코드로 되돌리기")
        top.addWidget(self.hint, 1)
        top.addWidget(self.reset_btn)
        box.addLayout(top)
        split = QSplitter(Qt.Orientation.Vertical)
        self.editor = CodeEditor()
        self.console = QTextBrowser()
        self.console.setOpenLinks(False)
        self.console.setPlaceholderText("'코드 실행'을 누르면 예시 실행 결과가 여기에 나옵니다. 예시만 실행하며 기록되지 않습니다.")
        split.addWidget(self.editor)
        split.addWidget(self.console)
        split.setSizes([340, 280])
        split.setChildrenCollapsible(False)
        box.addWidget(split, 1)
        self.editor.textChanged.connect(lambda: self.changed.emit(self.editor.toPlainText()))
        self.console_html = ""

    def set_item(self, item):
        self.hint.setText("빈칸(____)만 채우세요. 다른 부분은 고치지 않습니다." if item["type"] == "fill" else "아래에 코드를 작성하세요.")
        self.set_code(item["answer"])
        self.show_console("")

    def set_code(self, text):
        self.editor.blockSignals(True)
        self.editor.setPlainText(text)
        self.editor.blockSignals(False)

    def show_console(self, html):
        self.console_html = html
        self.console.setHtml(html)

    def focus_input(self):
        self.editor.setFocus()


class UnitStrip(QWidget):
    """차시별 칸 하나씩. 색으로 상태를 보이고, 마우스를 올리면 단원 이름과 상태가 나온다."""

    def __init__(self, parent=None):
        super().__init__(parent)
        box = QVBoxLayout(self)
        box.setContentsMargins(0, 0, 0, 0)
        box.setSpacing(8)
        self.cells = QHBoxLayout()
        self.cells.setSpacing(4)
        legend = QHBoxLayout()
        legend.setSpacing(6)
        for state, (name, _, _) in theme.UNIT.items():
            swatch = QLabel()
            swatch.setObjectName("unit_" + state)
            swatch.setFixedSize(12, 12)
            text = QLabel(name)
            text.setObjectName("muted")
            legend.addWidget(swatch)
            legend.addWidget(text)
            legend.addSpacing(10)
        legend.addStretch(1)
        box.addLayout(self.cells)
        box.addLayout(legend)

    @staticmethod
    def state_of(unit):
        if not unit["tested"]:
            return "none"
        if unit["mastered"]:
            return "mastered"
        if unit["retry"]:
            return "retry"
        return "level1" if unit["level"] == 1 else "level2"

    def set_units(self, units):
        while self.cells.count():
            self.cells.takeAt(0).widget().deleteLater()
        for unit in units:
            number = unit["unit"][1:]
            cell = QLabel(str(int(number)) if number.isdigit() else unit["unit"])
            cell.setObjectName("unit_" + self.state_of(unit))  # 색은 theme.STYLE 에서(위젯에 직접 주면 툴팁까지 물든다)
            cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cell.setMinimumHeight(38)
            accuracy = "" if unit["accuracy"] is None else " · 정답률 %d%% (%d문항)" % (round(unit["accuracy"] * 100), unit["attempted"])
            cell.setToolTip("%s %s\n%s%s" % (unit["unit"], unit["title"], unit["label"], accuracy))
            self.cells.addWidget(cell, 1)
