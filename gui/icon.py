# -*- coding: utf-8 -*-
"""프로그램 아이콘. 그림 파일과 글꼴 없이 QPainter 로 그림: 둥근 사각형 바탕에 굵은 R, R 의 둥근 부분은 로봇 눈.
docs/img/icon.png 를 다시 만들 때: python -m gui.icon docs/img/icon.png"""
import sys

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QIcon, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap, QPolygonF

from gui import theme

# 좌표는 한 변이 100 인 칸 기준
EYE = (55.0, 39.0, 8.5)  # 눈(R 의 둥근 부분에 뚫린 구멍)의 중심과 반지름
PUPIL = (56.0, 38.0, 3.4)  # 눈동자
ROUND = 3.0  # 글자 모서리를 둥글리는 테두리 굵기
SIZES = (16, 20, 24, 32, 40, 48, 64, 128, 256)
APP_ID = "rokey.python.study"


def letter(hole=None):
    """R 의 윤곽. ROUND 굵기의 테두리를 함께 칠하면 EYE 크기의 구멍이 남음. hole 을 주면 눈 자리에 그 모양을 대신 뚫음."""
    edge = ROUND / 2
    stem = QPainterPath()
    stem.addRect(QRectF(28.5, 22.5, 13, 55))
    bowl = QPainterPath(QPointF(28.5, 22.5))
    bowl.lineTo(55, 22.5)
    bowl.arcTo(QRectF(38.5, 22.5, 33, 33), 90, -180)
    bowl.lineTo(28.5, 55.5)
    bowl.closeSubpath()
    leg = QPainterPath()
    leg.addPolygon(QPolygonF([QPointF(47, 54), QPointF(59.5, 54), QPointF(76.5, 77.5), QPointF(64, 77.5)]))
    leg.closeSubpath()
    if hole is None:
        hole = QPainterPath()
        hole.addEllipse(QPointF(EYE[0], EYE[1]), EYE[2] + edge, EYE[2] + edge)
    return stem.united(bowl).united(leg).subtracted(hole)


def paint(painter, size, hole=None):
    """(0, 0) 에서 한 변이 size 인 자리에 아이콘을 그림. hole 을 주면 눈을 그 모양으로 뚫고 눈동자는 그리지 않음(마스코트의 표정)."""
    start, end, ink = (QColor(value) for value in theme.BRAND)
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.scale(size / 100, size / 100)
    back = QLinearGradient(0, 0, 100, 100)
    back.setColorAt(0, start)
    back.setColorAt(1, end)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(back)
    painter.drawRoundedRect(QRectF(0, 0, 100, 100), 23, 23)
    painter.setBrush(ink)
    painter.setPen(QPen(ink, ROUND, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
    painter.drawPath(letter(hole))
    if hole is None and size >= 32:  # 더 작으면 눈동자가 구멍을 메워 R 로 읽히지 않음
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(PUPIL[0], PUPIL[1]), PUPIL[2], PUPIL[2])
    painter.restore()


def pixmap(size):
    image = QPixmap(size, size)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    paint(painter, size)
    painter.end()
    return image


def install(app):
    """창과 앱의 아이콘을 정함. Windows 에서는 작업 표시줄이 파이썬 아이콘으로 묶지 않게 앱 ID 도 줌."""
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
        except (AttributeError, OSError):
            pass
    icon = QIcon()
    for size in SIZES:
        icon.addPixmap(pixmap(size))
    app.setWindowIcon(icon)


if __name__ == "__main__":
    from PyQt6.QtGui import QGuiApplication

    app = QGuiApplication(sys.argv[:1])
    pixmap(256).save(sys.argv[1])
