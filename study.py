#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ROKEY 파이썬 스터디 — 문제 받기 · 채점 · 해설 도구.

표준 라이브러리만 사용합니다(별도 설치 없음).
사용법: python study.py --help  (자세한 흐름은 README.md)
"""
import argparse
import ast
import base64
import contextlib
import datetime
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import traceback
import zlib

ROOT = os.path.dirname(os.path.abspath(__file__))
PROBLEMS_DIR = os.path.join(ROOT, "problems")
SUBMISSIONS_DIR = os.path.join(ROOT, "submissions")
USER_FILE = os.path.join(ROOT, ".study_user")

PASS_RATIO = 0.8  # 세트 통과 기준(득점률)
DEFAULT_TIMEOUT = 5  # 문제 1개(모든 테스트 합계)의 제한 시간(초)
BLANK_RE = re.compile(r"_{4,}")  # 빈칸 표시: 밑줄 4개 이상
USER_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*")
KIND_ORDER = {"session": 0, "codetest": 1, "mock": 2}
TYPE_LABEL = {"fill": "빈칸 채우기", "return": "반환값", "print": "출력"}
QTYPE_LABEL = {"choice": "객관식", "output": "출력 예측", "short": "단답"}
MARK = {"ok": "✅", "wrong": "❌", "blank": "⬜"}
SECRET_QUIZ = "quiz_key.json"
SECRET_PROBLEM_FILES = ("solution.py", "explain.md")


# ───────────────────────── 공통 도우미 ─────────────────────────

def die(message):
    print("오류: " + message, file=sys.stderr)
    sys.exit(1)


def read_text(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write_text(path, text):
    """임시 파일에 쓴 뒤 바꿔치기한다 — 저장 도중 강제 종료돼도 반쯤 쓰인 파일이 남지 않는다."""
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    tmp = "%s.tmp%d" % (path, os.getpid())
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)


def read_json(path):
    return json.loads(read_text(path))


def natural_key(text):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", text)]


def norm_out(text, strip_leading=False):
    """비교용 정규화: 줄 끝 공백과 맨 끝 빈 줄은 무시하고, 나머지는 그대로 비교한다."""
    lines = [ln.rstrip() for ln in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    if strip_leading:
        while lines and lines[0] == "":
            lines.pop(0)
    return "\n".join(lines)


def clip(text, max_lines=12, max_chars=600):
    lines = text.split("\n")
    if len(lines) > max_lines:
        lines = lines[:max_lines] + ["… (이하 생략)"]
    text = "\n".join(lines)
    return text if len(text) <= max_chars else text[:max_chars] + " … (이하 생략)"


def indent(text, prefix="    "):
    return "\n".join(prefix + ln for ln in text.split("\n"))


# ───────────────────────── 문제 은행 ─────────────────────────

def all_set_ids():
    """problems/ 아래에서 meta.json 이 있는 폴더를 세트로 인식한다(폴더만 추가하면 확장됨)."""
    ids = []
    if os.path.isdir(PROBLEMS_DIR):
        for name in os.listdir(PROBLEMS_DIR):
            if os.path.isfile(os.path.join(PROBLEMS_DIR, name, "meta.json")):
                ids.append(name)

    def key(sid):
        kind = read_json(os.path.join(PROBLEMS_DIR, sid, "meta.json")).get("kind", "session")
        return (KIND_ORDER.get(kind, 9), natural_key(sid))

    return sorted(ids, key=key)


def resolve_set(token):
    """'3', 's3', 's03', 'm1' 같은 입력을 세트 ID 로 바꾼다."""
    ids = all_set_ids()
    if token in ids:
        return token
    m = re.fullmatch(r"s?(\d+)", token)
    if m and "s%02d" % int(m.group(1)) in ids:
        return "s%02d" % int(m.group(1))
    die("'%s' 세트를 찾을 수 없습니다. `python study.py list` 로 목록을 확인하세요." % token)


def problem_ids(set_dir):
    names = [n for n in os.listdir(set_dir) if os.path.isfile(os.path.join(set_dir, n, "problem.json"))]
    return sorted(names, key=natural_key)


def seal_blob(files):
    raw = json.dumps(files, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return base64.b64encode(zlib.compress(raw, 9)).decode("ascii")


def unseal_blob(blob):
    return json.loads(zlib.decompress(base64.b64decode(blob)).decode("utf-8"))


def plain_secret_paths(set_dir):
    """세트 안에 평문으로 놓인 정답·해설 파일의 상대경로 목록."""
    rels = []
    if os.path.isfile(os.path.join(set_dir, SECRET_QUIZ)):
        rels.append(SECRET_QUIZ)
    for pid in problem_ids(set_dir):
        for name in SECRET_PROBLEM_FILES:
            if os.path.isfile(os.path.join(set_dir, pid, name)):
                rels.append(pid + "/" + name)
    return rels


def load_secrets(set_dir):
    """정답·해설을 {상대경로: 내용} 으로 반환. sealed.json 위에 평문 파일(출제자 작업본)을 덮어쓴다."""
    files = {}
    sealed = os.path.join(set_dir, "sealed.json")
    if os.path.isfile(sealed):
        files.update(unseal_blob(read_json(sealed)["blob"]))
    for rel in plain_secret_paths(set_dir):
        files[rel] = read_text(os.path.join(set_dir, *rel.split("/")))
    return files


def load_set(sid):
    set_dir = os.path.join(PROBLEMS_DIR, sid)
    secrets = load_secrets(set_dir)
    has_quiz = os.path.isfile(os.path.join(set_dir, "quiz.md")) and SECRET_QUIZ in secrets
    questions = json.loads(secrets[SECRET_QUIZ])["questions"] if has_quiz else []
    problems = []
    for pid in problem_ids(set_dir):
        spec = read_json(os.path.join(set_dir, pid, "problem.json"))
        spec["id"] = pid
        spec["dir"] = os.path.join(set_dir, pid)
        problems.append(spec)
    return {
        "id": sid,
        "dir": set_dir,
        "meta": read_json(os.path.join(set_dir, "meta.json")),
        "questions": questions,
        "problems": problems,
        "secrets": secrets,
    }


def set_title(s):
    title = s["meta"].get("title", s["id"])
    m = re.fullmatch(r"s(\d+)", s["id"])
    return "%d차시 · %s" % (int(m.group(1)), title) if m else title


# ───────────────────────── 퀴즈 채점 ─────────────────────────

UNPARSED = object()


def parse_quiz_answers(path):
    """quiz.py 의 `Q1 = 값` 대입문을 읽는다. 코드를 실행하지 않고 리터럴만 해석한다."""
    try:
        tree = ast.parse(read_text(path))
    except SyntaxError as e:
        return None, "quiz.py %s번째 줄에 문법 오류가 있습니다." % e.lineno
    answers = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                answers[node.targets[0].id] = ast.literal_eval(node.value)
            except ValueError:
                answers[node.targets[0].id] = UNPARSED
    return answers, None


def check_quiz_answer(q, value):
    """'ok' | 'wrong' | 'blank' 를 반환한다. 부분 점수는 없다."""
    if value is None or value == "" or value == []:
        return "blank"
    if value is UNPARSED:
        return "wrong"
    if q["type"] == "choice":
        picked = list(value) if isinstance(value, (list, tuple, set)) else [value]
        if not all(isinstance(v, int) and not isinstance(v, bool) for v in picked):
            return "wrong"
        return "ok" if set(picked) == set(q["answer"]) else "wrong"
    if q["type"] == "output":
        return "ok" if norm_out(str(value), True) == norm_out(q["answer"], True) else "wrong"

    def canon(text):
        text = str(text).strip()
        if q.get("ignore_space"):
            text = re.sub(r"\s+", "", text)
        if q.get("ignore_case"):
            text = text.lower()
        return text

    return "ok" if canon(value) in {canon(a) for a in q["answer"]} else "wrong"


# ───────────────────────── 코드 문제 채점 ─────────────────────────

def check_fill(template, source):
    """빈칸 채우기: 빈칸 이외의 부분을 건드리지 않았는지 확인한다. 문제가 있으면 안내 문구를 반환."""
    t_lines = norm_out(template).split("\n")
    s_lines = norm_out(source).split("\n")
    if BLANK_RE.search("\n".join(s_lines)):
        return "아직 채우지 않은 빈칸(____)이 있습니다."
    if len(t_lines) != len(s_lines):
        return "줄 수가 달라졌습니다. 빈칸(____)만, 그 줄 안에서 채워 주세요."
    for number, (t, s) in enumerate(zip(t_lines, s_lines), 1):
        pattern = "(.+?)".join(re.escape(part) for part in BLANK_RE.split(t))
        if not re.fullmatch(pattern, s):
            return "%d번째 줄에서 빈칸 이외의 부분이 바뀌었습니다.\n원래 줄: %s" % (number, t.strip())
    return None


def run_cases(spec, source_path, limit=None):
    """제출 파일을 별도 프로세스에서 실행해 테스트별 결과를 돌려준다.
    반환: {"fatal": 문법 오류 등 | None, "cases": [{ok, input, want, got, detail?}], "timed_out": bool, "total": 실행하려던 수, "stderr": str}
    limit 를 주면 앞의 limit 개만 실행한다(화면의 '코드 실행' = 예시만)."""
    timeout = spec.get("timeout", DEFAULT_TIMEOUT)
    cases = spec["cases"] if limit is None else spec["cases"][:limit]
    with tempfile.TemporaryDirectory(prefix="study_") as tmp:
        job = {
            "source": os.path.abspath(source_path),
            "mode": spec["mode"],
            "cases": cases,
            "workdir": tmp,
            "result": os.path.join(tmp, "result.json"),
        }
        job_path = os.path.join(tmp, "job.json")
        write_text(job_path, json.dumps(job, ensure_ascii=False))
        env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1")
        timed_out, stderr = False, ""
        try:
            proc = subprocess.run(
                [sys.executable, os.path.abspath(__file__), "_run", job_path],
                cwd=tmp, env=env, timeout=timeout,
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
            )
            stderr = proc.stderr.decode("utf-8", "replace")
        except subprocess.TimeoutExpired:
            timed_out = True
        result = read_json(job["result"]) if os.path.isfile(job["result"]) else {"fatal": None, "cases": []}
    return {"fatal": result.get("fatal"), "cases": result["cases"], "timed_out": timed_out,
            "total": len(cases), "stderr": stderr, "timeout": timeout}


def run_problem(spec, source_path):
    """모든 테스트를 돌린다. (통과 여부, 통과 수, 실패 설명) 반환."""
    run = run_cases(spec, source_path)
    if run["fatal"]:
        return False, 0, run["fatal"]
    cases = run["cases"]
    passed = sum(1 for c in cases if c["ok"])
    first_fail = next((c for c in cases if not c["ok"]), None)
    if first_fail:
        return False, passed, first_fail["detail"]
    if run["timed_out"]:
        return False, passed, (
            "시간 초과 — %d번째 테스트가 %s초 안에 끝나지 않았습니다. 무한 루프가 없는지 확인하세요."
            % (len(cases) + 1, run["timeout"])
        )
    if len(cases) < run["total"]:
        return False, passed, "채점기 내부 오류입니다. 스터디장에게 알려 주세요.\n" + clip(run["stderr"].strip())
    return True, run["total"], ""


def grade_problem(spec, path):
    """('ok' | 'wrong' | 'blank', 설명) 반환. 시작 코드 그대로면 미제출(blank)로 본다."""
    if not os.path.isfile(path):
        return "blank", ""
    source = read_text(path)
    starter = read_text(os.path.join(spec["dir"], "starter.py"))
    if norm_out(source) == norm_out(starter):
        return "blank", ""
    if spec["type"] == "fill":
        problem = check_fill(starter, source)
        if problem:
            return "wrong", problem
    ok, passed, detail = run_problem(spec, path)
    if ok:
        return "ok", ""
    return "wrong", "테스트 %d/%d 통과\n%s" % (passed, len(spec["cases"]), detail)


# ── 여기부터는 별도 프로세스(_run)에서만 실행되는 채점 러너 ──

class _Capture(io.StringIO):
    LIMIT = 1000000

    def write(self, s):
        if self.tell() + len(s) > self.LIMIT:
            raise RuntimeError("출력이 너무 많습니다. 반복문이 끝나지 않고 계속 출력하는지 확인하세요.")
        return super().write(s)


def _strict_eq(a, b):
    """자료형까지 같아야 정답(예: 3 과 3.0, True 와 1 은 다르다). 실수는 미세 오차 허용."""
    if type(a) is not type(b):
        return False
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(_strict_eq(x, y) for x, y in zip(a, b))
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(_strict_eq(a[k], b[k]) for k in a)
    if isinstance(a, float):
        return abs(a - b) <= 1e-9 * max(1.0, abs(a), abs(b))
    return a == b


def _error_text(error, name):
    line = None
    for frame in traceback.extract_tb(error.__traceback__):
        if frame.filename == name:
            line = frame.lineno
    where = " (%d번째 줄)" % line if line else ""
    return "%s: %s%s" % (type(error).__name__, error, where)


def _case_label(mode, case):
    if mode == "io":
        stdin = case.get("stdin", "")
        return "입력:\n" + indent(clip(stdin.rstrip("\n"))) if stdin else "입력: (없음)"
    if mode == "exec":
        return "테스트 코드:\n" + indent(clip(case["code"].rstrip("\n")))
    return case["call"]


def _case_want(mode, case):
    if mode == "call":
        return repr(ast.literal_eval(case["expected"]))
    return clip(norm_out(case.get("stdout", ""))) or "(출력 없음)"


def _run_case(code, name, mode, case):
    stdin = io.StringIO(case.get("stdin", ""))

    def fake_input(prompt=""):  # 안내 문구(prompt)는 출력에 포함하지 않는다
        line = stdin.readline()
        if line == "":
            raise EOFError("input() 을 호출했지만 더 읽을 입력이 없습니다")
        return line.rstrip("\n")

    out = _Capture()
    ns = {"__name__": "__main__" if mode == "io" else "__study__", "input": fake_input}
    value = None
    real_stdin = sys.stdin
    sys.stdin = stdin
    try:
        with contextlib.redirect_stdout(out):
            exec(code, ns)
            if mode != "io":  # 함수·클래스 정의 단계의 출력은 버린다
                out.seek(0)
                out.truncate()
            if mode == "call":
                value = eval(case["call"], ns)
            elif mode == "exec":
                exec(compile(case["code"], "<테스트 코드>", "exec"), ns)
    except SystemExit:
        pass
    except BaseException as error:  # 학생 코드의 어떤 오류든 '오답 + 설명'으로 돌려준다
        message = "실행 중 오류: " + _error_text(error, name)
        return {"ok": False, "detail": _case_label(mode, case) + "\n" + message,
                "input": _case_label(mode, case), "want": _case_want(mode, case), "got": message}
    finally:
        sys.stdin = real_stdin

    shown = {"input": _case_label(mode, case), "want": _case_want(mode, case)}  # 화면 표시용(판정에는 쓰지 않는다)
    if mode == "call":
        expected = ast.literal_eval(case["expected"])
        shown["got"] = clip(repr(value))
        if _strict_eq(value, expected):
            return dict(shown, ok=True)
        note = ""
        if type(value) is not type(expected):
            note = "\n  (자료형이 다릅니다: 기대 %s, 실제 %s)" % (type(expected).__name__, type(value).__name__)
        return dict(shown, ok=False, detail="%s\n  기대한 반환값: %r\n  실제 반환값: %s%s"
                    % (case["call"], expected, clip(repr(value)), note))

    got, want = norm_out(out.getvalue()), norm_out(case.get("stdout", ""))
    shown["got"] = clip(got) or "(출력 없음)"
    if got != want:
        return dict(shown, ok=False, detail="%s\n기대한 출력:\n%s\n실제 출력:\n%s" % (
            _case_label(mode, case), indent(clip(want) or "(출력 없음)"), indent(clip(got) or "(출력 없음)")))
    for fname, content in (case.get("expect_files") or {}).items():
        if not os.path.isfile(fname):
            return dict(shown, ok=False, got="파일 '%s' 없음" % fname,
                        detail="%s\n파일 '%s' 이(가) 만들어지지 않았습니다." % (_case_label(mode, case), fname))
        actual = norm_out(read_text(fname))
        if actual != norm_out(content):
            return dict(shown, ok=False, got="파일 '%s' 내용이 다름" % fname,
                        detail="%s\n파일 '%s' 의 내용이 다릅니다.\n기대한 내용:\n%s\n실제 내용:\n%s" % (
                            _case_label(mode, case), fname, indent(clip(norm_out(content)) or "(빈 파일)"),
                            indent(clip(actual) or "(빈 파일)")))
    return dict(shown, ok=True)


def _child_main(job_path):
    job = read_json(job_path)
    results = []

    def save(fatal=None):
        write_text(job["result"], json.dumps({"fatal": fatal, "cases": results}, ensure_ascii=False))

    name = os.path.basename(job["source"])
    try:
        code = compile(read_text(job["source"]), name, "exec")
    except SyntaxError as error:
        save("문법 오류(%s) — %s번째 줄: %s" % (type(error).__name__, error.lineno, error.msg))
        return
    save()
    for index, case in enumerate(job["cases"]):
        work = os.path.join(job["workdir"], "case%d" % index)
        os.makedirs(work)
        os.chdir(work)  # 파일 문제는 테스트마다 빈 폴더에서 실행
        for fname, content in (case.get("files") or {}).items():
            write_text(os.path.join(work, fname), content)
        results.append(_run_case(code, name, job["mode"], case))
        save()


# ───────────────────────── 세트 채점 · 출력 ─────────────────────────

def grade_set(s, sub_dir):
    """세트 하나를 채점해 항목 목록을 반환한다. 항목: id, label, points, earned, state, detail"""
    items = []

    def add(item_id, label, points, state, detail=""):
        items.append({"id": item_id, "label": label, "points": points,
                      "earned": points if state == "ok" else 0, "state": state, "detail": detail})

    if s["questions"]:
        quiz_path = os.path.join(sub_dir, "quiz.py")
        answers, error = ({}, None)
        if os.path.isfile(quiz_path):
            answers, error = parse_quiz_answers(quiz_path)
        for q in s["questions"]:
            if error:
                add(q["id"], QTYPE_LABEL[q["type"]], q["points"], "wrong", error)
            else:
                add(q["id"], QTYPE_LABEL[q["type"]], q["points"], check_quiz_answer(q, answers.get(q["id"])))
    for p in s["problems"]:
        state, detail = grade_problem(p, os.path.join(sub_dir, p["id"] + ".py"))
        add(p["id"], "%s · %s" % (TYPE_LABEL[p["type"]], p["title"]), p["points"], state, detail)
    return items


def totals(items):
    earned = sum(i["earned"] for i in items)
    total = sum(i["points"] for i in items)
    return earned, total, (earned / total if total else 0.0)


def elapsed_note(s, sub_dir):
    limit = s["meta"].get("time_limit_min")
    started = os.path.join(sub_dir, ".started")
    if not limit or not os.path.isfile(started):
        return ""
    begin = datetime.datetime.fromisoformat(read_text(started).strip())
    minutes = int((datetime.datetime.now() - begin).total_seconds() // 60)
    return "경과 %d분 / 제한 %d분%s" % (minutes, limit, " — 시간 초과!" if minutes > limit else "")


def print_report(s, items, sub_dir):
    print("\n[%s] %s" % (s["id"], set_title(s)))
    for it in items:
        print("  %s %-4s %s  (%d/%d점)" % (MARK[it["state"]], it["id"], it["label"], it["earned"], it["points"]))
        if it["detail"]:
            print(indent(it["detail"], "         "))
    earned, total, ratio = totals(items)
    verdict = "통과" if ratio >= PASS_RATIO else "통과 기준 %d%%" % int(PASS_RATIO * 100)
    print("  ── 합계 %d/%d점 (%d%%) · %s" % (earned, total, round(ratio * 100), verdict))
    note = elapsed_note(s, sub_dir)
    if note:
        print("  ── " + note)
    wrong = [it["id"] for it in items if it["state"] == "wrong"]
    if wrong:
        target = wrong[0] if "_" in wrong[0] else "%s %s" % (s["id"], wrong[0])  # 라운드 문항은 s03_Q4 꼴
        print("  틀린 문제는 다시 풀어 본 뒤 해설 확인: python study.py explain %s" % target)


def started_sets(user):
    base = os.path.join(SUBMISSIONS_DIR, user)
    return [sid for sid in all_set_ids() if os.path.isdir(os.path.join(base, sid))]


def grade_user(user, set_ids=None):
    """[(세트, 항목 목록)] — 시작한 세트만 채점한다."""
    graded = []
    for sid in (set_ids or started_sets(user)):
        s = load_set(sid)
        graded.append((s, grade_set(s, os.path.join(SUBMISSIONS_DIR, user, sid))))
    return graded


def render_markdown(user, graded):
    """CI(PR 코멘트·요약)용 마크다운 채점표."""
    lines = ["### `%s` 채점 결과" % user, ""]
    if not graded:
        return "\n".join(lines + ["아직 시작한 세트가 없습니다.", ""])
    lines += ["| 세트 | 점수 | 득점률 | 통과 | 틀린 문항 |", "|---|---|---|---|---|"]
    all_earned = all_total = 0
    for s, items in graded:
        earned, total, ratio = totals(items)
        all_earned += earned
        all_total += total
        wrong = ", ".join(it["id"] for it in items if it["state"] == "wrong") or "-"
        blank = sum(1 for it in items if it["state"] == "blank")
        if blank:
            wrong += " (미응답 %d)" % blank
        lines.append("| %s | %d/%d | %d%% | %s | %s |" % (
            set_title(s), earned, total, round(ratio * 100), "✅" if ratio >= PASS_RATIO else "—", wrong))
    pct = round(all_earned / all_total * 100) if all_total else 0
    lines += ["", "**합계 %d/%d점 (%d%%)** · 세트 통과 기준 %d%%" % (all_earned, all_total, pct, int(PASS_RATIO * 100)), ""]
    return "\n".join(lines)


# ───────────────────────── 명령 ─────────────────────────

def all_users():
    if not os.path.isdir(SUBMISSIONS_DIR):
        return []
    return sorted(n for n in os.listdir(SUBMISSIONS_DIR)
                  if os.path.isdir(os.path.join(SUBMISSIONS_DIR, n)) and USER_RE.fullmatch(n))


def current_user(args):
    user = getattr(args, "user", None) or os.environ.get("STUDY_USER")
    if not user and os.path.isfile(USER_FILE):
        user = read_text(USER_FILE).strip()
    if not user and sys.stdin.isatty():
        print("처음이시군요. 내 깃허브 ID 를 입력하세요 (영문·숫자·-·_).")
        user = input("> ").strip()
        if not USER_RE.fullmatch(user):
            die("ID 는 영문·숫자·-·_ 만 쓸 수 있습니다.")
        os.makedirs(os.path.join(SUBMISSIONS_DIR, user), exist_ok=True)
        write_text(USER_FILE, user + "\n")
        print("내 풀이 폴더: submissions/%s/\n" % user)
    if not user:
        die("먼저 `python study.py init <내 깃허브 ID>` 로 내 풀이 폴더를 만들어 주세요.")
    if not USER_RE.fullmatch(user):
        die("ID 는 영문·숫자·-·_ 만 쓸 수 있습니다: %r" % user)
    return user


def cmd_init(args):
    if not USER_RE.fullmatch(args.id):
        die("ID 는 영문·숫자·-·_ 만 쓸 수 있습니다(깃허브 ID 권장).")
    os.makedirs(os.path.join(SUBMISSIONS_DIR, args.id), exist_ok=True)
    write_text(USER_FILE, args.id + "\n")
    print("내 풀이 폴더: submissions/%s/" % args.id)
    print("다음 단계: python study.py list  →  python study.py start 0")


def cmd_list(args):
    user = None
    if getattr(args, "user", None) or os.environ.get("STUDY_USER") or os.path.isfile(USER_FILE):
        user = current_user(args)
    print("세트 목록 (start/grade 에는 차시 번호 또는 ID 를 씁니다)")
    for sid in all_set_ids():
        s = load_set(sid)
        points = sum(q["points"] for q in s["questions"]) + sum(p["points"] for p in s["problems"])
        mine = ""
        if user and os.path.isdir(os.path.join(SUBMISSIONS_DIR, user, sid)):
            mine = " · 진행 중"
        week = s["meta"].get("week")
        print("  %-4s %s — 퀴즈 %d문항, 코드 %d문제, %d점%s%s" % (
            sid, set_title(s), len(s["questions"]), len(s["problems"]), points,
            " (%s주차)" % week if week else "", mine))


def quiz_stub(s):
    lines = [
        "# %s — 퀴즈 답안지" % set_title(s),
        "# 문제지: problems/%s/quiz.md  (코드를 실행하지 말고 눈으로 풀어 보세요)" % s["id"],
        "#",
        "# 답 적는 법",
        "#   객관식    : 보기 번호를 정수로.   예) Q1 = 3      정답이 여러 개면 Q1 = [1, 3]",
        '#   출력 예측 : 출력 내용을 문자열로. 예) Q2 = "7"    여러 줄이면 """ 로 감싸기',
        '#   단답      : 문자열로.             예) Q3 = "bool"',
        "#   아직 안 푼 문제는 None 그대로 둡니다.",
        "",
    ]
    for q in s["questions"]:
        lines.append("%s = None  # %s · %d점" % (q["id"], QTYPE_LABEL[q["type"]], q["points"]))
    return "\n".join(lines) + "\n"


