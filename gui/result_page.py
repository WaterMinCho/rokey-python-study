# -*- coding: utf-8 -*-
"""결과 화면: 점수 · 준비도 · 단원별 판정 · 문항별 결과와 해설."""
import html
import re

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (QFrame, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QProgressBar, QPushButton, QSplitter,
                             QTextBrowser, QVBoxLayout, QWidget)

import mdlite
from gui import theme


def md_html(text):
    """마크다운 문서를 다른 HTML 사이에 끼워 넣을 수 있게 body 태그를 벗긴다."""
    return mdlite.to_html(text)[len("<body>"):-len("</body>")]


def code_box(text):
    return ('<table width="100%%" cellspacing="0" cellpadding="8" border="0" style="margin-top:2px; margin-bottom:10px;">'
            '<tr><td class="codebox"><pre>%s</pre></td></tr></table>' % html.escape(text, quote=False))


def band(title, anchor=""):
    """구역 제목. 문제 본문 안의 제목과 섞이지 않게 띠로 그린다."""
    return ('<a name="%s"></a><table width="100%%" cellspacing="0" cellpadding="6" border="0" style="margin-top:14px; margin-bottom:8px;">'
            '<tr><td style="background-color:#eaeef2;"><b>%s</b></td></tr></table>' % (anchor, title))


def my_answer_html(item):
    answer = item["answer"]
    if not item["answered"]:
        return "<p>(작성하지 않았습니다)</p>"
    if item["type"] == "choice":
        picked = answer if isinstance(answer, (list, tuple)) else [answer]
        return "<p><b>%s</b></p>" % ", ".join("%s번" % n for n in picked)
    return code_box(str(answer).rstrip("\n"))


