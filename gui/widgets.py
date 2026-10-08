# -*- coding: utf-8 -*-
"""답안 입력 위젯과 단원 띠."""
import math
import re

from PyQt6.QtCore import QEvent, QObject, QPointF, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QKeySequence, QPainter, QPainterPath, QPen, QShortcut, QTextCursor, QTextDocument
from PyQt6.QtWidgets import (QFrame, QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit, QPushButton, QScrollArea, QSplitter, QTextBrowser,
                             QVBoxLayout, QWidget)

import mdlite
from gui import motion, theme

INDENT = 4


def is_paste(event):
    """붙여넣기 키(Ctrl/Cmd+V 와 플랫폼별 단축키, Shift+Insert)인지."""
    plain = event.modifiers() & ~Qt.KeyboardModifier.KeypadModifier
    return event.matches(QKeySequence.StandardKey.Paste) or (event.key() == Qt.Key.Key_Insert and plain == Qt.KeyboardModifier.ShiftModifier)


class PasteBlock(QObject):
    """답 칸의 붙여넣기를 막음: 붙여넣기 키, 가운데 버튼, 끌어다 놓기. 복사·잘라내기 키와 우클릭 메뉴는 gui/guard.py 가 창 전체에서 막음."""
    blocked = pyqtSignal()  # 붙여넣으려는 것을 막았을 때

    def __init__(self, parent=None):
        super().__init__(parent)

    def watch(self, edit):
        targets = [edit] + ([edit.viewport()] if isinstance(edit, QPlainTextEdit) else [])  # 여러 줄 칸의 마우스 이벤트는 viewport 가 받음
        for target in targets:
            target.installEventFilter(self)

    def eventFilter(self, target, event):
        kind, types = event.type(), QEvent.Type
        if kind == types.KeyPress and is_paste(event):
            self.blocked.emit()
            return True
        if kind in (types.MouseButtonPress, types.MouseButtonRelease) and event.button() == Qt.MouseButton.MiddleButton:
            if kind == types.MouseButtonRelease:
                self.blocked.emit()
            return True
        if kind in (types.DragEnter, types.DragMove, types.Drop):
            event.ignore()
            if kind != types.DragMove:
                self.blocked.emit()
            return True
        return False


class PlainEdit(QPlainTextEdit):
    """붙여넣기를 받지 않는 여러 줄 입력칸. 어느 길로 붙여넣든 insertFromMimeData 를 거치므로 여기서 버림."""

    def canInsertFromMimeData(self, source):
        return False

    def insertFromMimeData(self, source):
        pass


class CodeEditor(PlainEdit):
    """시험 화면과 같은 편집기. 고정폭이고 자동완성·문법 강조가 없음. 들여쓰기만 돕고 탭 문자는 넣지 않음."""

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


def hint_label():
    label = QLabel()
    label.setObjectName("muted")
    label.setWordWrap(True)
    return label


class LinkLabel(QLabel):
    """링크가 든 글. 링크 색은 글을 넣는 순간의 팔레트로 굳으므로 테마가 바뀌면 글을 다시 넣음."""

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.Type.PaletteChange and self.text():
            text = self.text()
            self.clear()  # 같은 글은 setText 가 건너뜀
            self.setText(text)


def content_height(doc):
    """문서의 내용이 끝나는 높이. 표나 코드 상자로 끝나면 그 아래 여백은 뺌."""
    last, child = None, doc.rootFrame().begin()
    while not child.atEnd():
        frame = child.currentFrame()
        if frame is not None or child.currentBlock().text():
            last = frame
        child += 1
    return doc.size().height() - (last.frameFormat().bottomMargin() if last is not None else 0)