def cmd_start(args):
    user = current_user(args)
    s = load_set(resolve_set(args.set))
    dest = os.path.join(SUBMISSIONS_DIR, user, s["id"])
    os.makedirs(dest, exist_ok=True)
    created = []
    if s["questions"] and not os.path.exists(os.path.join(dest, "quiz.py")):
        write_text(os.path.join(dest, "quiz.py"), quiz_stub(s))
        created.append("quiz.py")
    for p in s["problems"]:
        target = os.path.join(dest, p["id"] + ".py")
        if not os.path.exists(target):
            shutil.copyfile(os.path.join(p["dir"], "starter.py"), target)
            created.append(p["id"] + ".py")
    limit = s["meta"].get("time_limit_min")
    if limit and not os.path.exists(os.path.join(dest, ".started")):
        write_text(os.path.join(dest, ".started"), datetime.datetime.now().isoformat(timespec="seconds") + "\n")
    rel = "submissions/%s/%s" % (user, s["id"])
    print("[%s] %s" % (s["id"], set_title(s)))
    print("  새로 받은 파일 %d개 → %s/" % (len(created), rel))
    print("  ① 개념 정리 : problems/%s/README.md" % s["id"])
    if s["questions"]:
        print("  ② 퀴즈      : problems/%s/quiz.md 를 읽고 %s/quiz.py 에 답 적기" % (s["id"], rel))
    for p in s["problems"]:
        print("  · %s  %s · %s (%d점) — problems/%s/%s/problem.md" % (
            p["id"], TYPE_LABEL[p["type"]], p["title"], p["points"], s["id"], p["id"]))
    if limit:
        print("  ⏱ 제한 시간 %d분 — 지금부터 재기 시작합니다." % limit)
    print("  채점: python study.py grade %s" % s["id"])


