# -*- coding: utf-8 -*-
"""테마(시스템 · 밝게 · 어둡게) · 글꼴 · 색. 화면 코드는 색 값을 직접 적지 않고 color(토큰 이름)으로 꺼내 씀.
테마가 바뀌면 signals.changed 가 나옴. 직접 그리는 위젯과 HTML 을 만들어 넣는 화면은 이 신호를 받아 다시 그림."""
import os
import re
import sys

from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QFontDatabase, QPalette
from PyQt6.QtWidgets import QApplication

import mdlite

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")  # 같이 배포하는 나눔고딕
CLEAR_FONTS = ("NanumGothic", "Nanum Gothic", "Noto Sans KR", "Noto Sans CJK KR")  # 화면 글꼴로 먼저 씀
UI_FONTS = CLEAR_FONTS + ("Malgun Gothic", "Apple SD Gothic Neo")  # 한글이 있는 글꼴
CODE_FONTS = ("D2Coding", "Consolas", "Menlo", "Cascadia Mono", "DejaVu Sans Mono", "Courier New")
UI_PX = 15  # 버튼·목록·안내 글자 크기
CODE_PX = 16  # 편집기 글자 크기(확대 0 일 때)
DOC_PX = 2  # 문제 본문은 mdlite.CSS 의 크기에 이만큼 더함
ZOOM_RANGE = (-3, 10)

MODES = {"system": "시스템", "light": "밝게", "dark": "어둡게"}  # 홈의 단추를 누르면 이 순서로 돎
BRAND = ("#2f6bff", "#7b5cff", "#ffffff")  # 아이콘의 바탕 그라데이션 두 색과 글자 색. 테마가 바뀌어도 같음
AVATARS = ("#2a62f0", "#6d4df2", "#0b7f6a", "#b4530a", "#b83280", "#0e7490")  # 팀 현황의 이니셜 원. 글자는 BRAND 의 글자 색

# 글자와 바탕의 대비는 4.5:1 이상으로 맞춤(tests/test_gui.py 의 ThemeTest 가 확인함)
LIGHT = {
    "bg": "#f4f5f7", "surface": "#ffffff", "surface_alt": "#f6f8fa", "hover": "#f0f3f6",
    "border": "#d0d7de", "border_strong": "#c8d1da", "line": "#eef0f3", "track": "#e6e9ed",
    "scroll": "#c4ccd4", "scroll_hover": "#a3adb8",
    "ink": "#1f2328", "heading": "#16233b", "muted": "#57606a", "placeholder": "#6e7781", "faint": "#8c959f",
    "primary": "#1f6feb", "primary_hover": "#1a5fd0", "primary_ink": "#ffffff", "primary_off": "#9bbcf2", "primary_off_ink": "#ffffff",
    "selection": "#dbe9ff", "selection_ink": "#0b3d91", "text_selection": "#b6d4fe",
    "notice_bg": "#fff8e1", "notice_border": "#f0d98c",
    "code_bg": "#eef0f3", "codebox_bg": "#f3f4f6", "table_head": "#eaeef2", "grid": "#c8d1da",
    "doc_heading": "#0b3d91", "link": "#0969da",
    "ok": "#1a7f37", "wrong": "#cf222e", "blank": "#6e7781", "up": "#0969da", "retry": "#bc4c00",
    "unit_mastered": "#1f883d", "unit_mastered_ink": "#ffffff", "unit_level2": "#9cd0ff", "unit_level2_ink": "#1f2328",
    "unit_level1": "#f5d776", "unit_level1_ink": "#1f2328", "unit_retry": "#f0883e", "unit_retry_ink": "#1f2328",
    "unit_none": "#e1e5ea", "unit_none_ink": "#57606a", "unit_none_edge": "#848d97",
}
DARK = {
    "bg": "#0f1318", "surface": "#171c23", "surface_alt": "#1c222b", "hover": "#222a34",
    "border": "#2b323c", "border_strong": "#3a434f", "line": "#222933", "track": "#2b323c",
    "scroll": "#3a434f", "scroll_hover": "#4d5866",
    "ink": "#e6ebf2", "heading": "#f3f6fa", "muted": "#9aa5b1", "placeholder": "#8b949e", "faint": "#6b7684",
    "primary": "#5b8cff", "primary_hover": "#7aa2ff", "primary_ink": "#0b1220", "primary_off": "#2b3d66", "primary_off_ink": "#8fa0c0",
    "selection": "#1d3156", "selection_ink": "#cfe0ff", "text_selection": "#2c4a80",
    "notice_bg": "#2a2413", "notice_border": "#5f4d17",
    "code_bg": "#252c36", "codebox_bg": "#11161c", "table_head": "#1f2630", "grid": "#3a434f",
    "doc_heading": "#8fb4ff", "link": "#6ea8ff",
    "ok": "#3fb950", "wrong": "#ff7b72", "blank": "#8b949e", "up": "#6ea8ff", "retry": "#f0883e",
    "unit_mastered": "#2ea043", "unit_mastered_ink": "#06120a", "unit_level2": "#58a6ff", "unit_level2_ink": "#0b1220",
    "unit_level1": "#d9b44a", "unit_level1_ink": "#0b1220", "unit_retry": "#e2673a", "unit_retry_ink": "#0b1220",
    "unit_none": "#2b323c", "unit_none_ink": "#9aa5b1", "unit_none_edge": "#6b7684",
}
TOKENS = {"light": LIGHT, "dark": DARK}

