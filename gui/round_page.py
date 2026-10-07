# -*- coding: utf-8 -*-
"""회차 화면: 왼쪽 문항 목록 · 가운데 문제 · 오른쪽 답안 · 아래 실행과 제출."""
import datetime
import html
import textwrap

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QGuiApplication, QTextCursor
from PyQt6.QtWidgets import (QFrame, QHBoxLayout, QLabel, QListWidget, QProgressBar, QPushButton, QSplitter, QStackedWidget,
                             QTextBrowser, QVBoxLayout, QWidget)

import mdlite
import study
from gui import theme
from gui.widgets import ChoicePanel, CodePanel, TextPanel
from session import SessionError

SAVE_DELAY_MS = 400  # 입력이 멈춘 뒤 자동 저장까지


def split_input(text):
    """study 가 만든 입력 표시('입력:\\n    3', '테스트 코드:\\n    f()', 'f(1)')를 (이름, 내용)으로 나눈다."""
    for head in ("입력", "테스트 코드"):
        if text.startswith(head + ":"):
            return head, textwrap.dedent(text[len(head) + 1:].strip("\n")).strip()
    return "호출", text


def run_html(run):
    """'코드 실행' 결과(session.try_run)를 예시별 표로 그린다."""
    note = '<span style="color:%s;">예시만 실행하며 기록되지 않습니다.</span>' % theme.MUTED
    cases = run["cases"]
    if cases:
        parts = ["<p><b>예시 %d개 중 %d개 통과</b> · %s</p>" % (len(cases), sum(1 for case in cases if case["ok"]), note)]
    else:
        parts = ["<p>%s</p>" % note]
    if run["message"]:
        parts.append('<p style="color:%s; white-space:pre-wrap;"><b>%s</b></p>' % (theme.RED, html.escape(run["message"], quote=False)))
    elif not cases:
        parts.append("<p>실행 결과가 없습니다.</p>")
    for number, case in enumerate(cases, 1):
        head, body = split_input(case["input"])
        value = "반환값" if head == "호출" else "출력"
        label, color = ("통과", theme.GREEN) if case["ok"] else ("실패", theme.RED)
        rows = [(head, body), ("기대한 " + value, case["want"]), ("실제 " + value, case["got"])]
        if case["printed"]:
            rows.append(("함수 안 출력", case["printed"]))
        parts.append('<p><b>예시 %d · <span style="color:%s;">%s</span></b></p>' % (number, color, label))
        parts.append('<table class="grid" border="1" cellspacing="0" cellpadding="4">%s</table>' % "".join(
            '<tr><th align="left">%s</th><td><pre>%s</pre></td></tr>' % (name, html.escape(text, quote=False)) for name, text in rows))
    return "<body>%s</body>" % "".join(parts)