def cmd_grade(args):
    if args.dir:
        if not args.set:
            die("--dir 은 세트를 지정해야 합니다. 예) python study.py grade 3 --dir 폴더")
        s = load_set(resolve_set(args.set))
        print_report(s, grade_set(s, args.dir), args.dir)
        return
    user = current_user(args)
    import adaptive
    if args.set and adaptive.ROUND_RE.fullmatch(args.set):
        grade_round_cmd(user, args.set)
        return
    if not args.set and adaptive.load_profile(user)["rounds"]:
        cmd_go(args)
        return
    set_ids = [resolve_set(args.set)] if args.set else started_sets(user)
    if not set_ids:
        die("아직 시작한 세트가 없습니다. `python study.py` 로 진단 테스트부터 시작하세요.")
    graded = grade_user(user, set_ids)
    if args.md:
        print(render_markdown(user, graded))
        return
    for s, items in graded:
        print_report(s, items, os.path.join(SUBMISSIONS_DIR, user, s["id"]))


def cmd_status(args):
    user = current_user(args)
    graded = dict((s["id"], (s, items)) for s, items in grade_user(user))
    print("%s 님의 진행 현황 (통과 기준 %d%%)" % (user, int(PASS_RATIO * 100)))
    all_earned = all_total = 0
    for sid in all_set_ids():
        if sid not in graded:
            print("  ·  %-4s %s — 시작 전" % (sid, set_title(load_set(sid))))
            continue
        s, items = graded[sid]
        earned, total, ratio = totals(items)
        all_earned += earned
        all_total += total
        print("  %s %-4s %s — %d/%d점 (%d%%)" % (
            "✅" if ratio >= PASS_RATIO else "·", sid, set_title(s), earned, total, round(ratio * 100)))
    if all_total:
        print("  ── 시작한 세트 합계 %d/%d점 (%d%%)" % (all_earned, all_total, round(all_earned / all_total * 100)))