# 채점 결과와 판정: (이름, 토큰). 토큰 이름은 본문 CSS 의 클래스 이름(.ok, .wrong ...)으로도 씀
RESULT = {"ok": ("정답", "ok"), "wrong": ("오답", "wrong"), "blank": ("미응답", "blank")}
VERDICT = {"up": ("진급", "up"), "mastered": ("숙달", "ok"), "done": ("숙달", "ok"), "keep": ("유지", "muted"), "retry": ("재도전", "retry")}
UNIT = {"mastered": "숙달", "level2": "레벨2 진행", "level1": "레벨1 진행", "retry": "재도전", "none": "미진단"}  # 단원 띠. 색은 unit_<상태>, unit_<상태>_ink


def result_label(state):
    """채점 결과를 (이름, 토큰)으로 바꿈. 기록에 남은 skipped·None 은 미응답으로 봄."""
    return RESULT.get(state, RESULT["blank"])


class Signals(QObject):
    changed = pyqtSignal()  # 밝기가 바뀌어 색을 다시 칠한 뒤에 나옴


signals = Signals()
state = {"mode": "system", "scheme": "light"}  # 고른 값(MODES 의 키)과 지금 칠한 밝기(light · dark)


def color(name):
    """지금 테마에서 토큰의 색 값(#rrggbb)."""
    return TOKENS[state["scheme"]][name]


def qcolor(name):
    return QColor(color(name))


