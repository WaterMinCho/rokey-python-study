#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""학습 세션 서비스. CLI 와 GUI 가 함께 씀.

화면에 아무것도 출력하지 않고 dict 로 돌려줌. 저장 형식이 CLI 와 같아서
(submissions/<ID>/profile.json, 회차 폴더의 quiz.py 와 <문항>.py) GUI 로 풀든 파일을 직접 고치든
PR 리뷰·CI 분석·현황판이 똑같이 동작함.

오류는 전부 SessionError 로 올림. 문구를 사용자에게 그대로 보여 줄 수 있음.
"""
import ast
import os
import re
import shutil
import threading

import adaptive
import mdlite
import study

UNSAFE_RE = re.compile("[\x00\ud800-\udfff]")  # 파일에 쓸 수 없는 글자(NUL, 짝 없는 서러게이트)
LABEL_RE = re.compile(r"\*\*(\d+)번\*\*")
ASSIGN_RE = re.compile(r"^([A-Za-z_]\w*)\s*=\s*(.+?)\s*(?:#.*)?$")


class SessionError(Exception):
    """사용자에게 그대로 보여 줄 수 있는 오류."""


# 사용자

def valid_user(name):
    return bool(name) and bool(study.USER_RE.fullmatch(name))


def saved_user():
    """환경 변수 STUDY_USER, .study_user 파일 순으로 찾음. 없으면 None."""
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


# 도우미

def clean_text(text):
    return UNSAFE_RE.sub("", str(text)).replace("\r\n", "\n").replace("\r", "\n")


def choice_count(body):
    """객관식 본문의 보기 수: 마지막 번호 목록의 항목 수, 없으면 `**N번**` 문단의 수. 못 세면 0."""
    last, labeled = 0, 0
    for block in mdlite.parse(body):
        if block["t"] == "ol":
            last = len(block["items"])
        elif block["t"] == "para" and LABEL_RE.fullmatch(block["text"].strip()):
            labeled += 1
    return last or labeled


def literal(value):
    """quiz.py 에 적을 파이썬 리터럴. 여러 줄 문자열은 PR 에서 읽기 좋게 삼중 따옴표로 적음(되읽은 값이 같을 때만)."""
    if isinstance(value, str) and "\n" in value and '"""' not in value and "\\" not in value:
        text = '"""\n%s\n"""' % value.strip("\n")
        try:
            if ast.literal_eval(text).strip("\n") == value.strip("\n"):
                return text
        except (ValueError, SyntaxError):
            pass
    return repr(value)


def clean_quiz_value(kind, value):
    """화면에서 온 값을 저장용으로 다듬음. 빈 값은 None."""
    if value is None:
        return None
    if kind == "choice":
        picked = sorted({int(v) for v in value}) if isinstance(value, (list, tuple, set)) else [int(value)]
        if not picked:
            return None
        return picked[0] if len(picked) == 1 else picked
    text = clean_text(value)
    if kind == "short":
        text = text.strip()
    return text if text.strip() else None


def answer_text(q):
    if q["type"] == "choice":
        return ", ".join("%d번" % n for n in q["answer"])
    if q["type"] == "output":
        return q["answer"].rstrip("\n")
    return " 또는 ".join(q["answer"])


def salvage_quiz(text):
    """깨진 quiz.py 에서 한 줄짜리 답 가운데 읽히는 것만 건짐."""
    answers = {}
    for line in text.replace("\r\n", "\n").split("\n"):
        m = ASSIGN_RE.match(line)
        if not m:
            continue
        try:
            answers[m.group(1)] = ast.literal_eval(m.group(2))
        except (ValueError, SyntaxError):
            pass
    return answers


# 세션

