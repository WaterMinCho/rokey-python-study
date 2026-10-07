#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""학습 세션 서비스 — CLI 와 GUI 가 함께 쓰는 창구.

화면에 아무것도 출력하지 않고 dict 로 돌려준다. 저장 형식은 CLI 와 같다
(submissions/<ID>/profile.json, 회차 폴더의 quiz.py 와 <문항>.py). 그래서 GUI 로 풀든 파일을 직접 고치든
CI 채점·PR 코멘트·현황판이 똑같이 동작한다.
"""
import os
import re
import threading

import adaptive
import study

EXAMPLE_CASES = 2  # '코드 실행' 은 앞의 예시 테스트만 돌린다(시험의 '실행하기'처럼). 기록하지 않는다.
FENCE_RE = re.compile(r"^(`{3,}|~{3,}).*?^\1[ \t]*$", re.S | re.M)
OPTION_RE = re.compile(r"^(\d+)[.)]\s", re.M)


class SessionError(Exception):
    """사용자에게 그대로 보여 줄 수 있는 오류."""


# ───────────────────────── 사용자 ─────────────────────────

def valid_user(name):
    return bool(name) and bool(study.USER_RE.fullmatch(name))


def saved_user():
    """환경 변수 STUDY_USER → .study_user 순으로 찾는다. 없으면 None."""
    name = os.environ.get("STUDY_USER")
    if not name and os.path.isfile(study.USER_FILE):
        name = study.read_text(study.USER_FILE).strip()
    return name if valid_user(name) else None


def save_user(name):
    name = (name or "").strip()
    if not valid_user(name):
        raise SessionError("ID 는 영문·숫자·-·_ 만 쓸 수 있습니다(깃허브 ID 권장).")
    os.makedirs(os.path.join(study.SUBMISSIONS_DIR, name), exist_ok=True)
    study.write_text(study.USER_FILE, name + "\n")
    return name


# ───────────────────────── 도우미 ─────────────────────────

def choice_info(section):
    """객관식 문제 본문에서 (보기 수, 복수 정답 여부)를 읽는다. 코드 블록 안의 번호는 세지 않는다."""
    text = FENCE_RE.sub("", section)
    count = 0
    for m in OPTION_RE.finditer(text):
        n = int(m.group(1))
        if n == 1:
            count = 1  # 마지막으로 1 부터 다시 시작한 목록이 보기다
        elif n == count + 1:
            count = n
    return (count or 5), ("모두" in text)


def literal(value):
    """quiz.py 에 적을 파이썬 리터럴. 여러 줄 문자열은 PR 에서 읽기 좋게 삼중 따옴표로."""
    if isinstance(value, str) and "\n" in value and '"""' not in value and "\\" not in value:
        return '"""\n%s\n"""' % value.strip("\n")
    return repr(value)


def clean_quiz_value(kind, value):
    """화면에서 온 값을 저장용으로 다듬는다. 빈 값은 None."""
    if value is None:
        return None
    if kind == "choice":
        picked = sorted({int(v) for v in value}) if isinstance(value, (list, tuple, set)) else [int(value)]
        if not picked:
            return None
        return picked[0] if len(picked) == 1 else picked
    text = str(value).replace("\r\n", "\n").replace("\r", "\n")
    if kind == "short":
        text = text.strip()
    return text if text.strip() else None


def answer_text(q):
    if q["type"] == "choice":
        return ", ".join("%d번" % n for n in q["answer"])
    if q["type"] == "output":
        return q["answer"].rstrip("\n")
    return " 또는 ".join(q["answer"])


# ───────────────────────── 세션 ─────────────────────────