class ChoiceCard(QWidget):
    """객관식 보기 하나: 번호 배지와 보기 내용. 어디를 눌러도 골라지고, 고르면 오른쪽에 체크 표시가 그려짐.
    내용이 없으면(보기를 나누지 못한 문항) 번호만 보여 줌."""
    picked = pyqtSignal(int)  # 누르거나 Space 로 골랐을 때. 보기 번호
    stepped = pyqtSignal(int, int)  # 위·아래 키. 보기 번호와 방향(-1, 1)
    PAD, BADGE, MARK = 12, 26, 18  # 안쪽 여백, 번호 배지의 한 변, 체크 표시의 한 변

    def __init__(self, number, html, css, multi, parent=None):
        super().__init__(parent)
        self.number, self.multi = number, multi
        self.html = html or "<body><p><b>%d번</b></p></body>" % number
        self.checked, self.tick, self.over, self.ring, self.top = False, 0.0, False, False, self.PAD
        self.down = False  # 이 카드에서 왼쪽 버튼을 누른 채인지
        self.doc = QTextDocument(self)
        self.doc.setDocumentMargin(0)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.restyle(css)

    def restyle(self, css):
        """본문과 같은 CSS 로 내용을 다시 넣음. 긴 코드 줄은 카드 폭에서 줄바꿈함."""
        self.doc.setDefaultFont(self.font())
        self.doc.setDefaultStyleSheet(css + "pre { white-space: pre-wrap; }")
        self.doc.setHtml(self.html)
        self.arrange()
        self.update()

    def arrange(self):
        """폭에 맞춰 내용을 줄바꿈하고 카드 높이를 정함. 첫 줄의 가운데를 번호 배지의 가운데에 맞춤."""
        self.doc.setTextWidth(max(80, self.width() - 4 * self.PAD - self.BADGE - self.MARK))
        height, first = content_height(self.doc), self.doc.firstBlock()
        line = first.layout().lineAt(0).height() if first.text() else self.BADGE  # 코드 상자로 시작하면 위쪽을 배지에 맞춤
        self.top = self.PAD + max(0.0, (self.BADGE - line) / 2)
        self.setFixedHeight(math.ceil(max(self.PAD + self.BADGE, self.top + height) + self.PAD))

    def isChecked(self):
        return self.checked

    def setChecked(self, checked, animate=False):
        self.checked, self.tick = checked, 0.0
        motion.play(self, motion.CHECK_MS if checked and animate else 0, self._draw_tick)  # 0 이면 돌던 것을 멈추고 곧바로 끝 상태

    def _draw_tick(self, t):
        self.tick = t
        self.update()

    def resizeEvent(self, event):
        self.arrange()

    def enterEvent(self, event):
        self.over = True
        self.update()

    def leaveEvent(self, event):
        self.over = False
        self.update()

    def focusInEvent(self, event):
        self.ring = event.reason() != Qt.FocusReason.MouseFocusReason  # 키보드로 옮겨 왔을 때만 테두리를 보임
        self.update()

    def focusOutEvent(self, event):
        self.ring = False
        self.update()

    def mousePressEvent(self, event):
        self.down = event.button() == Qt.MouseButton.LeftButton
        event.accept()

    def mouseDoubleClickEvent(self, event):
        """더블클릭의 두 번째 누름은 고르기로 치지 않음. 앞 화면의 버튼을 두 번 누른 것이 같은 자리의 카드로 들어와 답이 바뀌거나,
        방금 고른 카드가 바로 풀리지 않게 함."""
        self.down = False
        event.accept()

    def mouseReleaseEvent(self, event):
        down, self.down = self.down, False
        if down and event.button() == Qt.MouseButton.LeftButton and self.rect().contains(event.position().toPoint()):
            self.picked.emit(self.number)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_Space:
            if not event.isAutoRepeat():  # 누르고 있어도 한 번만 고름
                self.picked.emit(self.number)
        elif key in (Qt.Key.Key_Up, Qt.Key.Key_Down):
            self.stepped.emit(self.number, -1 if key == Qt.Key.Key_Up else 1)
        else:
            super().keyPressEvent(event)

    def paintEvent(self, event):
        on, pad, badge = self.checked, self.PAD, self.BADGE
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if not self.isEnabled():
            painter.setOpacity(0.55)
        edge = "primary" if on else ("border_strong" if self.over else "border")
        painter.setPen(QPen(theme.qcolor(edge), 2 if on else 1))
        painter.setBrush(theme.qcolor("selection" if on else ("hover" if self.over else "surface")))
        painter.drawRoundedRect(QRectF(self.rect()).adjusted(1, 1, -1, -1), 8, 8)
        if self.ring:
            painter.setPen(QPen(theme.qcolor("primary"), 1, Qt.PenStyle.DotLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(QRectF(self.rect()).adjusted(4.5, 4.5, -4.5, -4.5), 5, 5)
        corner = 7 if self.multi else badge / 2  # 여러 개를 고르는 문항은 네모, 하나만 고르는 문항은 동그라미
        painter.setPen(QPen(theme.qcolor("primary" if on else "border_strong"), 1.5))
        painter.setBrush(theme.qcolor("primary" if on else "surface_alt"))
        painter.drawRoundedRect(QRectF(pad, pad, badge, badge), corner, corner)
        font = QFont(self.font())
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(theme.qcolor("primary_ink" if on else "muted"))
        painter.drawText(QRectF(pad, pad, badge, badge), Qt.AlignmentFlag.AlignCenter, str(self.number))
        painter.save()
        painter.translate(2 * pad + badge, self.top)
        self.doc.drawContents(painter)
        painter.restore()
        if on and self.tick > 0:
            self._paint_tick(painter)

    def _paint_tick(self, painter):
        """체크 표시를 tick(0~1)만큼만 그림. 짧은 획을 먼저 긋고 긴 획을 이어 긋음."""
        size = self.MARK
        left, top = self.width() - self.PAD - size, self.PAD + (self.BADGE - size) / 2
        points = [QPointF(left + size * x, top + size * y) for x, y in ((0.12, 0.55), (0.4, 0.8), (0.9, 0.22))]
        short = math.hypot(points[1].x() - points[0].x(), points[1].y() - points[0].y())
        long = math.hypot(points[2].x() - points[1].x(), points[2].y() - points[1].y())
        drawn = self.tick * (short + long)
        path = QPainterPath(points[0])
        path.lineTo(points[0] + (points[1] - points[0]) * min(1.0, drawn / short))
        if drawn > short:
            path.lineTo(points[1] + (points[2] - points[1]) * ((drawn - short) / long))
        painter.setPen(QPen(theme.qcolor("primary"), 2.6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)


class ChoicePanel(QWidget):
    """객관식: 보기마다 카드 하나. 보기 수를 세지 못한 문항은 번호 입력칸.
    보기는 카드를 누르거나 숫자 키로 고르고, 카드에 포커스가 있으면 위·아래 키로 옮기고 Space 로 고름."""
    changed = pyqtSignal(object)  # 고른 번호 목록

    def __init__(self, parent=None):
        super().__init__(parent)
        box = QVBoxLayout(self)
        box.setContentsMargins(0, 0, 0, 0)
        self.hint = hint_label()
        self.stray = hint_label()  # 답안지에 손으로 적은 값이 카드와 맞지 않을 때의 안내
        self.stray.setObjectName("warn")
        self.stray.hide()
        self.entry = QLineEdit()
        self.entry.setPlaceholderText("예: 2   (여러 개면 1, 3)")
        self.entry.textChanged.connect(lambda text: self.changed.emit(sorted({int(n) for n in re.findall(r"\d+", text)})))
        inner = QWidget()
        inner.setObjectName("page")
        self.cards = QVBoxLayout(inner)
        self.cards.setContentsMargins(0, 0, 0, 0)
        self.cards.setSpacing(8)
        self.cards.addStretch(1)
        self.scroll = QScrollArea()  # 보기가 길어 칸을 넘으면 스크롤함
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.scroll.setWidget(inner)
        box.addWidget(self.hint)
        box.addWidget(self.stray)
        box.addWidget(self.entry)
        box.addWidget(self.scroll, 1)
        self.buttons, self.multi, self.css = [], False, ""
        # 숫자 키는 포커스가 문항 목록이나 다른 버튼에 있어도 듣고, 이 칸이 가려지거나 잠기면 듣지 않음. 입력칸에서는 글자로 들어감
        self.keys = [QShortcut(QKeySequence(str(number)), self, lambda n=number: self.toggle(n)) for number in range(1, 10)]
        for key in self.keys:
            key.setAutoRepeat(False)  # 누르고 있어도 한 번만 고름

    def set_item(self, item):
        for card in self.buttons:
            self.cards.removeWidget(card)
            card.deleteLater()
        self.buttons, self.multi = [], item["multi"]
        answer = item["answer"]
        picked = [] if answer is None else (list(answer) if isinstance(answer, (list, tuple, set)) else [answer])
        options = item.get("options") or [None] * item["choices"]  # 보기를 나누지 못한 문항은 번호만 든 카드
        # 따옴표로 감싼 번호나 없는 번호는 카드로 보여 줄 수 없고 그대로 두면 오답으로 채점되므로 알림
        stray = [value for value in picked if type(value) is not int or not 1 <= value <= len(options)] if options else []
        self.stray.setText("답안지에 적힌 값(%s)이 보기 번호와 맞지 않습니다. 보기를 다시 골라 주세요." % ", ".join(repr(value) for value in stray))
        self.stray.setVisible(bool(stray))
        many = "정답을 모두 고르세요. 보기를 누르거나 숫자 키(1~%d)로 고릅니다."
        one = "보기를 누르거나 숫자 키(1~%d)로 고르세요. 다시 누르면 선택이 풀립니다."
        self.hint.setText((many if item["multi"] else one) % len(options) if options else "보기 번호를 숫자로 적으세요.")
        self.entry.setVisible(not options)
        self.entry.blockSignals(True)
        self.entry.setText(", ".join(str(n) for n in picked))
        self.entry.blockSignals(False)
        for number, blocks in enumerate(options, 1):
            card = ChoiceCard(number, mdlite.blocks_html(blocks) if blocks else "", self.css, item["multi"])
            card.setChecked(number in picked and number not in stray)
            card.picked.connect(self.toggle)
            card.stepped.connect(self.step)
            self.cards.insertWidget(self.cards.count() - 1, card)
            self.buttons.append(card)
        for key in self.keys:
            key.setEnabled(bool(options))
        self.scroll.verticalScrollBar().setValue(0)

    def restyle(self, css):
        self.css = css
        for card in self.buttons:
            card.restyle(css)

    def toggle(self, number):
        """number 번 보기를 고르거나 풂. 단일 정답이면 방금 고른 것만 남김."""
        if not 1 <= number <= len(self.buttons):
            return
        card = self.buttons[number - 1]
        if not card.checked and not self.multi:
            for other in self.buttons:
                other.setChecked(False)
        card.setChecked(not card.checked, animate=True)
        self.stray.hide()  # 이제 저장되는 값은 카드에 보이는 그대로임
        self.scroll.ensureWidgetVisible(card, 0, 8)
        self.changed.emit([n for n, each in enumerate(self.buttons, 1) if each.checked])

    def step(self, number, direction):
        """number 번 카드에서 위나 아래 카드로 포커스를 옮김."""
        if 1 <= number + direction <= len(self.buttons):
            card = self.buttons[number + direction - 1]
            card.setFocus(Qt.FocusReason.TabFocusReason)
            self.scroll.ensureWidgetVisible(card, 0, 8)

    def focus_input(self):
        pass


class TextPanel(QWidget):
    """출력 예측(여러 줄) · 단답(한 줄). 고정폭이라 화면에 보이는 공백과 줄바꿈이 똑같이 저장됨."""
    changed = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        box = QVBoxLayout(self)
        box.setContentsMargins(0, 0, 0, 0)
        self.hint = hint_label()
        self.multi = PlainEdit()
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
        self.hint.setText("실행하면 화면에 찍히는 글자를 그대로 적으세요. 답을 따옴표로 감싸지는 않지만, 출력에 찍히는 따옴표는 적습니다. "
                          "여러 줄이면 줄을 바꿔 적습니다." if is_output else "따옴표 없이 한 줄로 적으세요.")
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


def unit_legend():
    """단원 띠의 색이 뜻하는 상태를 한 줄로 보여 줌."""
    legend = QHBoxLayout()
    legend.setSpacing(6)
    for state, name in theme.UNIT.items():
        swatch = QLabel()
        swatch.setObjectName("unit_" + state)
        swatch.setFixedSize(12, 12)
        text = QLabel(name)
        text.setObjectName("muted")
        legend.addWidget(swatch)
        legend.addWidget(text)
        legend.addSpacing(10)
    legend.addStretch(1)
    return legend


class UnitStrip(QWidget):
    """차시마다 칸 하나. 색으로 상태를 보이고, 마우스를 올리면 단원 이름과 상태가 나옴.
    compact 면 칸을 낮추고 범례를 빼서 팀 현황의 카드에 넣음."""

    def __init__(self, compact=False, parent=None):
        super().__init__(parent)
        self.cell_height = 24 if compact else 38
        box = QVBoxLayout(self)
        box.setContentsMargins(0, 0, 0, 0)
        box.setSpacing(8)
        self.cells = QHBoxLayout()
        self.cells.setSpacing(3 if compact else 4)
        box.addLayout(self.cells)
        if not compact:
            box.addLayout(unit_legend())

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
            cell.setObjectName("unit_" + self.state_of(unit))  # 색을 위젯에 직접 주면 툴팁까지 물들어서 theme.STYLE 에서 줌
            cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cell.setMinimumHeight(self.cell_height)
            accuracy = "" if unit["accuracy"] is None else " · 정답률 %d%% (%d문항)" % (round(unit["accuracy"] * 100), unit["attempted"])
            cell.setToolTip("%s %s\n%s%s" % (unit["unit"], unit["title"], unit["label"], accuracy))
            self.cells.addWidget(cell, 1)