def board_rows():
    """[(사용자, {세트ID: 득점률}, 총득점, 총점)] — 점수 높은 순."""
    rows = []
    for user in all_users():
        ratios, earned_sum, total_sum = {}, 0, 0
        for s, items in grade_user(user):
            earned, total, ratio = totals(items)
            ratios[s["id"]] = ratio
            earned_sum += earned
            total_sum += total
        rows.append((user, ratios, earned_sum, total_sum))
    return sorted(rows, key=lambda r: -r[2])


def render_board():
    set_ids = all_set_ids()
    rows = board_rows()
    if not rows:
        return "아직 제출한 사람이 없습니다.\n"
    lines = ["| 이름 | 총점 | " + " | ".join(set_ids) + " |", "|---|---|" + "---|" * len(set_ids)]
    for user, ratios, earned, total in rows:
        cells = []
        for sid in set_ids:
            if sid not in ratios:
                cells.append("·")
            else:
                cells.append("%d%%%s" % (round(ratios[sid] * 100), " ✅" if ratios[sid] >= PASS_RATIO else ""))
        lines.append("| %s | %d/%d | %s |" % (user, earned, total, " | ".join(cells)))
    return "\n".join(lines) + "\n"


def cmd_board(args):
    print("스터디 현황판 (세트별 득점률, ✅ = 통과)\n")
    print(render_board())