class Session:
    def __init__(self, user):
        if not valid_user(user):
            raise SessionError("ID 가 올바르지 않습니다: %r" % (user,))
        self.user = user
        self._lock = threading.RLock()  # 화면 스레드와 채점 워커가 프로필을 동시에 건드리지 않게 함
        adaptive.clear_cache()  # 문제 받기 뒤에 새로 만든 세션은 은행을 다시 읽음
        self.cat = adaptive.catalog()
        self.prof = None
        self._reload()

    def _reload(self):
        """다른 창이나 터미널에서 바뀐 기록을 덮어쓰지 않게 프로필을 디스크에서 다시 읽음."""
        try:
            prof = adaptive.load_profile(self.user)
            prof["rounds"], prof["attempts"], prof["seed"]  # 필수 항목 확인
        except (ValueError, KeyError, TypeError, OSError) as error:
            raise SessionError("풀이 기록(profile.json)을 읽을 수 없습니다: %s" % error)
        self.prof = prof

    # 회차 찾기·만들기

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
        """풀 회차가 없으면 만듦(처음이면 진단). (회차 | None, 새로 만들었는지) 반환.
        전 단원을 심화까지 끝내 더 낼 문항이 없으면 회차 자리에 None 을 돌려줌."""
        with self._lock:
            self._reload()
            rnd = self.latest()
            if rnd is None:
                return self._start(adaptive.build_diagnostic(self.prof, self.cat)), True
            if not rnd.get("completed_at"):
                return rnd, False
            nxt = adaptive.build_round(self.prof, self.cat)
            if nxt is None:
                return None, False
            return self._start(nxt), True

    # 화면에 줄 모양

    def _keys(self, rnd):
        return [k for k in rnd["items"] if k in self.cat]  # 은행에서 사라진 문항은 건너뜀

    def quiz_problem(self, rid):
        """답안지(quiz.py)를 읽을 수 없으면 그 이유, 괜찮으면 None."""
        path = os.path.join(self.folder(rid), "quiz.py")
        if not os.path.isfile(path):
            return None
        try:
            return study.parse_quiz_answers(path)[1]
        except (OSError, ValueError) as error:  # 인코딩이 깨진 파일 등
            return "quiz.py 를 읽을 수 없습니다: %s" % error

    def _quiz_answers(self, rid):
        """답안지의 답. 읽을 수 없으면 오류를 올림. 빈 답으로 치면 저장할 때 나머지 답이 지워짐."""
        problem = self.quiz_problem(rid)
        if problem:
            raise SessionError("답안지를 읽을 수 없습니다. %s 답안지 복구를 먼저 해 주세요." % problem)
        path = os.path.join(self.folder(rid), "quiz.py")
        if not os.path.isfile(path):
            return {}
        answers, _ = study.parse_quiz_answers(path)
        return {k: (None if v is study.UNPARSED else v) for k, v in answers.items()}

    def repair_quiz(self, rid):
        """깨진 답안지를 quiz.py.bak 으로 보관하고, 건진 답만 남겨 새로 씀. 건진 답의 수를 돌려줌."""
        rnd = self._round(rid)
        path = os.path.join(self.folder(rnd["id"]), "quiz.py")
        saved = {}
        if os.path.isfile(path):
            shutil.copyfile(path, path + ".bak")
            with open(path, encoding="utf-8", errors="replace") as f:
                saved = salvage_quiz(f.read())
        names = {adaptive.fname_of(k): self.cat[k] for k in self._keys(rnd) if self.cat[k]["kind"] == "quiz"}
        answers = {}
        for name, value in saved.items():
            if name in names:
                try:
                    answers[name] = clean_quiz_value(names[name]["type"], value)
                except (TypeError, ValueError):
                    pass
        with self._lock:
            self._write_quiz(rnd, answers)
        return sum(1 for v in answers.values() if v is not None)

    def _code_path(self, rid, name):
        return os.path.join(self.folder(rid), name + ".py")

    def _item_view(self, rnd, key, number, quiz_answers):
        it = self.cat[key]
        name = adaptive.fname_of(key)
        view = {
            "id": name, "key": key, "no": number, "unit": it["unit"], "unit_title": it["unit_title"],
            "kind": it["kind"], "type": it["type"], "level": it["level"], "points": it["points"],
            "result": (rnd.get("results") or {}).get(key),  # None | ok | wrong | skipped. 채점한 뒤에만 값이 있음
            "retest": key in (rnd.get("retest") or []),
        }
        if it["kind"] == "quiz":
            body = adaptive.quiz_section(it["set"], it["q"]["id"])
            value = quiz_answers.get(name)
            if isinstance(value, str):
                value = value.strip("\n")  # 삼중 따옴표로 적힌 답의 앞뒤 줄바꿈
            view.update(type_label=study.QTYPE_LABEL[it["type"]], title=study.QTYPE_LABEL[it["type"]],
                        body_md=body, answer=value, answered=value not in (None, "", []))
            if it["type"] == "choice":
                view["choices"] = choice_count(body)  # 0 이면 화면은 번호 입력칸을 보여 줌
                view["multi"] = len(it["q"]["answer"]) > 1  # 복수 정답 문항은 본문에도 '모두 고르세요'가 있음(은행 검증)
        else:
            spec = it["spec"]
            starter = study.read_text(os.path.join(spec["dir"], "starter.py"))
            path = self._code_path(rnd["id"], name)
            source = study.read_text(path) if os.path.isfile(path) else starter
            view.update(type_label=study.TYPE_LABEL[it["type"]], title=spec["title"],
                        body_md=adaptive.problem_body(spec), starter=starter, answer=source,
                        answered=study.norm_out(source) != study.norm_out(starter),
                        examples=self._examples(spec))
        return view

    def _round_summary(self, rnd):
        return {
            "id": rnd["id"], "title": adaptive.round_title(rnd), "kind": rnd["kind"],
            "size": len(self._keys(rnd)), "score": rnd.get("score"), "first_score": rnd.get("first_score"),
            "completed": bool(rnd.get("completed_at")), "avg_level": rnd.get("avg_level"),
            "size_reason": rnd.get("size_reason", ""), "unanswered": rnd.get("unanswered"),
            "graded": bool(rnd.get("results")),
        }

    def open_round(self, rid=None):
        """회차를 화면용 dict 로 돌려줌. items 는 문제지 순서. 답안지가 깨졌으면 SessionError."""
        rnd = self._round(rid)
        answers = self._quiz_answers(rnd["id"])
        view = self._round_summary(rnd)
        view["folder"] = self.folder(rnd["id"])
        view["items"] = [self._item_view(rnd, k, i, answers) for i, k in enumerate(self._keys(rnd), 1)]
        return view

    def rounds(self):
        return [self._round_summary(r) for r in self.prof["rounds"]]

    # 답 저장 (자동 저장)

    def _find(self, rid, item_id):
        rnd = self._round(rid)
        for key in self._keys(rnd):
            if adaptive.fname_of(key) == item_id:
                return rnd, key, self.cat[key]
        raise SessionError("문항 %s 를 찾을 수 없습니다." % item_id)

    def set_answer(self, rid, item_id, value):
        """답을 파일에 바로 저장함. 채점·기록은 하지 않음."""
        rnd, key, it = self._find(rid, item_id)
        with self._lock:
            if it["kind"] == "code":
                text = clean_text(value or "")
                if text and not text.endswith("\n"):
                    text += "\n"
                study.write_text(self._code_path(rnd["id"], item_id), text)
                return
            answers = self._quiz_answers(rnd["id"])
            try:
                answers[item_id] = clean_quiz_value(it["type"], value)
            except (TypeError, ValueError):
                raise SessionError("답 형식이 올바르지 않습니다: %r" % (value,))
            self._write_quiz(rnd, answers)

    def _write_quiz(self, rnd, answers):
        lines = ["# %s 퀴즈 답안지입니다. 문제는 같은 폴더의 README.md 에 있습니다." % adaptive.round_title(rnd),
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
        """코드 문제를 시작 코드로 되돌림."""
        rnd, key, it = self._find(rid, item_id)
        if it["kind"] != "code":
            raise SessionError("코드 문제만 되돌릴 수 있습니다.")
        starter = study.read_text(os.path.join(it["spec"]["dir"], "starter.py"))
        with self._lock:
            study.write_text(self._code_path(rnd["id"], item_id), starter)
        return starter

    # 코드 실행 (예시만, 기록 없음)

    @staticmethod
    def _examples(spec):
        """'코드 실행'이 돌릴 테스트 수 = 문제 본문에 예시로 보이는 앞쪽 테스트(problem.json 의 examples)."""
        return max(1, min(int(spec.get("examples", 1)), len(spec["cases"])))

    def try_run(self, rid, item_id):
        """저장된 코드를 예시 테스트로만 돌려 봄(시험의 '실행하기'). 숙달 판정에는 반영하지 않음."""
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
                return {"message": problem, "cases": [], "ran": 0, "examples": self._examples(spec)}
        run = study.run_cases(spec, path, limit=self._examples(spec))
        message = run["fatal"] or ""
        if not message and run["timed_out"]:
            message = "시간 초과: %s초 안에 끝나지 않았습니다. 무한 루프가 없는지 확인하세요." % run["timeout"]
        cases = [{"ok": c["ok"], "input": c.get("input", ""), "want": c.get("want", ""), "got": c.get("got", ""),
                  "printed": c.get("printed", "")} for c in run["cases"]]
        return {"message": message, "cases": cases, "ran": len(cases), "examples": self._examples(spec)}

    # 채점 · 기록 · 다음 회차

    def pending(self, rid=None):
        """제출 확인 대화상자용: 아직 안 푼 문항 번호와 전체 문항 수."""
        view = self.open_round(rid)
        return {"total": len(view["items"]), "blank": [it["no"] for it in view["items"] if not it["answered"]]}

    def grade(self, rid=None, finalize=False):
        """회차를 채점하고 첫 시도를 기록함. 다 풀었으면 회차를 끝내고 다음 회차를 만듦.
        finalize=True 면 시험처럼 미응답을 오답으로 확정함(화면의 '회차 제출').
        아무것도 풀지 않았으면 기록하지 않고 untouched=True 로 돌려줌.
        답안지가 깨져 있으면 아무것도 기록하지 않고 SessionError."""
        with self._lock:
            self._reload()
        rnd = self._round(rid)
        self._quiz_answers(rnd["id"])  # 깨진 답안지를 '전부 오답'으로 기록하지 않음
        items = adaptive.grade_round(self.user, rnd, self.cat)  # 코드 실행은 오래 걸려서 잠금 밖에서 함
        untouched = all(it["state"] == "blank" for it in items) and not rnd.get("results")
        if untouched and not finalize:
            return self._result(rnd, items, untouched=True)
        with self._lock:
            adaptive.record(self.prof, rnd, items, finalize=finalize)
            completed_now, next_id = False, None
            if not rnd.get("completed_at") and rnd["unanswered"] == 0:
                rnd["completed_at"] = adaptive.now()
                rnd["first_score"] = rnd["score"]  # 다음 회차 크기는 이 점수로 정함. 나중에 고쳐서 다시 채점해도 바꾸지 않음
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

    # 해설

    def explain(self, rid, item_id):
        """정답·해설. 같은 단원의 남은 문항을 해설 없이 첫 시도로 풀도록 회차를 제출한 뒤에만 돌려줌.
        explain 은 퀴즈면 한 문단의 글(인라인 코드만), 코드 문제면 마크다운 문서임(markdown=True)."""
        rnd, key, it = self._find(rid, item_id)
        if not rnd.get("completed_at"):
            raise SessionError("회차를 제출한 뒤에 해설을 볼 수 있습니다.")
        if it["kind"] == "quiz":
            q = it["q"]
            return {"kind": "quiz", "answer": answer_text(q), "explain": q.get("explain", ""), "markdown": False, "solution": ""}
        secrets, pid = it["set"]["secrets"], it["spec"]["id"]
        return {"kind": "code", "answer": "", "explain": secrets.get(pid + "/explain.md", "").strip(), "markdown": True,
                "solution": secrets.get(pid + "/solution.py", "").rstrip("\n")}

    # 현황

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
