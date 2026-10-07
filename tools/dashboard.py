#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""학습 현황판 생성 — dashboard.svg 와 README.md 의 현황판 구역을 갱신한다.

main 에 풀이(profile.json)가 올라올 때마다 CI 가 실행해 커밋한다. 로컬에서도 실행할 수 있다.
"""
import datetime
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import study  # noqa: E402
import adaptive  # noqa: E402

SVG_PATH = os.path.join(study.ROOT, "dashboard.svg")
README_PATH = os.path.join(study.ROOT, "README.md")
START, END = "<!-- dashboard:start -->", "<!-- dashboard:end -->"
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


def summarize(user, cat, unit_ids):
    prof = adaptive.load_profile(user)
    states = {st["unit"]: st for st in adaptive.all_states(prof, cat)}
    firsts = adaptive.first_attempts(prof)
    mastered = [u for u in unit_ids if states[u]["mastered"]]
    not_mastered = [states[u] for u in unit_ids if not states[u]["mastered"] and states[u]["tested"]]
    weak = [st["unit"] for st in adaptive.rank_units(not_mastered)[:3]]
    strong = sorted(mastered, key=lambda u: -(states[u]["accuracy"] or 0))[:3]
    last = max((a["at"] for a in prof["attempts"]), default=None)
    levels = {"L1": 0, "L2": 0, "L3": 0}
    for u in unit_ids:
        st = states[u]
        if st["tested"] and not st["mastered"]:
            levels["L%d" % st["level"]] += 1
    return {
        "user": user, "states": states, "mastered": len(mastered), "total": len(unit_ids),
        "weak": weak, "strong": strong, "tags": adaptive.weak_tags(prof, cat, 4), "levels": levels,
        "rounds": len(prof["rounds"]), "attempts": len(firsts),
        "accuracy": (sum(1 for a in firsts if a["ok"]) / len(firsts)) if firsts else None,
        "last": last,
    }


def esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_svg(rows, cat, unit_ids):
    width, row_h, top = 960, 112, 64
    height = top + max(1, len(rows)) * row_h + 56
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" font-family="Pretendard, Apple SD Gothic Neo, Malgun Gothic, sans-serif" font-size="13">' % (width, height, width, height),
           '<rect width="100%" height="100%" fill="#ffffff"/>',
           '<text x="24" y="34" font-size="20" font-weight="700" fill="#1c211d">학습 현황판</text>',
           '<text x="24" y="52" fill="#6b7280">단원 = 차시, 진도 = 숙달 단원 비율. main 에 풀이가 올라오면 자동 갱신됩니다.</text>']
    if not rows:
        out.append('<text x="24" y="%d" fill="#6b7280">아직 진단 테스트를 한 사람이 없습니다. python study.py 로 시작하세요.</text>' % (top + 30))
    for i, r in enumerate(rows):
        y = top + i * row_h
        out.append('<rect x="16" y="%d" width="%d" height="%d" rx="12" fill="#f5f5f3"/>' % (y, width - 32, row_h - 10))
        out.append('<text x="32" y="%d" font-size="16" font-weight="700" fill="#1c211d">%s</text>' % (y + 28, esc(r["user"])))
        pct = r["mastered"] / r["total"] if r["total"] else 0
        out.append('<rect x="32" y="%d" width="220" height="12" rx="6" fill="#e5e7eb"/>' % (y + 40))
        out.append('<rect x="32" y="%d" width="%d" height="12" rx="6" fill="%s"/>' % (y + 40, int(220 * pct), COLORS["mastered"]))
        out.append('<text x="32" y="%d" fill="#374151">숙달 %d/%d (%d%%) · 라운드 %d회 · 정답률 %s</text>' % (
            y + 70, r["mastered"], r["total"], round(pct * 100), r["rounds"],
            "-" if r["accuracy"] is None else "%d%%" % round(r["accuracy"] * 100)))
        # 단원 띠
        x0 = 300
        for j, u in enumerate(unit_ids):
            kind = cell_kind(r["states"][u])
            x = x0 + j * 22
            out.append('<rect x="%d" y="%d" width="18" height="18" rx="4" fill="%s"><title>%s %s — %s</title></rect>' % (
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
    lines = [START, "", "![학습 현황판](dashboard.svg)", ""]
    if not rows:
        lines.append("아직 진단 테스트를 한 사람이 없습니다. `python study.py` 로 시작하세요.")
    else:
        lines += ["| 이름 | 진도 | 숙달 | 진행 중 레벨 | 약한 단원 | 능숙한 단원 | 약한 개념 | 라운드 | 마지막 풀이 |",
                  "|---|---|---|---|---|---|---|---|---|"]
        for r in rows:
            pct = r["mastered"] / r["total"] if r["total"] else 0
            lv = " · ".join("L%s %d" % (k[1], v) for k, v in r["levels"].items() if v) or "-"
            last = r["last"][:16].replace("T", " ") if r["last"] else "-"
            lines.append("| %s | %s %d%% | %d/%d | %s | %s | %s | %s | %d | %s |" % (
                r["user"], bar(pct), round(pct * 100), r["mastered"], r["total"], lv,
                ", ".join(r["weak"]) or "-", ", ".join(r["strong"]) or "-", ", ".join(r["tags"]) or "-", r["rounds"], last))
        latest = max((r["last"] for r in rows if r["last"]), default=None)
        lines += ["", "단원 번호 = 차시. 기준: 마지막 풀이 %s. main 에 풀이가 올라올 때마다 Actions 가 갱신합니다." % ((latest or "-")[:16].replace("T", " "))]
    lines += ["", END]
    return "\n".join(lines)


def main():
    cat = adaptive.catalog()
    unit_ids = [s["id"] for s in adaptive.units()]
    rows = [summarize(u, cat, unit_ids) for u in adaptive.users_with_profile()]
    rows.sort(key=lambda r: (-r["mastered"], -(r["accuracy"] or 0), r["user"]))
    study.write_text(SVG_PATH, render_svg(rows, cat, unit_ids))
    block = render_markdown(rows, cat, unit_ids)
    readme = study.read_text(README_PATH)
    if START in readme and END in readme:
        readme = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block, readme, flags=re.S)
    else:
        readme = readme.rstrip("\n") + "\n\n## 학습 현황판\n\n" + block + "\n"
    study.write_text(README_PATH, readme)
    print("현황판 갱신: %d명" % len(rows))


if __name__ == "__main__":
    main()
