# -*- coding: utf-8 -*-
"""움직임: 화면 전환 페이드, 숫자·막대가 올라가는 도우미, 색종이. 입력·저장·채점을 기다리게 하지 않음.
enabled 를 False 로 두면 모든 움직임이 곧바로 끝 상태가 됨(테스트와 스크린샷에서 씀)."""
import math
import random

from PyQt6.QtCore import QEasingCurve, QEvent, QRectF, Qt, QVariantAnimation
from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import QWidget

from gui import theme

enabled = True
FADE_MS = 180  # 화면 전환
COUNT_MS = 500  # 숫자와 막대. 감속이라 400ms 쯤이면 끝 값에 닿음
CHECK_MS = 140  # 보기 카드의 체크 표시
BLINK_MS = 160  # 마스코트가 눈을 감았다 뜨는 시간
CONFETTI_MS = 1500
CONFETTI_PIECES = 90
CONFETTI_COLORS = ("primary", "unit_mastered", "unit_level1", "unit_level2", "unit_retry")


def play(owner, ms, step, done=None, curve=QEasingCurve.Type.OutCubic):
    """owner 에 딸린 애니메이션 하나를 돌림. 진행도 0~1 로 step 을 부르고 끝나면 done 을 부름.
    owner 에서 먼저 돌던 것은 멈추고(그쪽 done 은 부르지 않음), 꺼져 있거나 ms 가 0 이면 step(1.0) 과 done 을 바로 부름."""
    running = getattr(owner, "_motion", None)
    if running is not None:
        running.stop()
        running.deleteLater()
    owner._motion = None
    if not enabled or ms <= 0:
        step(1.0)
        if done:
            done()
        return

    def finish():
        owner._motion = None
        anim.deleteLater()
        if done:
            done()

    anim = owner._motion = QVariantAnimation(owner)
    anim.setStartValue(0.0)
    anim.setEndValue(1.0)
    anim.setDuration(ms)
    anim.setEasingCurve(curve)
    anim.valueChanged.connect(step)
    anim.finished.connect(finish)
    anim.start()


def count(owner, end, show, ms=COUNT_MS):
    """show(정수)를 0 부터 end 까지 올려 가며 부름. 막대는 count(bar, 값, bar.setValue) 로 씀."""
    play(owner, ms if end else 0, lambda t: show(round(end * t)))


def count_text(label, form, end, ms=COUNT_MS):
    """label 의 글자를 form % 0 부터 form % end 까지 올림. 끝 글자의 폭을 먼저 잡아 두어 옆 위젯이 밀리지 않음."""
    label.setMinimumWidth(0)
    label.setText(form % end)
    if enabled and end:
        label.ensurePolished()
        label.setMinimumWidth(label.sizeHint().width())
    count(label, end, lambda n: label.setText(form % n), ms)


class Cover(QWidget):
    """바뀌기 전 모습을 찍은 그림. 부모 위에 덮여 투명해지며, 마우스는 통과시키고 포커스를 받지 않음."""

    def __init__(self, parent, shot):
        super().__init__(parent)
        self.shot, self.alpha = shot, 1.0
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setGeometry(parent.rect())
        self.raise_()
        self.show()

    def fade(self, t):
        self.alpha = 1.0 - t
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setOpacity(self.alpha)
        painter.drawPixmap(0, 0, self.shot)


def fade_over(widget, change, ms=FADE_MS):
    """change() 로 바뀌기 전 모습을 widget 위에 덮었다가 걷어 냄. 그림만 투명해지고 아래 위젯은 바로 쓸 수 있음."""
    if not (enabled and widget.isVisible()):
        change()
        return
    shot = widget.grab()
    for old in widget.findChildren(Cover, options=Qt.FindChildOption.FindDirectChildrenOnly):
        old.deleteLater()
    change()
    cover = Cover(widget, shot)
    play(cover, ms, cover.fade, cover.deleteLater)


def switch(stack, page):
    """QStackedWidget 의 화면을 page 로 바꾸며 페이드함."""
    if stack.currentWidget() is page:
        return
    fade_over(stack, lambda: stack.setCurrentWidget(page))


class Confetti(QWidget):
    """부모 위에서 떨어지는 색종이. 마우스는 통과시키고 포커스를 받지 않으며, 부모의 크기가 바뀌면 따라감."""

    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.time = 0.0
        rng = random.Random()
        self.pieces = [{"x": rng.random(), "wait": rng.uniform(0, 0.35), "speed": rng.uniform(0.9, 1.5), "sway": rng.uniform(8, 26),
                        "turn": rng.uniform(-3, 3), "phase": rng.uniform(0, math.tau), "size": rng.uniform(7, 12),
                        "color": rng.choice(CONFETTI_COLORS)} for _ in range(CONFETTI_PIECES)]
        parent.installEventFilter(self)
        self.setGeometry(parent.rect())
        self.raise_()
        self.show()

    def eventFilter(self, target, event):
        if event.type() == QEvent.Type.Resize:
            self.setGeometry(target.rect())
        return False

    def fall(self, t):
        self.time = t
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setOpacity(min(1.0, (1.0 - self.time) / 0.2))  # 끝나기 전에 옅어짐
        for piece in self.pieces:
            fallen = (self.time - piece["wait"]) * piece["speed"]
            if fallen <= 0:
                continue
            angle = piece["phase"] + piece["turn"] * math.tau * self.time
            painter.save()
            painter.translate(piece["x"] * self.width() + piece["sway"] * math.sin(angle), fallen * (self.height() + 40) - 20)
            painter.rotate(math.degrees(angle))
            painter.setBrush(theme.qcolor(piece["color"]))
            painter.drawRect(QRectF(-piece["size"] / 2, -piece["size"] / 4, piece["size"], piece["size"] / 2))
            painter.restore()


def clear_confetti(parent):
    """parent 위에서 떨어지던 색종이를 지움."""
    for old in parent.findChildren(Confetti, options=Qt.FindChildOption.FindDirectChildrenOnly):
        old.hide()
        old.deleteLater()


def confetti(parent):
    """parent 위에 색종이를 CONFETTI_MS 동안 떨어뜨리고 스스로 지움. 움직임이 꺼져 있으면 아무것도 만들지 않음."""
    if not enabled:
        return None
    clear_confetti(parent)
    paper = Confetti(parent)
    play(paper, CONFETTI_MS, paper.fall, paper.deleteLater, QEasingCurve.Type.Linear)
    return paper