class ResultPage(QWidget):
    def __init__(self, win):
        super().__init__()
        self.setObjectName("page")
        self.win = win
        self.view, self.verdicts, self.revealed = None, None, set()

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 0)
        head = QHBoxLayout()
        self.home_btn = QPushButton("홈으로")
        self.title = QLabel()
        self.title.setObjectName("h1")
        head.addWidget(self.home_btn)
        head.addSpacing(8)
        head.addWidget(self.title, 1)
        root.addLayout(head)

        card = QFrame()
        card.setObjectName("card")
        card_box = QHBoxLayout(card)
        card_box.setContentsMargins(20, 10, 20, 10)
        self.score = QLabel()
        self.score.setObjectName("big")
        self.ratio = QLabel()
        self.ratio.setObjectName("h2")
        self.note = QLabel()
        self.note.setObjectName("muted")
        self.note.setWordWrap(True)
        ready_box = QVBoxLayout()
        self.ready = QLabel()
        self.ready.setObjectName("h2")
        self.ready_bar = QProgressBar()
        self.ready_bar.setRange(0, 100)
        self.ready_bar.setTextVisible(False)
        self.ready_bar.setFixedWidth(260)
        ready_box.addStretch(1)
        ready_box.addWidget(self.ready)
        ready_box.addWidget(self.ready_bar)
        ready_box.addStretch(1)
        card_box.addWidget(self.score)
        card_box.addSpacing(14)
        card_box.addWidget(self.ratio)
        card_box.addSpacing(14)
        card_box.addWidget(self.note, 1)
        card_box.addLayout(ready_box)
        root.addWidget(card)

        split = QSplitter(Qt.Orientation.Horizontal)
        self.listw = QListWidget()
        self.listw.setMinimumWidth(260)
        self.listw.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        right = QWidget()
        right_box = QVBoxLayout(right)
        right_box.setContentsMargins(0, 0, 0, 0)
        top = QHBoxLayout()
        self.item_title = QLabel()
        self.item_title.setObjectName("h2")
        self.explain_btn = QPushButton("해설 보기")
        self.retry_btn = QPushButton("다시 풀기")
        top.addWidget(self.item_title, 1)
        top.addWidget(self.explain_btn)
        top.addWidget(self.retry_btn)
        self.detail = QTextBrowser()
        self.detail.setOpenLinks(False)
        self.detail.document().setDocumentMargin(14)
        right_box.addLayout(top)
        right_box.addWidget(self.detail, 1)
        split.addWidget(self.listw)
        split.addWidget(right)
        split.setStretchFactor(0, 0)
        split.setStretchFactor(1, 1)
        split.setSizes([330, 920])
        split.setChildrenCollapsible(False)
        root.addWidget(split, 1)

        bar = QFrame()
        bar.setObjectName("bar")
        bar_box = QHBoxLayout(bar)
        bar_box.setContentsMargins(4, 8, 4, 8)
        self.status = QLabel("")
        self.status.setObjectName("muted")
        self.busy_bar = QProgressBar()
        self.busy_bar.setRange(0, 0)
        self.busy_bar.setTextVisible(False)
        self.busy_bar.setFixedWidth(140)
        self.busy_bar.hide()
        self.git_btn = QPushButton("제출(PR 올리기)")
        self.next_btn = QPushButton()
        self.next_btn.setObjectName("primary")
        bar_box.addWidget(self.status, 1)
        bar_box.addWidget(self.busy_bar)
        bar_box.addWidget(self.git_btn)
        bar_box.addWidget(self.next_btn)
        root.addWidget(bar)

        self.listw.currentRowChanged.connect(self.show_row)
        self.explain_btn.clicked.connect(self.reveal)
        self.retry_btn.clicked.connect(lambda: win.open_round(self.view["id"], review=True, select=self.selected()["id"]))
        self.home_btn.clicked.connect(win.go_home)
        self.git_btn.clicked.connect(win.submit_pr)
        self.next_btn.clicked.connect(win.start_next)

    def load(self, rid, result=None):
        """끝난 회차의 결과를 올린다. result 는 방금 채점한 결과(session.grade)이고, 없으면 기록된 결과를 보여 준다."""
        session = self.win.session
        view = session.open_round(rid)
        states = {it["id"]: it["state"] for it in result["items"]} if result else {}
        for item in view["items"]:
            item["state"] = states.get(item["id"], item["result"])
        earned = sum(item["points"] for item in view["items"] if item["state"] == "ok")
        total = sum(item["points"] for item in view["items"])
        overview = session.overview()
        self.view, self.verdicts, self.revealed = view, result["verdicts"] if result else None, set()
        self.title.setText("%s 결과" % view["title"])
        self.score.setText("%d / %d점" % (earned, total))
        self.ratio.setText("득점률 %d%%" % (round(100 * earned / total) if total else 0))
        first = view["first_score"]
        self.note.setText("첫 제출 %s점. 숙달 판정에는 첫 제출만 반영됩니다." % first.replace("/", " / ")
                          if first and first != "%d/%d" % (earned, total) else "")
        self.ready.setText("시험 준비도 %d%%" % overview["readiness"])
        self.ready_bar.setValue(overview["readiness"])
        self.next_btn.setText(self.win.next_action(overview)[0])
        self.git_btn.setEnabled(self.win.gitflow is not None)
        self.git_btn.setToolTip(self.win.git_reason)
        self.status.setText("")
        self.listw.blockSignals(True)
        self.listw.clear()
        self.listw.addItem("단원별 판정")
        for item in view["items"]:
            name, color = theme.result_label(item["state"])
            row = QListWidgetItem("%s  %d. %s · %s" % (name, item["no"], item["type_label"], item["unit_title"]))
            row.setForeground(QColor(color))
            self.listw.addItem(row)
        self.listw.setCurrentRow(0)
        self.listw.blockSignals(False)
        self.show_row(0)

    def selected(self):
        """고른 문항. 맨 위의 '단원별 판정' 줄이면 None."""
        row = self.listw.currentRow()
        return self.view["items"][row - 1] if row > 0 else None

    def show_row(self, row):
        item = self.selected()
        if item is None:
            self.item_title.setText("단원별 판정")
            self.detail.setHtml(self.summary_html())
        else:
            label = "%s · %s · %d점" % (item["type_label"], item["unit_title"], item["points"])
            self.item_title.setText("%d. %s" % (item["no"], "%s — %s" % (item["title"], label) if item["kind"] == "code" else label))
            self.detail.setHtml(self.item_html(item))
        self.explain_btn.setEnabled(item is not None and item["id"] not in self.revealed)
        self.retry_btn.setEnabled(item is not None and item["state"] != "ok")

    def reveal(self):
        self.revealed.add(self.selected()["id"])
        self.show_row(self.listw.currentRow())
        self.detail.scrollToAnchor("answer")  # 문제 본문이 길어도 해설이 바로 보이게

    def summary_html(self):
        count = {"ok": 0, "wrong": 0, "blank": 0}
        for item in self.view["items"]:
            count[item["state"] if item["state"] in count else "blank"] += 1
        parts = ["<p>정답 %d문항 · 오답 %d문항 · 미응답 %d문항</p>" % (count["ok"], count["wrong"], count["blank"])]
        if self.verdicts:
            rows = "".join('<tr><td><b><span style="color:%s;">%s</span></b></td><td>%s %s</td><td>%s</td></tr>' % (
                theme.VERDICT[v["kind"]][1], theme.VERDICT[v["kind"]][0], v["unit"], html.escape(v["title"]), html.escape(v["text"]))
                for v in self.verdicts)
            parts.append('<table class="grid" border="1" cellspacing="0" cellpadding="6">'
                         "<tr><th>판정</th><th>단원</th><th>내용</th></tr>%s</table>" % rows)
        elif self.view["kind"] == "diag":
            parts.append("<p>진단 결과로 단원별 출발 레벨을 정했습니다. 단원별 상태는 홈의 단원 띠에서 볼 수 있습니다.</p>")
        else:
            parts.append("<p>단원별 판정은 제출한 직후에 보여 줍니다. 지금 단원별 상태는 홈의 단원 띠에서 볼 수 있습니다.</p>")
        parts.append("<h2>문항 다시 보기</h2><p>왼쪽에서 문항을 고르면 문제와 내 답이 나옵니다. 틀린 문항은 '다시 풀기'로 먼저 고쳐 보고, "
                     "'해설 보기'로 정답과 해설을 확인하세요.</p>")
        return "<body>%s</body>" % "".join(parts)

    def item_html(self, item):
        name, color = theme.result_label(item["state"])
        parts = ['<p><b><span style="color:%s;">%s</span></b></p>' % (color, name), md_html(item["body_md"]),
                 band("내 답"), my_answer_html(item)]
        if item["id"] in self.revealed:
            info = self.win.session.explain(self.view["id"], item["id"])
            parts.append(band("정답과 해설", "answer"))
            if info["answer"]:
                parts.append("<p><b>정답: %s</b></p>" % info["answer"] if item["type"] == "choice"
                             else "<p><b>정답</b></p>" + code_box(info["answer"]))
            if info["markdown"]:
                parts.append(md_html(re.sub(r"^# [^\n]*\n", "", info["explain"], count=1)))  # 문서 첫 줄의 제목은 띠 제목과 겹친다
            else:  # 퀴즈 해설은 마크다운 문서가 아니라 한 문단의 글이다
                parts.append("<p>%s</p>" % mdlite.inline_html(info["explain"]))
            if info["solution"]:
                parts += [band("모범 답안"), code_box(info["solution"])]
        return "<body>%s</body>" % "".join(parts)

    def apply_zoom(self):
        self.detail.document().setDefaultStyleSheet(theme.doc_css(self.win.zoom))
        if self.view:
            self.show_row(self.listw.currentRow())

    def set_busy(self, busy, text=""):
        for widget in (self.listw, self.explain_btn, self.retry_btn, self.home_btn, self.next_btn):
            widget.setEnabled(not busy)
        self.git_btn.setEnabled(not busy and self.win.gitflow is not None)
        self.busy_bar.setVisible(busy)
        self.status.setText(text if busy else "")
        if not busy and self.view:
            self.show_row(self.listw.currentRow())