def cmd_explain(args):
    set_token, item = args.set, args.item
    if item is None and "_" in set_token:  # 라운드 문항 ID: s03_Q4
        set_token, item = set_token.split("_", 1)
    if item is None:
        die("문항을 지정하세요. 예) python study.py explain 3 Q4  또는  python study.py explain s03_Q4")
    s = load_set(resolve_set(set_token))
    for q in s["questions"]:
        if q["id"].lower() == item.lower():
            if q["type"] == "choice":
                answer = ", ".join("%d번" % n for n in q["answer"])
            elif q["type"] == "output":
                answer = "\n" + indent(q["answer"].rstrip("\n"))
            else:
                answer = " 또는 ".join(q["answer"])
            print("[%s %s] %s · %d점\n정답: %s\n\n%s" % (s["id"], q["id"], QTYPE_LABEL[q["type"]], q["points"], answer, q["explain"]))
            return
    for p in s["problems"]:
        if p["id"].lower() == item.lower():
            print("[%s %s] %s · %s\n" % (s["id"], p["id"], TYPE_LABEL[p["type"]], p["title"]))
            print(s["secrets"].get(p["id"] + "/explain.md", "(해설 없음)").rstrip())
            print("\n── 모범 답안 ──\n" + s["secrets"].get(p["id"] + "/solution.py", "(없음)").rstrip())
            return
    die("%s 세트에 '%s' 문항이 없습니다. (예: Q3, p01)" % (s["id"], item))