class Session:
    def __init__(self, user):
        if not valid_user(user):
            raise SessionError("ID 가 올바르지 않습니다: %r" % (user,))
        self.user = user
        self.cat = adaptive.catalog()
        self.prof = adaptive.load_profile(user)
        self._lock = threading.RLock()  # 화면 스레드와 채점 워커가 프로필을 함께 건드리지 않게

    # ── 회차 찾기·만들기 ──

    def folder(self, rid):
        return os.path.join(study.SUBMISSIONS_DIR, self.user, rid)

    def latest(self):
        return self.prof["rounds"][-1] if self.prof["rounds"] else None

    def _round(self, rid=None):
        rnd = self.latest() if rid is None else adaptive.find_round(self.prof, rid)
        if not rnd:
            raise SessionError("회차 %s 를 찾을 수 없습니다." % (rid or ""))
        return rnd

    def _start(self, rnd):
        self.prof["rounds"].append(rnd)
        adaptive.write_round(self.user, rnd, self.cat)
        adaptive.save_profile(self.prof)
        return rnd

    def ensure_round(self):
        """풀 회차가 없으면 만든다(처음이면 진단). (회차 | None, 새로 만들었는지) 반환.
        None 은 전 단원을 심화까지 끝내 더 낼 문항이 없다는 뜻."""
        with self._lock:
            rnd = self.latest()
            if rnd is None:
                return self._start(adaptive.build_diagnostic(self.prof, self.cat)), True
            if not rnd.get("completed_at"):
                return rnd, False
            nxt = adaptive.build_round(self.prof, self.cat)
            if nxt is None:
                return None, False
            return self._start(nxt), True

    # ── 화면에 줄 모양 ──

    def _keys(self, rnd):
        return [k for k in rnd["items"] if k in self.cat]  # 은행에서 사라진 문항은 건너뛴다

    def _quiz_answers(self, rid):
        path = os.path.join(self.folder(rid), "quiz.py")
        if not os.path.isfile(path):
            return {}
        answers, error = study.parse_quiz_answers(path)
        if error:
            return {}
        return {k: (None if v is study.UNPARSED else v) for k, v in answers.items()}

    def _code_path(self, rid, name):
        return os.path.join(self.folder(rid), name + ".py")

    def _item_view(self, rnd, key, number, quiz_answers):
        it = self.cat[key]
        name = adaptive.fname_of(key)
        view = {
            "id": name, "key": key, "no": number, "unit": it["unit"], "unit_title": it["unit_title"],
            "kind": it["kind"], "type": it["type"], "level": it["level"], "points": it["points"],
            "result": (rnd.get("results") or {}).get(key),  # None | ok | wrong | skipped — 채점한 뒤에만 값이 있다
            "retest": key in (rnd.get("retest") or []),
        }
        if it["kind"] == "quiz":
            body = adaptive.quiz_section(it["set"], it["q"]["id"])
            value = quiz_answers.get(name)
            if it["type"] == "output" and isinstance(value, str):
                value = value.strip("\n")
            view.update(type_label=study.QTYPE_LABEL[it["type"]], title=study.QTYPE_LABEL[it["type"]],
                        body_md=body, answer=value, answered=value not in (None, "", []))
            if it["type"] == "choice":
                view["choices"], view["multi"] = choice_info(body)
        else:
            spec = it["spec"]
            starter = study.read_text(os.path.join(spec["dir"], "starter.py"))
            path = self._code_path(rnd["id"], name)
            source = study.read_text(path) if os.path.isfile(path) else starter
            view.update(type_label=study.TYPE_LABEL[it["type"]], title=spec["title"],
                        body_md=adaptive.problem_body(spec), starter=starter, answer=source,
                        answered=study.norm_out(source) != study.norm_out(starter),
                        examples=min(EXAMPLE_CASES, len(spec["cases"])))
        return view

    def _round_summary(self, rnd):
        return {
            "id": rnd["id"], "title": adaptive.round_title(rnd), "kind": rnd["kind"],
            "size": len(self._keys(rnd)), "score": rnd.get("score"), "completed": bool(rnd.get("completed_at")),
            "avg_level": rnd.get("avg_level"), "size_reason": rnd.get("size_reason", ""),
            "unanswered": rnd.get("unanswered"), "graded": bool(rnd.get("results")),
        }

    def open_round(self, rid=None):
        """회차 하나를 화면용으로. items 는 문제지 순서."""
        rnd = self._round(rid)
        answers = self._quiz_answers(rnd["id"])
        view = self._round_summary(rnd)
        view["folder"] = self.folder(rnd["id"])
        view["items"] = [self._item_view(rnd, k, i, answers) for i, k in enumerate(self._keys(rnd), 1)]
        return view

    def rounds(self):
        return [self._round_summary(r) for r in self.prof["rounds"]]

    # ── 답 저장 (자동 저장) ──

    def _find(self, rid, item_id):
        rnd = self._round(rid)
        for key in self._keys(rnd):
            if adaptive.fname_of(key) == item_id:
                return rnd, key, self.cat[key]
        raise SessionError("문항 %s 를 찾을 수 없습니다." % item_id)

    def set_answer(self, rid, item_id, value):
        """답 하나를 파일에 바로 저장한다. 채점·기록은 하지 않는다."""
        rnd, key, it = self._find(rid, item_id)
        with self._lock:
            if it["kind"] == "code":
                text = (value or "").replace("\r\n", "\n").replace("\r", "\n")
                if text and not text.endswith("\n"):
                    text += "\n"
                study.write_text(self._code_path(rnd["id"], item_id), text)
                return
            answers = self._quiz_answers(rnd["id"])
            answers[item_id] = clean_quiz_value(it["type"], value)
            self._write_quiz(rnd, answers)

    def _write_quiz(self, rnd, answers):
        lines = ["# %s — 퀴즈 답안지. 문제는 같은 폴더의 README.md" % adaptive.round_title(rnd),
                 "# 객관식: 번호(복수 정답은 [1, 3]) / 출력 예측·단답: 문자열(여러 줄은 \"\"\" 사용) / 안 푼 문제는 None", ""]
        for key in self._keys(rnd):
            it = self.cat[key]
            if it["kind"] != "quiz":
                continue
            name = adaptive.fname_of(key)
            lines.append("%s = %s  # %s · %s · %d점" % (
                name, literal(answers.get(name)), it["unit_title"], study.QTYPE_LABEL[it["type"]], it["points"]))
        study.write_text(os.path.join(self.folder(rnd["id"]), "quiz.py"), "\n".join(lines) + "\n")

    def reset_item(self, rid, item_id):
        """코드 문제를 시작 코드로 되돌린다."""
        rnd, key, it = self._find(rid, item_id)
        if it["kind"] != "code":
            raise SessionError("코드 문제만 되돌릴 수 있습니다.")
        starter = study.read_text(os.path.join(it["spec"]["dir"], "starter.py"))
        study.write_text(self._code_path(rnd["id"], item_id), starter)
        return starter

    # ── 코드 실행 (예시만, 기록 없음) ──

    def try_run(self, rid, item_id):
        """저장된 코드를 예시 테스트로만 돌려 본다. 숙달 판정에는 영향이 없다."""
        rnd, key, it = self._find(rid, item_id)
        if it["kind"] != "code":
            raise SessionError("코드 문제만 실행할 수 있습니다.")
        spec = it["spec"]
        path = self._code_path(rnd["id"], item_id)
        if not os.path.isfile(path):
            self.reset_item(rid, item_id)
        if spec["type"] == "fill":
            problem = study.check_fill(study.read_text(os.path.join(spec["dir"], "starter.py")), study.read_text(path))
            if problem:
                return {"message": problem, "cases": [], "ran": 0, "total": len(spec["cases"])}
        run = study.run_cases(spec, path, limit=EXAMPLE_CASES)
        message = run["fatal"] or ""
        if not message and run["timed_out"]:
            message = "시간 초과 — %s초 안에 끝나지 않았습니다. 무한 루프가 없는지 확인하세요." % run["timeout"]
        cases = [{"ok": c["ok"], "input": c.get("input", ""), "want": c.get("want", ""), "got": c.get("got", "")}
                 for c in run["cases"]]
        return {"message": message, "cases": cases, "ran": len(cases), "total": len(spec["cases"])}

    # ── 채점 · 기록 · 다음 회차 ──

    def grade(self, rid=None, finalize=False):
        """회차를 채점하고 첫 시도를 기록한다. 다 풀었으면 회차를 끝내고 다음 회차를 만든다.
        finalize=True 면 시험처럼 미응답을 오답으로 확정한다.
        아무것도 풀지 않았으면 기록하지 않고 untouched=True 로 돌려준다."""
        rnd = self._round(rid)
        items = adaptive.grade_round(self.user, rnd, self.cat)  # 오래 걸리는 부분(코드 실행)은 잠금 밖에서
        untouched = all(it["state"] == "blank" for it in items) and not rnd.get("results")
        if untouched and not finalize:
            return self._result(rnd, items, untouched=True)
        with self._lock:
            adaptive.record(self.prof, rnd, items, finalize=finalize)
            completed_now, next_id = False, None
            if not rnd.get("completed_at") and rnd["unanswered"] == 0:
                rnd["completed_at"] = adaptive.now()
                completed_now = True
                if rnd is self.latest():
                    nxt = adaptive.build_round(self.prof, self.cat)
                    if nxt:
                        self.prof["rounds"].append(nxt)
                        adaptive.write_round(self.user, nxt, self.cat)
                        next_id = nxt["id"]
            adaptive.save_profile(self.prof)
        return self._result(rnd, items, completed_now=completed_now, next_round=next_id)

    def _result(self, rnd, items, untouched=False, completed_now=False, next_round=None):
        earned, total, ratio = study.totals(items)
        states = adaptive.all_states(self.prof, self.cat)
        return {
            "round": self._round_summary(rnd), "items": items, "earned": earned, "total": total, "ratio": ratio,
            "unanswered": sum(1 for it in items if it["state"] == "blank"),
            "untouched": untouched, "completed": bool(rnd.get("completed_at")), "completed_now": completed_now,
            "next_round": next_round, "verdicts": adaptive.round_verdicts(rnd, states, self.cat),
            "readiness": adaptive.readiness(states),
        }

    # ── 해설 ──

    def explain(self, rid, item_id):
        """정답·해설. 그 문항을 한 번이라도 채점한 뒤에만 볼 수 있다."""
        rnd, key, it = self._find(rid, item_id)
        if key not in (rnd.get("results") or {}):
            raise SessionError("채점한 뒤에 해설을 볼 수 있습니다.")
        if it["kind"] == "quiz":
            q = it["q"]
            return {"kind": "quiz", "answer": answer_text(q), "explain_md": q.get("explain", ""), "solution": ""}
        secrets, pid = it["set"]["secrets"], it["spec"]["id"]
        return {"kind": "code", "answer": "", "explain_md": secrets.get(pid + "/explain.md", "").strip(),
                "solution": secrets.get(pid + "/solution.py", "").rstrip("\n")}

    # ── 현황 ──

    def overview(self):
        states = adaptive.all_states(self.prof, self.cat)
        priority = adaptive.unit_priority()
        units = [{
            "unit": st["unit"], "title": adaptive.cat_unit_title(self.cat, st["unit"]), "level": st["level"],
            "label": adaptive.state_label(st), "accuracy": st["accuracy"], "attempted": st["attempted"],
            "mastered": st["mastered"], "done": st["done"], "tested": st["tested"], "retry": st["retry"],
            "score": adaptive.unit_score(st), "priority": priority.get(st["unit"], 1.0),
        } for st in states]
        latest = self.latest()
        hint = None
        if self.prof["rounds"] and not all(st["mastered"] for st in states):
            size, reason = adaptive.round_size(self.prof, states)
            focus = [st["unit"] for st in adaptive.rank_units(states) if not st["mastered"]][:adaptive.FOCUS_UNITS]
            hint = {"size": size, "reason": reason, "focus": focus}
        return {
            "user": self.user, "readiness": adaptive.readiness(states),
            "mastered": sum(1 for st in states if st["mastered"]), "total_units": len(states),
            "all_mastered": bool(states) and all(st["mastered"] for st in states),
            "units": units, "weak_tags": adaptive.weak_tags(self.prof, self.cat),
            "rounds": self.rounds(), "attempts": len(adaptive.first_attempts(self.prof)),
            "current": self._round_summary(latest) if latest and not latest.get("completed_at") else None,
            "next_hint": hint,
        }
