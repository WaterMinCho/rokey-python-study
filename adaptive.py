#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""적응형 학습 엔진 — 진단 → 약점 분석 → 맞춤 라운드 → 채점·가이드 → 모의고사.

사람마다 결과가 다르니 받는 문항도 다르다. 상태는 submissions/<ID>/profile.json 한 파일에만 기록되고,
PR 로 올라가면 CI 와 스터디장이 같은 기준으로 분석한다. (study.py 가 불러 쓰는 모듈)
"""
import datetime
import json
import os
import random
import re
import shutil

import study

ROUND_SIZE = 9  # 한 라운드 문항 수
FOCUS_UNITS = 3  # 한 라운드에서 집중하는 단원 수
DIAG_PER_UNIT = 2  # 진단에서 단원당 문항 수
WINDOW = 4  # 레벨 통과 판정에 보는 최근 시도 수
MASTER_LEVEL = 2  # 이 레벨까지 통과하면 단원 숙달
DEFAULT_QUIZ_LEVEL = {"choice": 1, "short": 1, "output": 2}  # 출제자가 level 을 안 적은 퀴즈의 기본 레벨
ROUND_RE = re.compile(r"[dr]\d+")


def now():
    return datetime.datetime.now().isoformat(timespec="seconds")


# ───────────────────────── 문항 목록 ─────────────────────────

def units():
    """적응형 학습의 단원 = 차시 세트(연습용 s00 제외)."""
    out = []
    for sid in study.all_set_ids():
        s = study.load_set(sid)
        if s["meta"].get("kind", "session") == "session" and sid != "s00":
            out.append(s)
    return out


def short_title(s):
    return s["meta"].get("title", s["id"])


def catalog():
    """{문항키: 문항}. 키는 's03/Q4', 's03/p02' 형태."""
    items = {}
    for s in units():
        for q in s["questions"]:
            key = "%s/%s" % (s["id"], q["id"])
            items[key] = {"key": key, "unit": s["id"], "unit_title": short_title(s), "kind": "quiz",
                          "type": q["type"], "level": int(q.get("level") or DEFAULT_QUIZ_LEVEL[q["type"]]),
                          "points": q["points"], "tags": q.get("tags", []), "q": q, "set": s}
        for p in s["problems"]:
            key = "%s/%s" % (s["id"], p["id"])
            items[key] = {"key": key, "unit": s["id"], "unit_title": short_title(s), "kind": "code",
                          "type": p["type"], "level": int(p["level"]), "points": p["points"],
                          "tags": p.get("tags", []), "spec": p, "set": s}
    return items


# ───────────────────────── 프로필 ─────────────────────────

def profile_path(user):
    return os.path.join(study.SUBMISSIONS_DIR, user, "profile.json")


def load_profile(user):
    path = profile_path(user)
    if os.path.isfile(path):
        return study.read_json(path)
    return {"user": user, "created": now(), "seed": random.randint(1, 10 ** 6), "rounds": [], "attempts": []}


def save_profile(prof):
    study.write_text(profile_path(prof["user"]), json.dumps(prof, ensure_ascii=False, indent=1) + "\n")


def first_attempts(prof):
    return [a for a in prof["attempts"] if a["try"] == 1]


def find_round(prof, rid):
    return next((r for r in prof["rounds"] if r["id"] == rid), None)


# ───────────────────────── 숙달도 ─────────────────────────

def level_passed(results):
    """최근 시도(첫 시도만)로 레벨 통과 판정: 2문항 이상 전부 정답, 또는 4문항 이상에서 75% 이상."""
    w = results[-WINDOW:]
    n, c = len(w), sum(1 for ok in w if ok)
    return (n >= 2 and c == n) or (n >= 4 and c / n >= 0.75)


def unit_state(prof, cat, unit_id):
    firsts = [a for a in first_attempts(prof) if a["item"] in cat and cat[a["item"]]["unit"] == unit_id]
    by_level = {1: [], 2: [], 3: []}
    for a in firsts:
        by_level[cat[a["item"]]["level"]].append(a["ok"])
    available = {L: sum(1 for it in cat.values() if it["unit"] == unit_id and it["level"] == L) for L in (1, 2, 3)}
    passed = {}
    for L in (1, 2, 3):
        passed[L] = True if available[L] == 0 else level_passed(by_level[L])  # 문항이 없는 레벨은 건너뛴다
    level = next((L for L in (1, 2, 3) if not passed[L]), 3)
    recent = by_level[level][-WINDOW:]
    retry = len(recent) >= 3 and sum(1 for ok in recent if ok) / len(recent) < 0.5
    accuracy = (sum(1 for a in firsts if a["ok"]) / len(firsts)) if firsts else None
    return {
        "unit": unit_id, "level": level, "passed": passed, "available": available,
        "mastered": all(passed[L] for L in range(1, MASTER_LEVEL + 1)),
        "done": all(passed.values()), "tested": bool(firsts), "retry": retry,
        "accuracy": accuracy, "attempted": len(firsts),
    }


def all_states(prof, cat):
    return [unit_state(prof, cat, s["id"]) for s in units()]


def rank_units(states):
    """약한 단원 먼저: 미숙달 → 낮은 레벨 → 낮은 정답률 → 차시 순."""
    def key(st):
        acc = st["accuracy"] if st["accuracy"] is not None else 0.0
        return (1 if st["mastered"] else 0, st["level"], acc, study.natural_key(st["unit"]))
    return sorted(states, key=key)


def state_label(st):
    if not st["tested"]:
        return "미진단"
    if st["done"]:
        return "숙달(심화까지)"
    if st["mastered"]:
        return "숙달"
    if st["retry"]:
        return "레벨%d 재도전" % st["level"]
    return "레벨%d 진행" % st["level"]


# ───────────────────────── 라운드 만들기 ─────────────────────────

def pick_items(prof, cat, unit_id, level, n, rng):
    """단원·레벨에서 안 풀어 본 문항 우선(코드 문제 1개 이상 포함), 모자라면 틀렸던 문항 재도전, 그래도 모자라면 부족 기록."""
    attempted = {a["item"] for a in prof["attempts"]}
    wrong = {a["item"] for a in first_attempts(prof) if not a["ok"]}
    pool = [k for k, it in cat.items() if it["unit"] == unit_id and it["level"] == level]
    fresh = [k for k in pool if k not in attempted]
    rng.shuffle(fresh)
    code = [k for k in fresh if cat[k]["kind"] == "code"]
    quiz = [k for k in fresh if cat[k]["kind"] == "quiz"]
    chosen = code[:1]
    rest = quiz + code[1:]
    rng.shuffle(rest)
    chosen += rest[: max(0, n - len(chosen))]
    if len(chosen) < n:
        retry = [k for k in pool if k in wrong and k not in chosen]
        rng.shuffle(retry)
        chosen += retry[: n - len(chosen)]
    return chosen, n - len(chosen)


def build_diagnostic(prof, cat):
    """단원마다 레벨1 퀴즈 2문항(부족하면 아무 퀴즈)으로 출발점을 정한다."""
    rng = random.Random(prof["seed"])
    items = []
    for s in units():
        quiz = [k for k, it in cat.items() if it["unit"] == s["id"] and it["kind"] == "quiz"]
        level1 = [k for k in quiz if cat[k]["level"] == 1]
        pool = level1 if len(level1) >= DIAG_PER_UNIT else quiz
        rng.shuffle(pool)
        items += pool[:DIAG_PER_UNIT]
    rid = "d%d" % (1 + sum(1 for r in prof["rounds"] if r["id"].startswith("d")))
    return {"id": rid, "kind": "diag", "focus": [], "items": items, "shortages": [], "created": now(), "tries": 0}


def build_round(prof, cat):
    """약한 단원 FOCUS_UNITS 개에 집중하는 라운드. 전 단원 숙달이면 심화(레벨3), 그것도 끝이면 None."""
    ranked = rank_units(all_states(prof, cat))
    focus = [st for st in ranked if not st["mastered"]][:FOCUS_UNITS]
    kind = "round"
    if not focus:
        focus = [st for st in ranked if not st["done"]][:FOCUS_UNITS]
        kind = "deep"
    if not focus:
        return None
    rng = random.Random(prof["seed"] * 1000 + len(prof["rounds"]))
    per = ROUND_SIZE // len(focus)
    items, shortages = [], []
    for st in focus:
        chosen, missing = pick_items(prof, cat, st["unit"], st["level"], per, rng)
        items += chosen
        if missing:
            shortages.append({"unit": st["unit"], "level": st["level"], "missing": missing})
    # 남는 자리는 숙달한 단원 복습 1문항으로
    mastered = [st for st in ranked if st["mastered"] and st["unit"] not in [f["unit"] for f in focus]]
    if mastered and len(items) < ROUND_SIZE:
        st = rng.choice(mastered)
        extra, _ = pick_items(prof, cat, st["unit"], MASTER_LEVEL, 1, rng)
        items += extra
    rid = "r%02d" % (1 + sum(1 for r in prof["rounds"] if r["id"].startswith("r")))
    return {"id": rid, "kind": kind, "focus": [{"unit": st["unit"], "level": st["level"]} for st in focus],
            "items": items, "shortages": shortages, "created": now(), "tries": 0}


def fname_of(key):
    return key.replace("/", "_")


def quiz_section(s, qid):
    """세트 quiz.md 에서 해당 문항 본문(제목 줄 제외)을 꺼낸다."""
    text = study.read_text(os.path.join(s["dir"], "quiz.md"))
    m = re.search(r"^## %s\b[^\n]*\n(.*?)(?=^## Q\d+\b|\Z)" % re.escape(qid), text, flags=re.M | re.S)
    return m.group(1).strip() if m else "(문제지를 찾지 못했습니다: problems/%s/quiz.md %s)" % (s["id"], qid)


def problem_body(spec):
    text = study.read_text(os.path.join(spec["dir"], "problem.md"))
    return re.sub(r"^# [^\n]*\n", "", text, count=1).strip()


def write_round(user, rnd, cat):
    """라운드 폴더에 문제지(README.md), 퀴즈 답안지(quiz.py), 코드 문제 시작 파일을 만든다."""
    folder = os.path.join(study.SUBMISSIONS_DIR, user, rnd["id"])
    os.makedirs(folder, exist_ok=True)
    title = "진단 테스트" if rnd["kind"] == "diag" else ("심화 라운드 %s" if rnd["kind"] == "deep" else "라운드 %s") % rnd["id"]
    readme = ["# %s" % title, "",
              "> 퀴즈는 코드를 실행하지 말고 눈으로 풀어 `quiz.py` 에 답을 적습니다. 코드 문제는 같은 폴더의 `.py` 파일을 고칩니다.",
              "> 채점: `python study.py grade %s`" % rnd["id"], ""]
    if rnd["focus"]:
        readme.append("이번 라운드 집중 단원: " + ", ".join(
            "%s(레벨%d)" % (cat_unit_title(cat, f["unit"]), f["level"]) for f in rnd["focus"]))
        readme.append("")
    quiz_lines = ["# %s — 퀴즈 답안지. 문제는 같은 폴더의 README.md" % title,
                  "# 객관식: 번호(복수 정답은 [1, 3]) / 출력 예측·단답: 문자열(여러 줄은 \"\"\" 사용) / 안 푼 문제는 None", ""]
    for key in rnd["items"]:
        it = cat[key]
        name = fname_of(key)
        if it["kind"] == "quiz":
            readme.append("## %s (%s · %s · %d점)\n\n%s\n" % (
                name, it["unit_title"], study.QTYPE_LABEL[it["type"]], it["points"], quiz_section(it["set"], it["q"]["id"])))
            quiz_lines.append("%s = None  # %s · %s · %d점" % (name, it["unit_title"], study.QTYPE_LABEL[it["type"]], it["points"]))
        else:
            spec = it["spec"]
            readme.append("## %s (%s · %s · %s · %d점)\n\n파일: `%s.py`\n\n%s\n" % (
                name, it["unit_title"], study.TYPE_LABEL[spec["type"]], spec["title"], it["points"], name, problem_body(spec)))
            target = os.path.join(folder, name + ".py")
            if not os.path.exists(target):
                shutil.copyfile(os.path.join(spec["dir"], "starter.py"), target)
    study.write_text(os.path.join(folder, "README.md"), "\n".join(readme) + "\n")
    if not os.path.exists(os.path.join(folder, "quiz.py")):
        study.write_text(os.path.join(folder, "quiz.py"), "\n".join(quiz_lines) + "\n")
    return folder


def cat_unit_title(cat, unit_id):
    for it in cat.values():
        if it["unit"] == unit_id:
            return it["unit_title"]
    return unit_id


# ───────────────────────── 채점 · 기록 ─────────────────────────

def grade_round(user, rnd, cat):
    """라운드 채점. 세트 채점과 같은 항목 형식을 돌려준다."""
    folder = os.path.join(study.SUBMISSIONS_DIR, user, rnd["id"])
    answers, error = {}, None
    if os.path.isfile(os.path.join(folder, "quiz.py")):
        answers, error = study.parse_quiz_answers(os.path.join(folder, "quiz.py"))
    items = []
    for key in rnd["items"]:
        it = cat[key]
        name = fname_of(key)
        if it["kind"] == "quiz":
            state, detail = ("wrong", error) if error else (study.check_quiz_answer(it["q"], answers.get(name)), "")
            label = "%s · %s" % (it["unit_title"], study.QTYPE_LABEL[it["type"]])
        else:
            state, detail = study.grade_problem(it["spec"], os.path.join(folder, name + ".py"))
            label = "%s · %s · %s" % (it["unit_title"], study.TYPE_LABEL[it["type"]], it["spec"]["title"])
        items.append({"id": name, "key": key, "label": label, "points": it["points"],
                      "earned": it["points"] if state == "ok" else 0, "state": state, "detail": detail})
    return items


def record(prof, rnd, items):
    """답한 문항만 시도로 기록한다(빈 문항은 나중에 답했을 때 첫 시도가 된다)."""
    stamp = now()
    for it in items:
        if it["state"] == "blank":
            continue
        tries = sum(1 for a in prof["attempts"] if a["round"] == rnd["id"] and a["item"] == it["key"])
        prof["attempts"].append({"round": rnd["id"], "item": it["key"], "try": tries + 1,
                                 "ok": it["state"] == "ok", "at": stamp})
    rnd["tries"] = rnd.get("tries", 0) + 1
    rnd["last_graded"] = stamp
    earned, total, _ = study.totals(items)
    rnd["score"] = "%d/%d" % (earned, total)
    rnd["unanswered"] = sum(1 for it in items if it["state"] == "blank")


# ───────────────────────── 가이드 ─────────────────────────

def mastery_lines(states, cat):
    lines = []
    for st in states:
        acc = "-" if st["accuracy"] is None else "%d%%" % round(st["accuracy"] * 100)
        mark = "✅" if st["mastered"] else ("·" if not st["tested"] else " ")
        lines.append("  %s %-4s %-22s %-12s 정답률 %s (%d문항)" % (
            mark, st["unit"], cat_unit_title(cat, st["unit"])[:22], state_label(st), acc, st["attempted"]))
    return lines


def weak_tags(prof, cat, limit=6):
    """최근 틀린 문항의 개념 태그를 모아 약한 개념을 추린다(태그가 있는 문항만)."""
    count = {}
    for a in first_attempts(prof):
        if a["ok"] or a["item"] not in cat:
            continue
        for tag in cat[a["item"]]["tags"]:
            count[tag] = count.get(tag, 0) + 1
    return [t for t, _ in sorted(count.items(), key=lambda x: -x[1])[:limit]]


def guide_text(prof, cat, rnd=None):
    states = all_states(prof, cat)
    lines = ["", "단원별 숙달도 (✅ = 레벨%d 통과)" % MASTER_LEVEL] + mastery_lines(states, cat)
    tags = weak_tags(prof, cat)
    if tags:
        lines.append("  약한 개념: " + ", ".join(tags))
    if rnd and rnd["focus"]:
        lines.append("")
        lines.append("이번 라운드 판정")
        by_unit = {st["unit"]: st for st in states}
        for f in rnd["focus"]:
            st = by_unit[f["unit"]]
            if st["passed"].get(f["level"]):
                verdict = "레벨%d 통과 → 다음은 레벨%d" % (f["level"], f["level"] + 1) if f["level"] < 3 else "레벨3 통과 → 단원 완료"
                if st["mastered"] and f["level"] == MASTER_LEVEL:
                    verdict = "레벨%d 통과 → 단원 숙달" % f["level"]
            elif st["retry"]:
                verdict = "정답률 낮음 → 같은 레벨을 다른 문항으로 재도전"
            else:
                verdict = "레벨%d 유지 → 같은 레벨 문항을 조금 더" % f["level"]
            lines.append("  %-4s %-22s %s" % (f["unit"], cat_unit_title(cat, f["unit"])[:22], verdict))
    if rnd and rnd.get("unanswered"):
        lines.append("  아직 답하지 않은 문항 %d개 — 마저 풀고 다시 채점하면 기록됩니다." % rnd["unanswered"])
    lines.append("")
    untested = [st for st in states if not st["tested"]]
    if untested and not any(r["kind"] == "diag" for r in prof["rounds"]):
        lines.append("다음: python study.py diagnose  (진단 테스트로 출발점 정하기)")
    elif all(st["mastered"] for st in states):
        lines.append("전 단원 숙달. 다음: python study.py start m1  (모의고사) — 심화 라운드를 원하면 python study.py next")
    else:
        ranked = [st for st in rank_units(states) if not st["mastered"]][:FOCUS_UNITS]
        lines.append("다음 라운드 집중 단원: " + ", ".join("%s(레벨%d)" % (st["unit"], st["level"]) for st in ranked))
        lines.append("다음: python study.py next")
    shortages = (rnd or {}).get("shortages") or []
    if shortages:
        lines.append("부족한 문항: " + ", ".join("%s 레벨%d %d문항" % (x["unit"], x["level"], x["missing"]) for x in shortages)
                     + " — PR 로 올리면 스터디장에게 출제 요청이 갑니다.")
    return "\n".join(lines)


# ───────────────────────── 분석(CI · 스터디장) ─────────────────────────

def users_with_profile():
    return [u for u in study.all_users() if os.path.isfile(profile_path(u))]


def user_analysis_markdown(user, cat):
    prof = load_profile(user)
    states = all_states(prof, cat)
    lines = ["### `%s` 학습 분석" % user, "",
             "| 단원 | 상태 | 정답률 | 시도 |", "|---|---|---|---|"]
    for st in states:
        acc = "-" if st["accuracy"] is None else "%d%%" % round(st["accuracy"] * 100)
        lines.append("| %s %s | %s | %s | %d |" % (st["unit"], cat_unit_title(cat, st["unit"]), state_label(st), acc, st["attempted"]))
    mastered = sum(1 for st in states if st["mastered"])
    lines += ["", "숙달 %d/%d 단원 · 라운드 %d회 · 시도 %d문항" % (mastered, len(states), len(prof["rounds"]), len(first_attempts(prof)))]
    tags = weak_tags(prof, cat)
    if tags:
        lines.append("약한 개념: " + ", ".join(tags))
    shortages = collect_shortages([prof])
    if shortages:
        lines.append("부족한 문항: " + ", ".join("%s 레벨%d %d문항" % (u, L, n) for (u, L), n in sorted(shortages.items())))
    return "\n".join(lines) + "\n"


def collect_shortages(profiles):
    """최근 라운드들에 기록된 부족 문항을 (단원, 레벨) 별로 합산."""
    total = {}
    for prof in profiles:
        for rnd in prof["rounds"][-3:]:
            for x in rnd.get("shortages", []):
                total[(x["unit"], x["level"])] = max(total.get((x["unit"], x["level"]), 0), x["missing"])
    return total


def team_analysis_markdown(cat):
    users = users_with_profile()
    if not users:
        return "### 학습 현황\n\n아직 진단 테스트를 한 사람이 없습니다.\n", {}
    unit_ids = [s["id"] for s in units()]
    lines = ["### 학습 현황 (단원별 상태)", "",
             "| 이름 | 숙달 | " + " | ".join(unit_ids) + " |", "|---|---|" + "---|" * len(unit_ids)]
    weak_count = {u: 0 for u in unit_ids}
    profiles = []
    for user in users:
        prof = load_profile(user)
        profiles.append(prof)
        states = {st["unit"]: st for st in all_states(prof, cat)}
        cells = []
        for u in unit_ids:
            st = states[u]
            if st["mastered"]:
                cells.append("✅")
            elif not st["tested"]:
                cells.append("·")
            else:
                cells.append("L%d%s" % (st["level"], "!" if st["retry"] else ""))
                weak_count[u] += 1
        lines.append("| %s | %d/%d | %s |" % (user, sum(1 for s in states.values() if s["mastered"]), len(unit_ids), " | ".join(cells)))
    weakest = sorted(weak_count.items(), key=lambda x: -x[1])[:5]
    lines += ["", "L1~L3 = 진행 중인 레벨, ! = 재도전, · = 미진단", "",
              "팀 전체 약한 단원: " + ", ".join("%s(%d명)" % (u, n) for u, n in weakest if n)]
    shortages = collect_shortages(profiles)
    if shortages:
        lines += ["", "부족한 문항: " + ", ".join("%s 레벨%d %d문항" % (u, L, n) for (u, L), n in sorted(shortages.items()))]
    return "\n".join(lines) + "\n", shortages


def shortage_request_markdown(shortages, cat):
    lines = ["문제 은행에 아래 문항이 모자랍니다. 스터디장이 `docs/AUTHORING.md` 규격대로 추가하면 다음 `git pull` 부터 라운드에 포함됩니다.", "",
             "| 단원 | 레벨 | 부족 수 |", "|---|---|---|"]
    for (u, L), n in sorted(shortages.items()):
        lines.append("| %s %s | %d | %d |" % (u, cat_unit_title(cat, u), L, n))
    lines += ["", "이 이슈는 main 에 풀이가 올라올 때마다 자동으로 갱신됩니다."]
    return "\n".join(lines) + "\n"
