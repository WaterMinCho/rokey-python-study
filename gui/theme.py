# -*- coding: utf-8 -*-
"""밝은 테마 · 글꼴 · 색. 운영체제가 다크 모드여도 시험 화면처럼 밝게 고정한다."""
import re
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QFontDatabase, QPalette

import mdlite

UI_FONTS = ("Malgun Gothic", "Apple SD Gothic Neo", "Noto Sans CJK KR", "NanumGothic")  # 한글이 있는 글꼴
CODE_FONTS = ("D2Coding", "Consolas", "Menlo", "Cascadia Mono", "DejaVu Sans Mono", "Courier New")
CODE_PX = 14  # 편집기 글자 크기(확대 0 일 때)
ZOOM_RANGE = (-3, 10)

INK, MUTED, GREEN, RED, ORANGE, BLUE, GRAY = "#1f2328", "#57606a", "#1a7f37", "#cf222e", "#bc4c00", "#0969da", "#6e7781"
RESULT = {"ok": ("정답", GREEN), "wrong": ("오답", RED), "blank": ("미응답", GRAY)}


def result_label(state):
    """채점 결과(ok·wrong·blank, 기록에는 skipped·None 도 있다) → (이름, 색)."""
    return RESULT.get(state, RESULT["blank"])


VERDICT = {"up": ("진급", BLUE), "mastered": ("숙달", GREEN), "done": ("숙달", GREEN), "keep": ("유지", MUTED), "retry": ("재도전", ORANGE)}
# 단원 띠: (이름, 배경, 글자)
UNIT = {"mastered": ("숙달", "#2da44e", "#ffffff"), "level2": ("레벨2 진행", "#9cd0ff", INK), "level1": ("레벨1 진행", "#f5d776", INK),
        "retry": ("재도전", "#f0883e", "#ffffff"), "none": ("미진단", "#e1e5ea", MUTED)}

STYLE = """
QMainWindow, QDialog, QWidget#page, QScrollArea { background: #f4f5f7; }
QLabel { color: #1f2328; }
QLabel#h1 { font-size: 20px; font-weight: 700; color: #16233b; }
QLabel#h2 { font-size: 15px; font-weight: 700; color: #16233b; }
QLabel#muted { color: #57606a; }
QLabel#big { font-size: 46px; font-weight: 700; color: #16233b; }
QLabel#error { color: #cf222e; }
QLabel#notice { background: #fff8e1; color: #1f2328; border: 1px solid #f0d98c; border-radius: 6px; padding: 8px 12px; }
QFrame#card { background: #ffffff; border: 1px solid #d0d7de; border-radius: 8px; }
QFrame#bar { background: #ffffff; border-top: 1px solid #d0d7de; }
QListWidget { background: #ffffff; border: 1px solid #d0d7de; border-radius: 6px; outline: 0; }
QListWidget#plain { border: 0; }
QListWidget::item { padding: 7px 10px; border-bottom: 1px solid #eef0f3; }
QListWidget::item:selected { background: #dbe9ff; color: #0b3d91; }
QTextBrowser, QPlainTextEdit, QLineEdit { background: #ffffff; color: #1f2328; border: 1px solid #d0d7de; border-radius: 6px;
    selection-background-color: #b6d4fe; selection-color: #1f2328; }
QPlainTextEdit:disabled, QLineEdit:disabled { background: #f6f8fa; }
QLineEdit { padding: 6px 8px; }
QPushButton { background: #ffffff; color: #1f2328; border: 1px solid #c8d1da; border-radius: 6px; padding: 7px 16px; }
QPushButton:hover { background: #f0f3f6; }
QPushButton:disabled { color: #a0a8b1; background: #f4f5f7; }
QPushButton#primary { background: #1f6feb; color: #ffffff; border: 1px solid #1a5fd0; font-weight: 700; }
QPushButton#primary:hover { background: #1a5fd0; }
QPushButton#primary:disabled { background: #9bbcf2; border-color: #9bbcf2; color: #ffffff; }
QPushButton#primary[big="true"] { font-size: 17px; }
QPushButton#choice { font-size: 17px; font-weight: 700; min-height: 46px; text-align: left; padding-left: 18px; }
QPushButton#choice:checked { background: #1f6feb; color: #ffffff; border-color: #1a5fd0; }
QPushButton#choice:checked:disabled { background: #9bbcf2; border-color: #9bbcf2; }
QProgressBar { background: #e6e9ed; border: 0; border-radius: 5px; max-height: 10px; min-height: 10px; }
QProgressBar::chunk { background: #1f6feb; border-radius: 5px; }
QToolTip { background: #ffffff; color: #1f2328; border: 1px solid #c8d1da; padding: 4px 6px; }
QSplitter::handle { background: #f4f5f7; }
"""

STYLE += "".join("QLabel#unit_%s { background: %s; color: %s; border-radius: 4px; font-weight: 700; }\n" % (state, back, ink)
                 for state, (_, back, ink) in UNIT.items())

_fonts = {}


def _installed(names):
    if "all" not in _fonts:
        _fonts["all"] = set(QFontDatabase.families())
    return [name for name in names if name in _fonts["all"]]


def apply(app):
    app.setStyle("Fusion")
    hints = app.styleHints()
    if hasattr(hints, "setColorScheme"):  # Qt 6.8 이상
        hints.setColorScheme(Qt.ColorScheme.Light)
    palette = QPalette()
    for role, color in ((QPalette.ColorRole.Window, "#f4f5f7"), (QPalette.ColorRole.WindowText, INK),
                        (QPalette.ColorRole.Base, "#ffffff"), (QPalette.ColorRole.AlternateBase, "#f6f8fa"),
                        (QPalette.ColorRole.Text, INK), (QPalette.ColorRole.Button, "#ffffff"),
                        (QPalette.ColorRole.ButtonText, INK), (QPalette.ColorRole.Highlight, "#b6d4fe"),
                        (QPalette.ColorRole.HighlightedText, INK), (QPalette.ColorRole.PlaceholderText, "#8c959f"),
                        (QPalette.ColorRole.ToolTipBase, "#ffffff"), (QPalette.ColorRole.ToolTipText, INK),
                        (QPalette.ColorRole.Link, BLUE)):
        palette.setColor(role, QColor(color))
    app.setPalette(palette)
    if sys.platform == "win32" and _installed(("Malgun Gothic",)):  # 굴림이 없는 Windows 에서 한글이 네모로 나오지 않게
        font = app.font()
        font.setFamily("Malgun Gothic")
        app.setFont(font)
    app.setStyleSheet(STYLE)


def code_families():
    """고정폭 글꼴 하나 + 한글 대체 글꼴. 플랫폼 기본 고정폭이 고정폭이 아닌 환경이 있어 설치된 것 중에서 이름으로 고른다."""
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
    """문제 본문용 CSS: mdlite.CSS 의 글자 크기를 확대 단계만큼 키우고 코드 글꼴을 설치된 글꼴로 바꾼다."""
    css = re.sub(r"font-size: (\d+)px", lambda m: "font-size: %dpx" % (int(m.group(1)) + zoom), mdlite.CSS)
    families = ", ".join("'%s'" % name for name in code_families())
    return re.sub(r"font-family: [^;]+;", "font-family: %s;" % families, css)
