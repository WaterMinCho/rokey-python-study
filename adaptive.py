#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""적응형 학습 엔진. 진단 → 약점 분석 → 맞춤 라운드 → 채점·가이드 → 모의고사 순으로 진행함.

결과가 사람마다 달라서 받는 문항도 달라짐. 상태는 submissions/<ID>/profile.json 에만 기록하고,
PR 로 올라가면 CI 와 스터디장이 같은 기준으로 분석함. study.py 가 불러 쓰는 모듈임.
"""
import datetime
import json
import os
import random
import re
import shutil
import unicodedata

import study

ROUND_MIN, ROUND_MAX = 8, 18  # 회차 문항 수 범위. 실제 수는 보강할 단원 수와 직전 성적으로 정함
CODE_RATIO = 0.4  # 회차의 코드 문제 비율. 실제 평가 비율에 맞춤
FOCUS_UNITS = 3  # 가이드에서 보여 주는 집중 단원 수
DIAG_PER_UNIT = 2  # 진단에서 단원당 문항 수
WINDOW = 4  # 레벨 통과 판정에 보는 최근 시도 수
MASTER_LEVEL = 2  # 이 레벨까지 통과하면 단원 숙달
DEFAULT_QUIZ_LEVEL = {"choice": 1, "short": 1, "output": 2}  # 출제자가 level 을 안 적은 퀴즈의 기본 레벨
ROUND_RE = re.compile(r"[dr]\d+")


def now():
    return datetime.datetime.now().isoformat(timespec="seconds")


# 문항 목록

_UNITS = None  # 문제 은행은 실행 중에 바뀌지 않아서 한 번만 읽음. 바뀌었으면 clear_cache 로 비움


def clear_cache():
    global _UNITS
    _UNITS = None


def units():
    """적응형 학습의 단원 = 차시 세트."""
    global _UNITS
    if _UNITS is None:
        out = []
        for sid in study.all_set_ids():
            s = study.load_set(sid)
            if s["meta"].get("kind", "session") == "session":
                out.append(s)
        _UNITS = out
    return _UNITS


def short_title(s):
    return s["meta"].get("title", s["id"])


def unit_priority():
    """단원 중요도(meta.json 의 priority, 기본 1.0). 시험 비중이 큰 단원은 더 자주 나오고 준비도 계산에서도 비중이 커짐."""
    return {s["id"]: float(s["meta"].get("priority", 1.0)) for s in units()}


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


# 프로필

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


# 숙달도

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
        passed[L] = True if available[L] == 0 else level_passed(by_level[L])  # 문항이 없는 레벨은 건너뜀
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


def unit_score(st):
    """단원 준비도 0~100. 숙달이면 85, 심화까지 끝내면 100, 진행 중이면 레벨과 정답률로 계산함."""
    if st["done"]:
        return 100
    if st["mastered"]:
        return 85
    if not st["tested"]:
        return 0
    base = 20 if st["level"] == 1 else 55
    return round(base + 25 * (st["accuracy"] or 0))


def readiness(states):
    """시험 준비도 0~100. 단원 준비도를 중요도로 가중 평균함."""
    priority = unit_priority()
    total = sum(priority.get(st["unit"], 1.0) for st in states)
    return round(sum(unit_score(st) * priority.get(st["unit"], 1.0) for st in states) / total) if total else 0


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


# 라운드 만들기

def completed_rounds(prof):
    return [r for r in prof["rounds"] if r["kind"] != "diag" and r.get("completed_at")]


def last_ratio(prof):
    """직전에 끝낸 회차의 득점률(없으면 None)."""
    done = completed_rounds(prof)
    score = (done[-1].get("first_score") or done[-1].get("score")) if done else None  # 고쳐서 다시 채점한 점수는 쓰지 않음
    if not score:
        return None
    earned, total = score.split("/")
    return int(earned) / int(total) if int(total) else None


def round_size(prof, states):
    """회차 문항 수와 그 이유를 정함.
    보강할 단원은 단원당 1.5~2.5문항, 숙달 단원은 복습으로 0.25~0.5문항씩 더함.
    직전 회차 득점률이 50% 미만이면 문항을 줄이고, 90% 이상이면 2문항을 더 냄."""
    need = 0.0
    weak = 0
    for st in states:
        if st["done"]:
            need += 0.25
        elif st["mastered"]:
            need += 0.5
        else:
            weak += 1
            if st["retry"]:
                need += 2.5
            elif not st["tested"] or st["level"] == 1:
                need += 2.0
            else:
                need += 1.5
    ratio = last_ratio(prof)
    cap = ROUND_MAX
    reason = "보강할 단원 %d개" % weak
    if ratio is not None and ratio < 0.5:  # 힘들어하면 짧게 끊어 자주 피드백
        need *= 0.75
        cap = 12
        reason += " · 직전 득점률이 낮아 짧게"
    elif ratio is not None and ratio >= 0.9:
        need += 2
        reason += " · 직전 득점률이 높아 조금 더"
    size = int(min(cap, max(ROUND_MIN, round(need))))
    return size, reason


def deep_review(states):
    """숙달 단원이 절반 이상이면 숙달 단원 복습을 심화(레벨3)로 올림."""
    return sum(1 for st in states if st["mastered"]) * 2 >= len(states)


def rounds_since_seen(prof, cat):
    """단원별로 마지막으로 문항이 나온 뒤 지난 회차 수(한 번도 안 나왔으면 큰 수)."""
    last = {}
    for index, rnd in enumerate(prof["rounds"]):
        for key in rnd["items"]:
            if key in cat:
                last[cat[key]["unit"]] = index
    total = len(prof["rounds"])
    return {u: total - 1 - i for u, i in last.items()}


def unit_weight(st, since=0):
    """약한 단원일수록 자주 뽑힘. 숙달 단원은 오래 안 볼수록 복습 가중치가 커짐(간격 반복)."""
    if not st["tested"]:
        return 3.0
    if st["done"]:
        return 0.3 + 0.15 * min(since, 4)
    if st["mastered"]:
        return 0.5 + 0.25 * min(since, 4)
    w = (4 - st["level"]) + (2 if st["retry"] else 0)
    if st["accuracy"] is not None:
        w += 1 - st["accuracy"]
    return w


def target_level(st, deep):
    if st["done"]:
        return 3
    if st["mastered"]:
        return 3 if deep else MASTER_LEVEL  # 숙달 단원이 늘면 복습도 심화 문항으로 냄
    return st["level"]


def pick_one(prof, cat, unit_id, level, exclude, rng, prefer):
    """단원·레벨에서 안 풀어 본 문항 하나(가능하면 prefer 유형). 없으면 틀렸던 문항, 그래도 없으면 None."""
    attempted = {a["item"] for a in prof["attempts"]}
    wrong = {a["item"] for a in first_attempts(prof) if not a["ok"]}
    pool = [k for k, it in cat.items() if it["unit"] == unit_id and it["level"] == level and k not in exclude]
    fresh = [k for k in pool if k not in attempted]
    for group in (fresh, [k for k in pool if k in wrong]):
        preferred = [k for k in group if cat[k]["kind"] == prefer]
        others = [k for k in group if cat[k]["kind"] != prefer]
        for cands in (preferred, others):
            if cands:
                return rng.choice(cands)
    return None


RETEST_GAP = 2  # 틀린 문항은 이만큼 회차가 지난 뒤에 다시 냄
RETEST_SLOTS = 2  # 한 회차에 다시 내는 오답 문항 수 상한


def retest_pool(prof, cat):
    """첫 시도에 틀렸고 아직 다른 회차에서 맞히지 못한 문항 중, 마지막으로 본 지 RETEST_GAP 회차 이상 지난 것."""
    index_of = {r["id"]: i for i, r in enumerate(prof["rounds"])}
    last_seen, ever_wrong, later_ok = {}, set(), set()
    for a in sorted(prof["attempts"], key=lambda a: index_of.get(a["round"], 0)):
        key = a["item"]
        if key not in cat:
            continue
        last_seen[key] = index_of.get(a["round"], 0)
        if a["try"] == 1 and not a["ok"]:
            ever_wrong.add(key)
        elif a["try"] == 1 and a["ok"] and key in ever_wrong:
            later_ok.add(key)
    current = len(prof["rounds"])
    return [k for k in ever_wrong - later_ok if current - last_seen[k] >= RETEST_GAP]


def weighted_choice(rng, weights):
    total = sum(weights.values())
    if total <= 0:
        return None
    r = rng.random() * total
    for key, w in weights.items():
        r -= w
        if r <= 0:
            return key
    return key


def build_diagnostic(prof, cat):
    """진단 회차를 만듦. 단원마다 레벨1 퀴즈 2문항을 내고, 레벨1 이 모자라면 그 단원 퀴즈 전체에서 뽑음."""
    rng = random.Random(prof["seed"])
    items = []
    for s in units():
        quiz = [k for k, it in cat.items() if it["unit"] == s["id"] and it["kind"] == "quiz"]
        level1 = [k for k in quiz if cat[k]["level"] == 1]
        pool = level1 if len(level1) >= DIAG_PER_UNIT else quiz
        rng.shuffle(pool)
        items += pool[:DIAG_PER_UNIT]
    rid = "d%d" % (1 + sum(1 for r in prof["rounds"] if r["id"].startswith("d")))
    return {"id": rid, "kind": "diag", "focus": [], "items": items, "shortages": [], "created": now(), "tries": 0,
            "avg_level": round(sum(cat[k]["level"] for k in items) / len(items), 2) if items else 0}


def build_round(prof, cat):
    """전 단원을 섞은 미니 모의고사를 만듦. 약한 단원 문항을 더 많이 넣고, 문항 레벨은 단원별 레벨을 따름.
    전 단원이 심화까지 끝나면 None."""
    states = all_states(prof, cat)
    if all(st["done"] for st in states):
        return None
    by_unit = {st["unit"]: st for st in states}
    deep = deep_review(states)
    size, reason = round_size(prof, states)
    rng = random.Random(prof["seed"] * 1000 + len(prof["rounds"]))
    cap = max(2, size // 4)  # 한 단원이 회차를 독차지하지 않게 함
    since = rounds_since_seen(prof, cat)
    priority = unit_priority()
    weights = {st["unit"]: unit_weight(st, since.get(st["unit"], 9)) * priority.get(st["unit"], 1.0) for st in states}
    counts = {u: 0 for u in weights}
    items, shortages = [], {}
    code_target = round(size * CODE_RATIO)
    code_n = 0
    # 오답 재출제. 예전에 틀린 문항을 간격을 두고 다시 냄
    retest = retest_pool(prof, cat)
    rng.shuffle(retest)
    for key in retest[:min(RETEST_SLOTS, size // 4)]:
        items.append(key)
        counts[cat[key]["unit"]] += 1
        if cat[key]["kind"] == "code":
            code_n += 1
    for _ in range(size * 8):
        if len(items) >= size:
            break
        avail = {u: w for u, w in weights.items() if w > 0 and counts[u] < cap}
        unit_id = weighted_choice(rng, avail)
        if unit_id is None:
            break
        level = target_level(by_unit[unit_id], deep)
        prefer = "code" if code_n < code_target else "quiz"
        key = pick_one(prof, cat, unit_id, level, set(items), rng, prefer)
        if key is None:  # 이 단원·레벨엔 더 낼 문항이 없음
            shortages[(unit_id, level)] = shortages.get((unit_id, level), 0) + 1
            weights[unit_id] = 0
            continue
        items.append(key)
        counts[unit_id] += 1
        if cat[key]["kind"] == "code":
            code_n += 1
    if not items:
        return None
    items.sort(key=lambda k: (cat[k]["kind"] != "quiz", study.natural_key(k)))  # 퀴즈 먼저, 단원 순
    focus = [{"unit": u, "level": target_level(by_unit[u], deep), "count": n} for u, n in counts.items() if n]
    focus.sort(key=lambda f: -f["count"])
    rid = "r%02d" % (1 + sum(1 for r in prof["rounds"] if r["id"].startswith("r")))
    return {"id": rid, "kind": "round", "size_reason": reason, "focus": focus, "items": items,
            "retest": [k for k in items if k in retest],
            "shortages": [{"unit": u, "level": L, "missing": n} for (u, L), n in sorted(shortages.items())],
            "created": now(), "tries": 0,
            "avg_level": round(sum(cat[k]["level"] for k in items) / len(items), 2)}


def round_title(rnd):
    if rnd["kind"] == "diag":
        return "진단 테스트"
    return "%d회차 미니 모의고사" % int(rnd["id"][1:])


def fname_of(key):
    return key.replace("/", "_")


def quiz_section(s, qid):
    """세트 quiz.md 에서 문항 본문을 꺼냄(제목 줄 제외)."""
    text = study.read_text(os.path.join(s["dir"], "quiz.md"))
    m = re.search(r"^## %s\b[^\n]*\n(.*?)(?=^## Q\d+\b|\Z)" % re.escape(qid), text, flags=re.M | re.S)
    return m.group(1).strip() if m else "(문제지를 찾지 못했습니다: problems/%s/quiz.md %s)" % (s["id"], qid)


def problem_body(spec):
    text = study.read_text(os.path.join(spec["dir"], "problem.md"))
    return re.sub(r"^# [^\n]*\n", "", text, count=1).strip()


def write_round(user, rnd, cat):
    """라운드 폴더에 문제지(README.md), 퀴즈 답안지(quiz.py), 코드 문제 시작 파일을 만듦."""
    folder = os.path.join(study.SUBMISSIONS_DIR, user, rnd["id"])
    os.makedirs(folder, exist_ok=True)
    title = round_title(rnd)
    readme = ["# %s" % title, "",
              "> 프로그램(`python study.py`)에서 풀면 이 폴더의 `quiz.py` 와 `.py` 파일에 답이 자동으로 저장됩니다.", ""]
    if rnd["focus"]:
        readme.append("문항 %d개(%s) · 평균 레벨 %.1f · 단원: %s" % (len(rnd["items"]), rnd.get("size_reason", ""), rnd.get("avg_level", 0), ", ".join(
            "%s %d" % (f["unit"], f["count"]) for f in rnd["focus"])))
        readme.append("")
    quiz_lines = ["# %s 퀴즈 답안지입니다. 문제는 같은 폴더의 README.md 에 있습니다." % title,
                  "# 객관식: 번호(복수 정답은 [1, 3]) / 출력 예측·단답: 문자열(여러 줄은 \"\"\" 사용) / 안 푼 문제는 None", ""]
    for key in rnd["items"]:
        if key not in cat:  # 은행에서 사라진 문항
            continue
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


# 채점 · 기록

def grade_round(user, rnd, cat):
    """라운드 채점. 세트 채점과 같은 항목 형식으로 돌려줌."""
    folder = os.path.join(study.SUBMISSIONS_DIR, user, rnd["id"])
    answers, error = {}, None
    if os.path.isfile(os.path.join(folder, "quiz.py")):
        answers, error = study.parse_quiz_answers(os.path.join(folder, "quiz.py"))
    items = []
    for key in rnd["items"]:
        if key not in cat:  # 은행에서 사라진 문항
            continue
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


def record(prof, rnd, items, finalize=False):
    """답한 문항만 시도로 기록함. 빈 문항은 나중에 답했을 때 첫 시도가 됨.
    finalize=True 면 시험처럼 미응답도 오답으로 확정해 기록하므로 회차를 끝낼 수 있음."""
    stamp = now()
    results = rnd.setdefault("results", {})  # 문항별 마지막 결과. 결과가 같으면 다시 채점해도 기록을 늘리지 않음
    blanks = 0
    for it in items:
        state = it["state"]
        if state == "blank":
            if not finalize or it["key"] in results:
                blanks += 0 if it["key"] in results else 1
                continue
            state = "skipped"
        if results.get(it["key"]) == state:
            continue
        tries = sum(1 for a in prof["attempts"] if a["round"] == rnd["id"] and a["item"] == it["key"])
        attempt = {"round": rnd["id"], "item": it["key"], "try": tries + 1, "ok": state == "ok", "at": stamp}
        if state == "skipped":
            attempt["skipped"] = True
        prof["attempts"].append(attempt)
        results[it["key"]] = state
    rnd["tries"] = rnd.get("tries", 0) + 1
    rnd["last_graded"] = stamp
    earned, total, _ = study.totals(items)
    rnd["score"] = "%d/%d" % (earned, total)
    rnd["unanswered"] = blanks


# 가이드

def pad(text, width):
    """한글(전각)을 2칸으로 세어 폭을 맞춤."""
    w = sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in text)
    return text + " " * max(0, width - w)


def mastery_lines(states, cat):
    lines = []
    for st in states:
        acc = "-" if st["accuracy"] is None else "%d%%" % round(st["accuracy"] * 100)
        mark = "✅" if st["mastered"] else ("·" if not st["tested"] else " ")
        lines.append("  %s %s %s %s 정답률 %s (%d문항)" % (
            mark, st["unit"], pad(cat_unit_title(cat, st["unit"])[:14], 28), pad(state_label(st), 14), acc, st["attempted"]))
    return lines


def weak_tags(prof, cat, limit=6):
    """첫 시도에 틀린 문항의 개념 태그를 세어 많이 틀린 개념을 추림(태그가 있는 문항만)."""
    count = {}
    for a in first_attempts(prof):
        if a["ok"] or a["item"] not in cat:
            continue
        for tag in cat[a["item"]]["tags"]:
            count[tag] = count.get(tag, 0) + 1
    return [t for t, _ in sorted(count.items(), key=lambda x: -x[1])[:limit]]


def round_verdicts(rnd, states, cat):
    """이번 회차에 나온 단원별 판정. [{unit, title, level, kind: up|mastered|done|retry|keep, text}]"""
    by_unit = {st["unit"]: st for st in states}
    out = []
    for f in sorted(rnd.get("focus") or [], key=lambda f: study.natural_key(f["unit"])):
        st = by_unit.get(f["unit"])
        if not st:
            continue
        if st["passed"].get(f["level"]):
            if f["level"] >= 3:
                kind, text = "done", "레벨3 통과 → 단원 완료"
            elif st["mastered"] and f["level"] == MASTER_LEVEL:
                kind, text = "mastered", "레벨%d 통과 → 단원 숙달" % f["level"]
            else:
                kind, text = "up", "레벨%d 통과 → 다음은 레벨%d" % (f["level"], f["level"] + 1)
        elif st["retry"]:
            kind, text = "retry", "정답률 낮음 → 같은 레벨을 다른 문항으로 재도전"
        else:
            kind, text = "keep", "레벨%d 유지 → 같은 레벨 문항을 조금 더" % f["level"]
        out.append({"unit": f["unit"], "title": cat_unit_title(cat, f["unit"]), "level": f["level"], "kind": kind, "text": text})
    return out


def guide_text(prof, cat, rnd=None, show_next=False):
    states = all_states(prof, cat)
    lines = ["", "시험 준비도 %d%% (단원 준비도의 중요도 가중 평균)" % readiness(states),
             "단원별 숙달도 (✅ = 레벨%d 통과)" % MASTER_LEVEL] + mastery_lines(states, cat)
    tags = weak_tags(prof, cat)
    if tags:
        lines.append("  약한 개념: " + ", ".join(tags))
    if rnd and rnd["focus"]:
        lines.append("")
        prev = [r for r in prof["rounds"] if r["kind"] != "diag" and r["id"] < rnd["id"] and r.get("avg_level")]
        trend = " (지난 회차 %.1f)" % prev[-1]["avg_level"] if prev else ""
        lines.append("이번 회차 난이도: 평균 레벨 %.1f%s · 문항 %d개" % (rnd.get("avg_level", 0), trend, len(rnd["items"])))
        lines.append("단원별 판정")
        for v in round_verdicts(rnd, states, cat):
            lines.append("  %s %s %s" % (v["unit"], pad(v["title"][:14], 28), v["text"]))
    if rnd and rnd.get("retest"):
        lines.append("  다시 낸 오답 문항: " + ", ".join(fname_of(k) for k in rnd["retest"]))
    if rnd and rnd.get("unanswered"):
        lines.append("  아직 답하지 않은 문항이 %d개 있습니다. 마저 풀고 다시 채점하면 기록됩니다." % rnd["unanswered"])
    lines.append("")
    if not prof["rounds"]:
        lines.append("아직 진단 전입니다. 프로그램을 실행하면 진단 테스트부터 시작합니다.")
    elif all(st["mastered"] for st in states):
        lines.append("전 단원을 숙달했습니다. python study.py start m1 로 실전 모의고사(120분)를 볼 수 있고, 계속 풀면 심화(레벨3) 회차가 나옵니다.")
    else:
        ranked = [st for st in rank_units(states) if not st["mastered"]][:FOCUS_UNITS]
        size, reason = round_size(prof, states)
        lines.append("다음 회차: 문항 %d개(%s) · 많이 나올 단원 %s" % (
            size, reason, ", ".join("%s(레벨%d)" % (st["unit"], st["level"]) for st in ranked)))
        if show_next:
            lines.append("이어서 하기: python study.py go")
    shortages = (rnd or {}).get("shortages") or []
    if shortages:
        lines.append("문항이 바닥난 단원·레벨: " + ", ".join("%s 레벨%d" % (x["unit"], x["level"]) for x in shortages)
                     + ". PR 로 올리면 스터디장에게 출제 요청이 갑니다.")
    return "\n".join(lines)


# 분석(CI · 스터디장)

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
    lines += ["", "시험 준비도 %d%% · 숙달 %d/%d 단원 · 회차 %d회 · 시도 %d문항" % (readiness(states), mastered, len(states), len(prof["rounds"]), len(first_attempts(prof)))]
    tags = weak_tags(prof, cat)
    if tags:
        lines.append("약한 개념: " + ", ".join(tags))
    shortages = collect_shortages([prof])
    if shortages:
        lines.append("부족한 문항: " + ", ".join("%s 레벨%d %d문항" % (u, L, n) for (u, L), n in sorted(shortages.items())))
    return "\n".join(lines) + "\n"


def collect_shortages(profiles):
    """최근 3개 라운드에 기록된 부족 문항 수를 (단원, 레벨)별 최댓값으로 모음."""
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
             "| 이름 | 준비도 | 숙달 | " + " | ".join(unit_ids) + " |", "|---|---|---|" + "---|" * len(unit_ids)]
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
                weak_count[u] += (4 - st["level"]) + (2 if st["retry"] else 0)  # 낮은 레벨·재도전일수록 약함
        lines.append("| %s | %d%% | %d/%d | %s |" % (user, readiness(list(states.values())), sum(1 for s in states.values() if s["mastered"]), len(unit_ids), " | ".join(cells)))
    weakest = sorted(weak_count.items(), key=lambda x: -x[1])[:5]
    lines += ["", "L1~L3 = 진행 중인 레벨, ! = 재도전, · = 미진단", "",
              "팀 전체 약한 단원(약한 순): " + ", ".join(u for u, n in weakest if n)]
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