def cmd_reset(args):
    user = current_user(args)
    s = load_set(resolve_set(args.set))
    for p in s["problems"]:
        if p["id"].lower() == args.item.lower():
            target = os.path.join(SUBMISSIONS_DIR, user, s["id"], p["id"] + ".py")
            shutil.copyfile(os.path.join(p["dir"], "starter.py"), target)
            print("시작 코드로 되돌렸습니다: submissions/%s/%s/%s.py" % (user, s["id"], p["id"]))
            return
    die("%s 세트에 '%s' 문제가 없습니다. (예: p01)" % (s["id"], args.item))


# ───────────────────────── 적응형 학습 명령 ─────────────────────────

def round_as_set(rnd):
    """라운드를 print_report 가 받는 세트 모양으로 감싼다."""
    import adaptive
    return {"id": rnd["id"], "meta": {"title": adaptive.round_title(rnd)}}


def announce_round(user, rnd, folder):
    import adaptive
    title = round_as_set(rnd)["meta"]["title"]
    print("%s 준비 — %d문항" % (title, len(rnd["items"])))
    print("  문제지 : %s/README.md" % os.path.relpath(folder, ROOT))
    print("  답안   : 같은 폴더의 quiz.py 와 .py 파일")
    if rnd["kind"] == "diag":
        print("  약 30분. 코드는 실행하지 말고 눈으로 풀어 주세요. 출발점을 정하는 용도라 점수는 중요하지 않습니다.")
    else:
        print("  전 단원이 섞여 있고 약한 단원이 더 많이 나옵니다. 평균 레벨 %.1f." % rnd.get("avg_level", 0))
        print("  문항 수 기준: %s" % rnd.get("size_reason", "필요에 따라"))
    print("  다 풀면 : python study.py")


