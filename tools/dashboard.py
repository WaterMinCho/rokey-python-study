#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""학습 현황판(dashboard.svg, DASHBOARD.md)을 만듦.

main 에 풀이(profile.json)가 올라올 때마다 CI 가 실행해 `dashboard` 브랜치에 커밋함. main 은 PR 로만 바뀌어서 거기에는 커밋하지 못함.
README 는 `dashboard` 브랜치의 이미지를 보여 줌. 로컬에서는 `python tools/dashboard.py` 로 out/ 에 만들어 볼 수 있음.
"""
import datetime
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import study  # noqa: E402
import adaptive  # noqa: E402

OUT_DIR = os.path.join(study.ROOT, "out")
COLORS = {"mastered": "#2e7d32", "deep": "#81c784", "L2": "#ffb300", "L1": "#fb8c00", "retry": "#e53935", "none": "#cfd8dc"}
KST = datetime.timezone(datetime.timedelta(hours=9))


def cell_kind(st):
    if st["done"] or (st["mastered"] and st["level"] == 3):
        return "mastered" if st["done"] else "deep"
    if st["mastered"]:
        return "mastered"
    if not st["tested"]:
        return "none"
    if st["retry"]:
        return "retry"
    return "L%d" % min(st["level"], 2)


def esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_svg(rows, cat, unit_ids):
    width, row_h, top = 960, 112, 64
    height = top + max(1, len(rows)) * row_h + 56
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" font-family="Pretendard, Apple SD Gothic Neo, Malgun Gothic, sans-serif" font-size="13">' % (width, height, width, height),
           '<rect width="100%" height="100%" fill="#ffffff"/>',
           '<text x="24" y="34" font-size="20" font-weight="700" fill="#1c211d">학습 현황판</text>',
           '<text x="24" y="52" fill="#6b7280">단원 = 차시. 준비도 = 단원 준비도의 중요도 가중 평균(0~100). main 에 풀이가 올라오면 자동 갱신됩니다.</text>']
    if not rows:
        out.append('<text x="24" y="%d" fill="#6b7280">아직 진단 테스트를 한 사람이 없습니다. 프로그램을 실행해 시작하세요.</text>' % (top + 30))
    for i, r in enumerate(rows):
        y = top + i * row_h
        out.append('<rect x="16" y="%d" width="%d" height="%d" rx="12" fill="#f5f5f3"/>' % (y, width - 32, row_h - 10))
        out.append('<text x="32" y="%d" font-size="16" font-weight="700" fill="#1c211d">%s</text>' % (y + 28, esc(r["user"])))
        pct = r["readiness"] / 100
        out.append('<rect x="32" y="%d" width="220" height="12" rx="6" fill="#e5e7eb"/>' % (y + 40))
        out.append('<rect x="32" y="%d" width="%d" height="12" rx="6" fill="%s"/>' % (y + 40, int(220 * pct), COLORS["mastered"]))
        out.append('<text x="32" y="%d" fill="#374151">준비도 %d%% · 숙달 %d/%d · 회차 %d · 정답률 %s</text>' % (
            y + 70, r["readiness"], r["mastered"], r["total"], r["rounds"],
            "-" if r["accuracy"] is None else "%d%%" % round(r["accuracy"] * 100)))
        # 단원 띠
        x0 = 300
        for j, u in enumerate(unit_ids):
            kind = cell_kind(r["states"][u])
            x = x0 + j * 22
            out.append('<rect x="%d" y="%d" width="18" height="18" rx="4" fill="%s"><title>%s %s: %s</title></rect>' % (
                x, y + 22, COLORS[kind], u, esc(adaptive.cat_unit_title(cat, u)), esc(adaptive.state_label(r["states"][u]))))
            out.append('<text x="%d" y="%d" font-size="9" fill="#6b7280" text-anchor="middle">%s</text>' % (x + 9, y + 54, u[1:]))
        weak = ", ".join(r["weak"]) or "-"
        strong = ", ".join(r["strong"]) or "-"
        out.append('<text x="%d" y="%d" fill="#b91c1c">약한 단원: %s</text>' % (x0, y + 74, esc(weak)))
        out.append('<text x="%d" y="%d" fill="#166534">능숙한 단원: %s</text>' % (x0 + 260, y + 74, esc(strong)))
        tags = ", ".join(r["tags"]) or "-"
        out.append('<text x="%d" y="%d" fill="#374151">약한 개념: %s</text>' % (x0, y + 94, esc(tags[:60])))
    ly = height - 22
    legend = [("mastered", "숙달"), ("L2", "레벨2 진행"), ("L1", "레벨1 진행"), ("retry", "재도전"), ("none", "미진단")]
    x = 24
    for key, label in legend:
        out.append('<rect x="%d" y="%d" width="12" height="12" rx="3" fill="%s"/>' % (x, ly - 10, COLORS[key]))
        out.append('<text x="%d" y="%d" fill="#374151">%s</text>' % (x + 16, ly, label))
        x += 110
    out.append("</svg>")
    return "\n".join(out) + "\n"


def bar(pct, width=10):
    filled = round(pct * width)
    return "▓" * filled + "░" * (width - filled)


def render_markdown(rows, cat, unit_ids):
    lines = ["# 학습 현황판", "", "![학습 현황판](dashboard.svg)", ""]
    if not rows:
        lines.append("아직 진단 테스트를 한 사람이 없습니다. 프로그램을 실행해 시작하세요.")
    else:
        lines += ["| 이름 | 준비도 | 숙달 | 진행 중 레벨 | 약한 단원 | 능숙한 단원 | 약한 개념 | 회차 | 마지막 풀이 |",
                  "|---|---|---|---|---|---|---|---|---|"]
        for r in rows:
            pct = r["readiness"] / 100
            lv = " · ".join("L%s %d" % (k[1], v) for k, v in r["levels"].items() if v) or "-"
            last = r["last"][:16].replace("T", " ") if r["last"] else "-"
            lines.append("| %s | %s %d%% | %d/%d | %s | %s | %s | %s | %d | %s |" % (
                r["user"], bar(pct), r["readiness"], r["mastered"], r["total"], lv,
                ", ".join(r["weak"]) or "-", ", ".join(r["strong"]) or "-", ", ".join(r["tags"]) or "-", r["rounds"], last))
        latest = max((r["last"] for r in rows if r["last"]), default=None)
        lines += ["", "단원 번호 = 차시. 기준: 마지막 풀이 %s. main 에 풀이가 올라올 때마다 Actions 가 갱신합니다." % ((latest or "-")[:16].replace("T", " "))]
    return "\n".join(lines) + "\n"


def main():
    out_dir = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else OUT_DIR
    cat = adaptive.catalog()
    unit_ids = [s["id"] for s in adaptive.units()]
    rows = [adaptive.user_summary(u, cat) for u in adaptive.users_with_profile()]
    rows.sort(key=lambda r: (-r["readiness"], -r["mastered"], r["user"]))
    study.write_text(os.path.join(out_dir, "dashboard.svg"), render_svg(rows, cat, unit_ids))
    study.write_text(os.path.join(out_dir, "DASHBOARD.md"), render_markdown(rows, cat, unit_ids))
    print("현황판 생성: %d명 → %s" % (len(rows), os.path.relpath(out_dir, study.ROOT)))


if __name__ == "__main__":
    main()