STYLE = """
QMainWindow, QDialog, QWidget#page, QScrollArea { background: %(bg)s; }
QLabel { color: %(ink)s; }
QLabel#h1 { font-size: 21px; font-weight: 700; color: %(heading)s; }
QLabel#h2 { font-size: 17px; font-weight: 700; color: %(heading)s; }
QLabel#muted { color: %(muted)s; }
QLabel#big { font-size: 46px; font-weight: 700; color: %(heading)s; }
QLabel#ready { font-size: 26px; font-weight: 700; color: %(heading)s; }
QLabel#me { background: %(primary)s; color: %(primary_ink)s; border-radius: 9px; padding: 1px 8px; font-size: 12px; font-weight: 700; }
QLabel#error { color: %(wrong)s; }
QLabel#warn { color: %(retry)s; }
QLabel#notice { background: %(notice_bg)s; color: %(ink)s; border: 1px solid %(notice_border)s; border-radius: 6px; padding: 8px 12px; }
QFrame#card { background: %(surface)s; border: 1px solid %(border)s; border-radius: 8px; }
QFrame#card[me="true"] { border-color: %(primary)s; }
QFrame#bar { background: %(surface)s; border-top: 1px solid %(border)s; }
QListWidget { background: %(surface)s; color: %(ink)s; border: 1px solid %(border)s; border-radius: 6px; outline: 0; }
QListWidget#plain { border: 0; }
QListWidget::item { padding: 7px 10px; border-bottom: 1px solid %(line)s; }
QListWidget::item:hover { background: %(hover)s; }
QListWidget::item:selected { background: %(selection)s; color: %(selection_ink)s; }
QTextBrowser, QPlainTextEdit, QLineEdit { background: %(surface)s; color: %(ink)s; border: 1px solid %(border)s; border-radius: 6px;
    selection-background-color: %(text_selection)s; selection-color: %(ink)s; placeholder-text-color: %(placeholder)s; }
QPlainTextEdit:focus, QLineEdit:focus { border-color: %(primary)s; }
QPlainTextEdit:disabled, QLineEdit:disabled { background: %(surface_alt)s; }
QLineEdit { padding: 6px 8px; }
QPushButton { background: %(surface)s; color: %(ink)s; border: 1px solid %(border_strong)s; border-radius: 6px; padding: 7px 16px; }
QPushButton:hover { background: %(hover)s; }
QPushButton:pressed { background: %(track)s; }
QPushButton:disabled { color: %(faint)s; background: %(bg)s; }
QPushButton#primary { background: %(primary)s; color: %(primary_ink)s; border: 1px solid %(primary_hover)s; font-weight: 700; }
QPushButton#primary:hover, QPushButton#primary:pressed { background: %(primary_hover)s; }
QPushButton#primary:disabled { background: %(primary_off)s; border-color: %(primary_off)s; color: %(primary_off_ink)s; }
QPushButton#primary[big="true"] { font-size: 18px; }
QPushButton#quiet { background: transparent; color: %(muted)s; border: 1px solid %(border)s; padding: 4px 12px; }
QPushButton#quiet:hover { background: %(hover)s; color: %(ink)s; }
QProgressBar { background: %(track)s; border: 0; border-radius: 5px; max-height: 10px; min-height: 10px; }
QProgressBar::chunk { background: %(primary)s; border-radius: 5px; }
QToolTip { background: %(surface)s; color: %(ink)s; border: 1px solid %(border_strong)s; padding: 4px 6px; }
QSplitter::handle { background: %(bg)s; }
QMenu { background: %(surface)s; color: %(ink)s; border: 1px solid %(border_strong)s; padding: 4px; }
QMenu::item { padding: 5px 22px; border-radius: 4px; }
QMenu::item:selected { background: %(selection)s; color: %(selection_ink)s; }
QMenu::item:disabled { color: %(faint)s; }
QMenu::separator { height: 1px; background: %(line)s; margin: 4px 6px; }
QScrollBar { background: transparent; border: 0; }
QScrollBar:vertical { width: 14px; margin: 3px; }
QScrollBar:horizontal { height: 14px; margin: 3px; }
QScrollBar::handle { background: %(scroll)s; border-radius: 4px; }
QScrollBar::handle:vertical { min-height: 28px; }
QScrollBar::handle:horizontal { min-width: 28px; }
QScrollBar::handle:hover { background: %(scroll_hover)s; }
QScrollBar::add-line, QScrollBar::sub-line { width: 0; height: 0; }
QScrollBar::add-page, QScrollBar::sub-page { background: transparent; }
QAbstractScrollArea::corner { background: transparent; border: 0; }
"""
STYLE += "".join("QLabel#unit_%s { background: %%(unit_%s)s; color: %%(unit_%s_ink)s; border-radius: 4px; font-weight: 700; }\n" % (name, name, name)
                 for name in UNIT)
STYLE += "QLabel#unit_none { border: 1px solid %(unit_none_edge)s; }\n"  # 미진단 칸은 바탕과 색이 비슷해 테두리로 구분함

# 본문 CSS(mdlite.CSS)에 화면이 더하는 것: 결과·판정 글자색과 결과 화면의 구역 띠
DOC_CSS = """
.muted { color: %(muted)s; }
.ok { color: %(ok)s; }
.wrong { color: %(wrong)s; }
.blank { color: %(blank)s; }
.up { color: %(up)s; }
.retry { color: %(retry)s; }
td.band { background-color: %(table_head)s; }
"""

_fonts = {}


def _installed(names):
    if "all" not in _fonts:
        _fonts["all"] = set(QFontDatabase.families())
    return [name for name in names if name in _fonts["all"]]


def system_scheme():
    """운영체제가 어두운 모드면 dark, 아니거나 알 수 없으면(Qt 6.5 미만 포함) light."""
    hints = QApplication.instance().styleHints()
    return "dark" if hasattr(hints, "colorScheme") and hints.colorScheme() == Qt.ColorScheme.Dark else "light"