def print_round_result(sess, result):
    """채점 결과와 가이드를 출력한다(회차 채점 공통)."""
    import adaptive
    rnd = adaptive.find_round(sess.prof, result["round"]["id"])
    print_report(round_as_set(rnd), result["items"], sess.folder(rnd["id"]))
    if result["unanswered"]:
        print("\n아직 답하지 않은 문항 %d개가 있습니다. 마저 풀고 다시 python study.py 를 실행하세요." % result["unanswered"])
        return
    print(adaptive.guide_text(sess.prof, sess.cat, rnd))
    if result["next_round"]:
        nxt = adaptive.find_round(sess.prof, result["next_round"])
        print()
        announce_round(sess.user, nxt, sess.folder(nxt["id"]))


def grade_round_cmd(user, rid):
    import session
    sess = session.Session(user)
    try:
        result = sess.grade(rid)
    except session.SessionError as error:
        die(str(error))
    print_round_result(sess, result)


def cmd_go(args):
    """명령 하나로 다음 할 일을 이어 간다: 진단 → 풀기 → 채점·판정 → 다음 회차 → … → 모의고사."""
    import adaptive
    import session
    user = current_user(args)
    sess = session.Session(user)
    rnd, created = sess.ensure_round()
    if rnd is None:
        print("전 단원을 심화까지 마쳤습니다. 실전 모의고사: python study.py start m1")
        return
    if created:
        announce_round(user, rnd, sess.folder(rnd["id"]))
        return
    result = sess.grade(rnd["id"])
    if result["untouched"]:
        print("%s 를 아직 풀지 않았습니다." % adaptive.round_title(rnd))
        announce_round(user, rnd, sess.folder(rnd["id"]))
        return
    print_round_result(sess, result)