class RoundPage(QWidget):
    def __init__(self, win):
        super().__init__()
        self.setObjectName("page")
        self.win = win
        self.view, self.current, self.review = None, None, False
        self.dirty = {}  # 아직 파일에 쓰지 않은 답 {문항 ID: 값}

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 0)
        head = QHBoxLayout()
        self.home_btn = QPushButton("홈으로")
        self.title = QLabel()
        self.title.setObjectName("h1")
        self.progress = QLabel()
        self.progress.setObjectName("muted")
        self.back_btn = QPushButton("결과로 돌아가기")
        head.addWidget(self.home_btn)
        head.addSpacing(8)
        head.addWidget(self.title)
        head.addStretch(1)
        head.addWidget(self.progress)
        head.addWidget(self.back_btn)
        root.addLayout(head)
        self.banner = QLabel("연습입니다. 숙달 판정에는 첫 제출만 반영됩니다. 고친 뒤 '다시 채점'을 누르면 점수만 다시 계산합니다.")
        self.banner.setObjectName("notice")
        root.addWidget(self.banner)

        split = QSplitter(Qt.Orientation.Horizontal)
        self.listw = QListWidget()
        self.listw.setMinimumWidth(200)
        self.listw.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        mid = QWidget()
        mid_box = QVBoxLayout(mid)
        mid_box.setContentsMargins(0, 0, 0, 0)
        self.item_title = QLabel()
        self.item_title.setObjectName("h2")
        self.item_title.setWordWrap(True)
        self.body = QTextBrowser()
        self.body.setOpenLinks(False)
        self.body.document().setDocumentMargin(14)
        mid_box.addWidget(self.item_title)
        mid_box.addWidget(self.body, 1)
        right = QWidget()
        right_box = QVBoxLayout(right)
        right_box.setContentsMargins(0, 0, 0, 0)
        self.pane_title = QLabel("답안")
        self.pane_title.setObjectName("h2")
        self.stack = QStackedWidget()
        self.choice_panel, self.text_panel, self.code_panel = ChoicePanel(), TextPanel(), CodePanel()
        for panel in (self.choice_panel, self.text_panel, self.code_panel):
            self.stack.addWidget(panel)
            panel.changed.connect(self.on_answer_changed)
        right_box.addWidget(self.pane_title)
        right_box.addWidget(self.stack, 1)
        for widget in (self.listw, mid, right):
            split.addWidget(widget)
        split.setStretchFactor(0, 0)
        split.setStretchFactor(1, 5)
        split.setStretchFactor(2, 4)
        split.setSizes([225, 555, 475])
        split.setChildrenCollapsible(False)
        root.addWidget(split, 1)

        bar = QFrame()
        bar.setObjectName("bar")
        bar_box = QHBoxLayout(bar)
        bar_box.setContentsMargins(4, 8, 4, 8)
        self.prev_btn = QPushButton("이전")
        self.next_btn = QPushButton("다음")
        self.status = QLabel("")
        self.status.setObjectName("muted")
        self.busy_bar = QProgressBar()
        self.busy_bar.setRange(0, 0)  # 끝을 모르는 진행 표시
        self.busy_bar.setTextVisible(False)
        self.busy_bar.setFixedWidth(140)
        self.busy_bar.hide()
        self.run_btn = QPushButton("코드 실행")
        self.submit_btn = QPushButton("회차 제출")
        self.submit_btn.setObjectName("primary")
        bar_box.addWidget(self.prev_btn)
        bar_box.addWidget(self.next_btn)
        bar_box.addSpacing(8)
        bar_box.addWidget(self.status, 1)
        bar_box.addWidget(self.busy_bar)
        bar_box.addWidget(self.run_btn)
        bar_box.addWidget(self.submit_btn)
        root.addWidget(bar)

        self.save_timer = QTimer(self)
        self.save_timer.setSingleShot(True)
        self.save_timer.setInterval(SAVE_DELAY_MS)
        self.save_timer.timeout.connect(lambda: self.flush(commit=False))  # 타이머로는 조합 중인 한글을 끊지 않는다
        self.listw.currentRowChanged.connect(self.show_item)
        self.prev_btn.clicked.connect(lambda: self.listw.setCurrentRow(self.listw.currentRow() - 1))
        self.next_btn.clicked.connect(lambda: self.listw.setCurrentRow(self.listw.currentRow() + 1))
        self.run_btn.clicked.connect(self.run_code)
        self.submit_btn.clicked.connect(self.submit)
        self.code_panel.reset_btn.clicked.connect(self.ask_reset)
        self.home_btn.clicked.connect(win.go_home)
        self.back_btn.clicked.connect(lambda: win.show_result(self.view["id"]))

    # ── 불러오기 ──

    def load(self, rid, review=False, select=None):
        """회차를 화면에 올린다. 답안지를 읽을 수 없으면 SessionError 를 올리고 화면은 그대로 둔다."""
        if self.view:
            self.flush()  # 앞에 보던 회차에 남은 입력부터 저장
        view = self.win.session.open_round(rid)
        self.dirty.clear()
        self.view, self.review, self.current = view, review, None
        self.title.setText(view["title"] + (" · 다시 풀기" if review else ""))
        self.banner.setVisible(review)
        self.back_btn.setVisible(review)
        self.submit_btn.setText("다시 채점" if review else "회차 제출")
        self.status.setText("")
        row = next((n for n, item in enumerate(view["items"]) if item["id"] == select), 0)
        self.listw.blockSignals(True)
        self.listw.clear()
        for item in view["items"]:
            self.listw.addItem(self._row_text(item))
        self.listw.setCurrentRow(row)
        self.listw.blockSignals(False)
        self._update_progress()
        self.show_item(row)

    def _row_text(self, item):
        if self.review:
            state = theme.result_label(item["result"])[0]
        else:
            state = "작성함" if item["answered"] else "안 풂"
        return "%s %d. %s · %s\n     %s" % ("●" if item["answered"] else "○", item["no"], item["type_label"], state, item["unit_title"])

    def _update_progress(self):
        items = self.view["items"]
        self.progress.setText("작성 %d / %d문항" % (sum(1 for item in items if item["answered"]), len(items)))

    def show_item(self, row):
        self.flush()  # 앞 문항에 남은 입력부터 저장
        if not 0 <= row < len(self.view["items"]):
            return
        item = self.current = self.view["items"][row]
        label = "%s · %s · %d점" % (item["type_label"], item["unit_title"], item["points"])
        if item["kind"] == "code":
            label = "%s — %s" % (item["title"], label)
        self.item_title.setText("%d. %s%s" % (item["no"], label, " · 지난번에 틀린 문항" if item["retest"] else ""))
        self.body.setHtml(mdlite.to_html(item["body_md"]))
        if item["kind"] == "code":
            panel, name = self.code_panel, "코드"
        elif item["type"] == "choice":
            panel, name = self.choice_panel, "답안 · 객관식"
        else:
            panel, name = self.text_panel, "답안 · " + item["type_label"]
        panel.set_item(item)
        self.stack.setCurrentWidget(panel)
        self.pane_title.setText(name)
        self.run_btn.setVisible(item["kind"] == "code")
        self.prev_btn.setEnabled(row > 0)
        self.next_btn.setEnabled(row < len(self.view["items"]) - 1)

    def apply_zoom(self):
        css, font = theme.doc_css(self.win.zoom), theme.code_font(self.win.zoom)
        for browser in (self.body, self.code_panel.console):
            browser.document().setDefaultStyleSheet(css)
        for widget in (self.code_panel.editor, self.text_panel.multi, self.text_panel.single, self.choice_panel.entry):
            widget.setFont(font)
        if self.current:  # 스타일은 다음에 넣는 HTML 부터 적용되므로 다시 그린다
            self.body.setHtml(mdlite.to_html(self.current["body_md"]))
            self.code_panel.show_console(self.code_panel.console_html)

    # ── 자동 저장 ──

    def on_answer_changed(self, value):
        item = self.current
        if item is None:
            return
        item["answer"] = value
        if item["kind"] == "code":
            item["answered"] = study.norm_out(value) != study.norm_out(item["starter"])
        else:
            item["answered"] = bool(value if item["type"] == "choice" else value.strip())
        self.dirty[item["id"]] = value
        self.save_timer.start()
        self.listw.item(item["no"] - 1).setText(self._row_text(item))
        self._update_progress()

    def flush(self, commit=True):
        """대기 중인 답을 파일에 쓴다. 다 썼으면 True. commit=True 면 조합 중인 한글부터 확정한다."""
        if commit:
            QGuiApplication.inputMethod().commit()
        self.save_timer.stop()
        if not self.dirty:
            return True
        for item_id, value in list(self.dirty.items()):
            try:
                self.win.session.set_answer(self.view["id"], item_id, value)
            except (SessionError, OSError) as error:
                self.status.setText("저장하지 못했습니다: %s" % error)
                self.win.offer_repair(self.view["id"], self.reload)
                return False
            del self.dirty[item_id]
        self.status.setText("자동 저장됨 %s" % datetime.datetime.now().strftime("%H:%M:%S"))
        return True

    def reload(self):
        """답안지를 복구한 뒤: 못 쓴 답을 마저 쓰고 파일에 남은 답으로 화면을 다시 맞춘다."""
        self.flush()
        self.load(self.view["id"], self.review, self.current["id"] if self.current else None)

    # ── 실행 · 제출 ──

    def set_busy(self, busy, text=""):
        """실행·채점 중에는 입력을 잠근다(채점하는 파일과 화면이 어긋나지 않게)."""
        for widget in (self.listw, self.stack, self.prev_btn, self.next_btn, self.run_btn, self.submit_btn, self.home_btn, self.back_btn):
            widget.setEnabled(not busy)
        self.busy_bar.setVisible(busy)
        if busy:
            self.status.setText(text)
        else:
            row = self.listw.currentRow()
            self.prev_btn.setEnabled(row > 0)
            self.next_btn.setEnabled(row < self.listw.count() - 1)

    def run_code(self):
        item = self.current
        if item is None or item["kind"] != "code" or not self.flush():
            return
        self.code_panel.show_console("<body><p>실행 중입니다.</p></body>")
        rid = self.view["id"]
        self.win.run_job("예시를 실행하는 중입니다.", lambda: self.win.session.try_run(rid, item["id"]), self._ran,
                         on_fail=lambda: self.code_panel.show_console(""))

    def _ran(self, run):
        self.code_panel.show_console(run_html(run))
        self.status.setText("예시 실행을 마쳤습니다.")
        self.code_panel.focus_input()

    def ask_reset(self):
        self.win.ask("시작 코드로 되돌리기", "지금 작성한 코드를 지우고 처음 받은 코드로 되돌립니다.",
                     (("되돌리기", "reset"), ("취소", "")), lambda key: self._reset())

    def _reset(self):
        cur = self.code_panel.editor.textCursor()
        cur.select(QTextCursor.SelectionType.Document)
        cur.insertText(self.current["starter"])  # 편집으로 넣어 자동 저장 경로를 타게 하고, 되돌리기(Ctrl+Z)도 남긴다
        self.flush()

    def submit(self):
        if not self.flush():
            return
        rid = self.view["id"]
        if self.review:
            self.win.run_job("다시 채점하는 중입니다.", lambda: self.win.session.grade(rid), lambda result: self.win.show_result(rid, result))
            return
        try:
            pending = self.win.session.pending(rid)
        except SessionError as error:
            self.status.setText(str(error))
            self.win.offer_repair(rid, self.reload)
            return
        blank, total = pending["blank"], pending["total"]
        if len(blank) == total:
            lines = ["아직 작성한 문항이 없습니다. 지금 제출하면 전체 %d문항이 미응답으로 남습니다." % total, "미응답은 오답으로 처리됩니다."]
        elif blank:
            lines = ["전체 %d문항 중 %d문항을 작성했습니다." % (total, total - len(blank)),
                     "미응답 문항: %s번" % ", ".join(str(n) for n in blank), "미응답은 오답으로 처리됩니다."]
        else:
            lines = ["전체 %d문항을 모두 작성했습니다." % total]
        lines += ["", "제출하면 지금 답이 첫 시도로 기록됩니다. 제출한 뒤에 고쳐서 다시 채점해도 숙달 판정은 바뀌지 않습니다."]
        self.win.ask("회차 제출", "\n".join(lines), (("제출", "submit"), ("계속 풀기", "")), lambda key: self._grade(rid))

    def _grade(self, rid):
        self.win.run_job("채점하는 중입니다. 코드 문제는 모든 테스트를 실행합니다.",
                         lambda: self.win.session.grade(rid, finalize=True), lambda result: self.win.show_result(rid, result))