def apply(app, mode="system"):
    """시작할 때 한 번 부름. 글꼴과 스타일을 정하고 mode 의 테마를 칠함."""
    app.setStyle("Fusion")
    for name in sorted(os.listdir(FONT_DIR)) if os.path.isdir(FONT_DIR) else []:  # 어느 컴퓨터에서나 같은 글꼴로 보이게 등록함
        if name.endswith(".ttf"):
            QFontDatabase.addApplicationFont(os.path.join(FONT_DIR, name))
    _fonts.clear()
    family = _installed(CLEAR_FONTS) or (_installed(("Malgun Gothic",)) if sys.platform == "win32" else [])
    font = app.font()
    if family:  # 또렷한 글꼴이 있으면 그것을 쓰고, Windows 에서는 굴림 대신 맑은 고딕을 씀
        font.setFamily(family[0])
    font.setPixelSize(UI_PX)
    app.setFont(font)
    hints = app.styleHints()
    if hasattr(hints, "colorSchemeChanged"):  # Qt 6.5 이상. 시스템을 따르는 동안 운영체제 설정이 바뀌면 따라감
        hints.colorSchemeChanged.connect(_follow_system)
    set_mode(mode, force=True)


def set_mode(mode, force=False):
    """테마를 고름(MODES 의 키, 모르는 값은 system). 밝기가 달라지면 창 전체를 다시 칠하고 signals.changed 를 냄."""
    state["mode"] = mode = mode if mode in MODES else "system"
    hints = QApplication.instance().styleHints()
    if hasattr(hints, "setColorScheme"):  # Qt 6.8 이상. 제목 표시줄처럼 운영체제가 그리는 부분도 맞춤
        if mode == "system":
            hints.unsetColorScheme()
        else:
            hints.setColorScheme(Qt.ColorScheme.Dark if mode == "dark" else Qt.ColorScheme.Light)
    scheme = system_scheme() if mode == "system" else mode
    if force or scheme != state["scheme"]:
        _paint(scheme)


def _follow_system(*_):
    if state["mode"] == "system" and system_scheme() != state["scheme"]:
        _paint(system_scheme())


def _paint(scheme):
    state["scheme"] = scheme
    app = QApplication.instance()
    palette = QPalette(qcolor("surface"), qcolor("bg"))  # 버튼 색과 창 색을 주면 나머지 음영은 Qt 가 계산함
    role = QPalette.ColorRole
    for part, name in ((role.Window, "bg"), (role.WindowText, "ink"), (role.Base, "surface"), (role.AlternateBase, "surface_alt"),
                       (role.Text, "ink"), (role.Button, "surface"), (role.ButtonText, "ink"), (role.Highlight, "text_selection"),
                       (role.HighlightedText, "ink"), (role.PlaceholderText, "placeholder"), (role.ToolTipBase, "surface"),
                       (role.ToolTipText, "ink"), (role.Link, "link")):
        palette.setColor(part, qcolor(name))
    app.setPalette(palette)
    app.setStyleSheet(STYLE % TOKENS[scheme])
    signals.changed.emit()


def code_families():
    """고정폭 글꼴 하나와 한글 대체 글꼴. 플랫폼 기본 고정폭이 실제로는 고정폭이 아닌 환경이 있어 설치된 글꼴에서 이름으로 고름."""
    mono = _installed(CODE_FONTS)[:1] or [QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont).family()]
    return mono + _installed(UI_FONTS)[:1]


def code_font(zoom=0):
    font = QFont()
    font.setFamilies(code_families())
    font.setStyleHint(QFont.StyleHint.Monospace)
    font.setFixedPitch(True)
    font.setPixelSize(CODE_PX + zoom)
    return font


def doc_css(zoom=0):
    """문제 본문용 CSS. 지금 테마의 색을 채우고, 글자 크기를 확대 단계만큼 키우고, 코드 글꼴을 설치된 글꼴로 바꿈."""
    css = (mdlite.CSS + DOC_CSS) % TOKENS[state["scheme"]]
    css = re.sub(r"font-size: (\d+)px", lambda m: "font-size: %dpx" % (int(m.group(1)) + DOC_PX + zoom), css)
    families = ", ".join("'%s'" % name for name in code_families())
    return re.sub(r"font-family: [^;]+;", "font-family: %s;" % families, css)
