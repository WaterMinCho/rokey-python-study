# -*- coding: utf-8 -*-
"""마스코트: 아이콘의 R 을 얼굴로 한 로봇. 그림 파일 없이 QPainter 로 그림."""
from PyQt6.QtCore import QEasingCurve, QPointF, QRectF, Qt, QTimer
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPainterPathStroker, QPen
from PyQt6.QtWidgets import QWidget

from gui import icon, motion, theme

BLINK_EVERY_MS = 4200
SLIT = 1.2  # 감은 눈으로 남는 틈의 높이(반지름)


def eye(openness):
    """눈 자리에 뚫을 모양. openness 가 1 이면 뜬 눈, 0 이면 감은 눈."""
    edge = icon.ROUND / 2
    hole = QPainterPath()
    hole.addEllipse(QPointF(icon.EYE[0], icon.EYE[1]), icon.EYE[2] + edge, max(SLIT, icon.EYE[2] * openness) + edge)
    return hole


def smile():
    """웃는 눈: 위로 볼록한 호."""
    arc, box = QPainterPath(), QRectF(icon.EYE[0] - 6.5, icon.EYE[1] - 3.5, 13, 13)
    arc.arcMoveTo(box, 15)
    arc.arcTo(box, 15, 150)
    pen = QPainterPathStroker()
    pen.setWidth(4 + icon.ROUND)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    return pen.createStroke(arc)


class Mascot(QWidget):
    """한 변이 size 인 마스코트. 보이는 동안 몇 초마다 눈을 깜빡이고, set_happy(True) 면 웃는 눈이 됨."""

    def __init__(self, size, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.happy, self.open = False, 1.0
        self.timer = QTimer(self)
        self.timer.setInterval(BLINK_EVERY_MS)
        self.timer.timeout.connect(self.blink)

    def set_happy(self, happy):
        self.happy = happy
        self.update()

    def blink(self):
        if not self.happy:
            motion.play(self, motion.BLINK_MS, self._lid, curve=QEasingCurve.Type.Linear)

    def _lid(self, t):
        self.open = abs(1 - 2 * t)  # 감았다가 다시 뜸
        self.update()

    def showEvent(self, event):
        self.timer.start()

    def hideEvent(self, event):
        self.timer.stop()

    def paintEvent(self, event):
        start, end, ink = (QColor(value) for value in theme.BRAND)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.scale(self.width() / 120, self.height() / 120)  # 머리는 한 변 100, 위에 안테나, 양옆에 귀
        painter.setPen(QPen(end, 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(QPointF(60, 21), QPointF(60, 11))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(end)
        painter.drawEllipse(QPointF(60, 8), 6.5, 6.5)
        painter.setBrush(start)
        painter.drawRoundedRect(QRectF(2, 58, 12, 24), 4, 4)
        painter.setBrush(end)
        painter.drawRoundedRect(QRectF(106, 58, 12, 24), 4, 4)
        painter.translate(10, 20)
        icon.paint(painter, 100, smile() if self.happy else eye(self.open))
        if not self.happy:
            painter.setBrush(ink)
            painter.drawEllipse(QPointF(icon.PUPIL[0], icon.PUPIL[1]), icon.PUPIL[2], min(icon.PUPIL[2], icon.EYE[2] * self.open * 0.5))