def cmd_diagnose(args):
    import adaptive
    user = current_user(args)
    cat = adaptive.catalog()
    prof = adaptive.load_profile(user)
    rnd = adaptive.build_diagnostic(prof, cat)
    prof["rounds"].append(rnd)
    adaptive.save_profile(prof)
    announce_round(user, rnd, adaptive.write_round(user, rnd, cat))


def cmd_next(args):
    import adaptive
    user = current_user(args)
    cat = adaptive.catalog()
    prof = adaptive.load_profile(user)
    rnd = adaptive.build_round(prof, cat)
    if not rnd:
        print("전 단원을 심화까지 마쳤습니다. 실전 모의고사: python study.py start m1")
        return
    prof["rounds"].append(rnd)
    adaptive.save_profile(prof)
    announce_round(user, rnd, adaptive.write_round(user, rnd, cat))


def cmd_me(args):
    import adaptive
    user = current_user(args)
    cat = adaptive.catalog()
    prof = adaptive.load_profile(user)
    print("%s 님의 학습 현황 — 라운드 %d회, 시도 %d문항" % (user, len(prof["rounds"]), len(adaptive.first_attempts(prof))))
    print(adaptive.guide_text(prof, cat, show_next=True))


def cmd_analyze(args):
    import adaptive
    md, shortages = adaptive.team_analysis_markdown(adaptive.catalog())
    print(md)
    if shortages:
        print(adaptive.shortage_request_markdown(shortages, adaptive.catalog()))


def build_parser():
    parser = argparse.ArgumentParser(description="ROKEY 파이썬 스터디 — 그냥 `python study.py` 만 치면 다음 할 일을 이어 갑니다")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("go", help="(기본) 다음 할 일 이어 가기: 진단 → 풀기 → 채점 → 다음 라운드")
    p.add_argument("--user")
    p.set_defaults(func=cmd_go)

    p = sub.add_parser("diagnose", help="진단 테스트 새로 받기")
    p.add_argument("--user")
    p.set_defaults(func=cmd_diagnose)

    p = sub.add_parser("next", help="다음 맞춤 라운드 받기")
    p.add_argument("--user")
    p.set_defaults(func=cmd_next)

    p = sub.add_parser("me", help="내 단원별 숙달도·약점·다음 추천")
    p.add_argument("--user")
    p.set_defaults(func=cmd_me)

    p = sub.add_parser("analyze", help="스터디원 전체 학습 분석 (스터디장용)")
    p.set_defaults(func=cmd_analyze)

    p = sub.add_parser("init", help="내 풀이 폴더 만들기 (처음 한 번)")
    p.add_argument("id", help="내 깃허브 ID (영문·숫자·-·_)")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("list", help="세트(차시·모의고사) 목록")
    p.add_argument("--user")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("start", help="세트 문제 받기")
    p.add_argument("set", help="차시 번호 또는 세트 ID (예: 3, s03, m1)")
    p.add_argument("--user")
    p.set_defaults(func=cmd_start)

    p = sub.add_parser("grade", help="채점 (세트를 생략하면 시작한 세트 전부)")
    p.add_argument("set", nargs="?")
    p.add_argument("--user")
    p.add_argument("--dir", help="임의 폴더의 풀이를 채점(출제자용)")
    p.add_argument("--md", action="store_true", help="마크다운 표로 출력")
    p.set_defaults(func=cmd_grade)

    p = sub.add_parser("status", help="내 진행 현황")
    p.add_argument("--user")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("board", help="전체 스터디원 현황판")
    p.set_defaults(func=cmd_board)

    p = sub.add_parser("explain", help="해설·정답 보기 (먼저 스스로 다시 풀어 본 뒤에!)")
    p.add_argument("set", help="세트 또는 라운드 문항 ID (예: 3, s03_Q4)")
    p.add_argument("item", nargs="?", help="문항 ID (예: Q3, p01)")
    p.set_defaults(func=cmd_explain)

    p = sub.add_parser("reset", help="코드 문제를 시작 코드로 되돌리기")
    p.add_argument("set")
    p.add_argument("item", help="문제 ID (예: p01)")
    p.add_argument("--user")
    p.set_defaults(func=cmd_reset)
    return parser


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) == 2 and argv[0] == "_run":  # 채점 러너(내부용)
        _child_main(argv[1])
        return
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        cmd_go(args)
        return
    args.func(args)


if __name__ == "__main__":
    main()
