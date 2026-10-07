#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""문제 은행 무결성 검사 (출제자·CI용).

  python tools/verify_bank.py [세트...]

세트마다 확인하는 것:
  - meta.json / README.md / quiz.md / problem.json 형식
  - 퀴즈: 문제지(quiz.md)와 정답표의 문항 ID 일치, '출력 예측' 정답을 실제 실행 결과와 대조
  - 코드 문제: 모범 답안이 모든 테스트를 통과하고, 시작 코드는 통과하지 못하는지
  - 빈칸 채우기: 모범 답안이 빈칸만 채운 형태인지
"""
import ast
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import session  # noqa: E402
import study  # noqa: E402

KINDS = ("session", "codetest", "mock")
MODES = ("call", "io", "exec")
MIN_CASES = {"call": 3, "io": 1, "exec": 1}  # 모드별 최소 테스트 수


def run_source(text, spec):
    """소스 문자열을 임시 파일로 만들어 테스트를 돌린다."""
    with tempfile.TemporaryDirectory(prefix="verify_") as tmp:
        path = os.path.join(tmp, "submission.py")
        study.write_text(path, text)
        return study.run_problem(spec, path)


def check_quiz(s, errors):
    set_dir = s["dir"]
    quiz_md = os.path.join(set_dir, "quiz.md")
    has_key = study.SECRET_QUIZ in s["secrets"]
    if not os.path.isfile(quiz_md):
        if has_key:
            errors.append("quiz_key.json 은 있는데 quiz.md 가 없습니다.")
        return
    if not has_key:
        errors.append("quiz.md 는 있는데 정답표(quiz_key.json)가 없습니다.")
        return
    quiz_text = study.read_text(quiz_md)
    headings = re.findall(r"^## (Q\d+)\b", quiz_text, flags=re.M)
    sections = {}  # 문항별 본문(코드 블록 대조용)
    for m in re.finditer(r"^## (Q\d+)\b(.*?)(?=^## Q\d+\b|\Z)", quiz_text, flags=re.M | re.S):
        sections[m.group(1)] = m.group(2)
    ids = [q.get("id") for q in s["questions"]]
    if headings != ids:
        errors.append("quiz.md 의 문항(## Q1 …)과 정답표의 문항 순서·ID 가 다릅니다: %s vs %s" % (headings, ids))
    if ids != ["Q%d" % (i + 1) for i in range(len(ids))]:
        errors.append("퀴즈 문항 ID 는 Q1 부터 순서대로여야 합니다: %s" % ids)
    for q in s["questions"]:
        where = "퀴즈 %s: " % q.get("id")
        if q.get("type") not in study.QTYPE_LABEL:
            errors.append(where + "type 은 choice/output/short 중 하나여야 합니다.")
            continue
        if not (isinstance(q.get("points"), int) and q["points"] > 0):
            errors.append(where + "points 는 양의 정수여야 합니다.")
        if not str(q.get("explain", "")).strip():
            errors.append(where + "explain(해설)이 비어 있습니다.")
        if q.get("level") not in (1, 2, 3):
            errors.append(where + "level(1·2·3)이 필요합니다.")
        if not (isinstance(q.get("tags"), list) and q["tags"] and all(isinstance(t, str) and t.strip() for t in q["tags"])):
            errors.append(where + "tags(개념 1~3개)가 필요합니다.")
        answer = q.get("answer")
        if q["type"] == "choice":
            if not (isinstance(answer, list) and answer and all(isinstance(n, int) and 1 <= n <= 9 for n in answer)):
                errors.append(where + "객관식 answer 는 보기 번호의 리스트여야 합니다. 예) [3]")
            else:
                body = sections.get(q["id"], "")
                count = session.choice_count(body)
                if count < max(max(answer), 2):
                    errors.append(where + "보기를 %d개로 읽었는데 정답은 %s 입니다. 보기는 본문 마지막의 번호 목록(1. 2. …)이나 `**1번**` 문단으로 적어 주세요." % (count, answer))
                if len(answer) > 1 and not re.search(r"모두\**\s*고르", body):
                    errors.append(where + "복수 정답 문항은 본문에 '모두 고르세요'가 있어야 합니다.")
        elif q["type"] == "short":
            if not (isinstance(answer, list) and answer and all(isinstance(a, str) and a.strip() for a in answer)):
                errors.append(where + "단답 answer 는 허용 답안 문자열의 리스트여야 합니다. 예) [\"bool\"]")
        else:
            if not (isinstance(answer, str) and answer.strip()):
                errors.append(where + "출력 예측 answer 는 비어 있지 않은 문자열이어야 합니다.")
                continue
            if not isinstance(q.get("code"), str):
                errors.append(where + "출력 예측 문항에는 실제로 실행해 볼 code 가 필요합니다.")
                continue
            blocks = re.findall(r"```[^\n]*\n(.*?)```", sections.get(q["id"], ""), flags=re.S)
            if study.norm_out(q["code"]) not in [study.norm_out(b) for b in blocks]:
                errors.append(where + "quiz.md 에 보이는 코드와 정답표의 code 가 다릅니다(글자 그대로 같아야 합니다).")
            spec = {"mode": "io", "cases": [{"stdin": q.get("stdin", ""), "stdout": answer}]}
            ok, _, detail = run_source(q["code"], spec)
            if not ok:
                errors.append(where + "code 의 실제 출력이 answer 와 다릅니다.\n" + study.indent(detail, "      "))


def check_problem(s, p, errors):
    where = "%s: " % p["id"]
    for name in ("problem.md", "starter.py"):
        path = os.path.join(p["dir"], name)
        if not (os.path.isfile(path) and study.read_text(path).strip()):
            errors.append(where + "%s 가 없거나 비어 있습니다." % name)
            return
    solution = s["secrets"].get(p["id"] + "/solution.py", "")
    if not solution.strip():
        errors.append(where + "모범 답안(solution.py)이 없습니다.")
        return
    if not s["secrets"].get(p["id"] + "/explain.md", "").strip():
        errors.append(where + "해설(explain.md)이 없습니다.")
    if not str(p.get("title", "")).strip():
        errors.append(where + "title 이 없습니다.")
    if p.get("type") not in study.TYPE_LABEL:
        errors.append(where + "type 은 fill/return/print 중 하나여야 합니다.")
        return
    if p.get("mode") not in MODES:
        errors.append(where + "mode 는 call/io/exec 중 하나여야 합니다.")
        return
    if p.get("level") not in (1, 2, 3):
        errors.append(where + "level 은 1·2·3 중 하나여야 합니다.")
    if not (isinstance(p.get("tags"), list) and p["tags"] and all(isinstance(t, str) and t.strip() for t in p["tags"])):
        errors.append(where + "tags(개념 1~3개)가 필요합니다.")
    if not (isinstance(p.get("points"), int) and p["points"] > 0):
        errors.append(where + "points 는 양의 정수여야 합니다.")
    cases = p.get("cases")
    if isinstance(cases, list) and not (isinstance(p.get("examples"), int) and 1 <= p["examples"] <= len(cases)):
        errors.append(where + "examples 가 필요합니다: 문제 본문에 예시로 보이는 앞쪽 테스트 수(1 이상, 테스트 수 이하). 화면의 '코드 실행'이 이만큼만 돌립니다.")
    if not (isinstance(cases, list) and len(cases) >= MIN_CASES[p["mode"]]):
        errors.append(where + "테스트(cases)는 %d개 이상이어야 합니다." % MIN_CASES[p["mode"]])
        return
    for index, case in enumerate(cases, 1):
        if p["mode"] == "call":
            if not isinstance(case.get("call"), str) or not isinstance(case.get("expected"), str):
                errors.append(where + "cases[%d]: call 모드는 call·expected(문자열)가 필요합니다." % index)
                return
            try:
                ast.literal_eval(case["expected"])
            except (ValueError, SyntaxError):
                errors.append(where + "cases[%d]: expected 는 파이썬 리터럴이어야 합니다: %r" % (index, case["expected"]))
                return
        elif p["mode"] == "io":
            if not isinstance(case.get("stdout"), str):
                errors.append(where + "cases[%d]: io 모드는 stdout 이 필요합니다." % index)
                return
        else:
            if not isinstance(case.get("code"), str):
                errors.append(where + "cases[%d]: exec 모드는 code 가 필요합니다." % index)
                return

    starter = study.read_text(os.path.join(p["dir"], "starter.py"))
    has_blank = bool(study.BLANK_RE.search(starter))
    if p["type"] == "fill":
        if not has_blank:
            errors.append(where + "빈칸 채우기인데 starter.py 에 빈칸(____)이 없습니다.")
            return
        problem = study.check_fill(starter, solution)
        if problem:
            errors.append(where + "모범 답안이 빈칸만 채운 형태가 아닙니다. " + problem)
            return
    else:
        if has_blank:
            errors.append(where + "빈칸 채우기가 아닌데 starter.py 에 ____ 가 있습니다.")
        try:
            compile(starter, "starter.py", "exec")
        except SyntaxError as error:
            errors.append(where + "starter.py 문법 오류: %s번째 줄 %s" % (error.lineno, error.msg))

    ok, passed, detail = run_source(solution, p)
    if not ok:
        errors.append(where + "모범 답안이 테스트를 통과하지 못합니다 (%d/%d).\n%s" % (
            passed, len(cases), study.indent(detail, "      ")))
    ok, _, _ = run_source(starter, p)
    if ok:
        errors.append(where + "시작 코드(starter.py)가 그대로 테스트를 통과합니다. 테스트를 보강하세요.")


def check_set(sid):
    errors = []
    set_dir = os.path.join(study.PROBLEMS_DIR, sid)
    try:
        s = study.load_set(sid)
    except Exception as error:  # 형식이 깨진 파일도 오류 목록으로 보고한다
        return ["세트를 읽지 못했습니다: %s: %s" % (type(error).__name__, error)], None
    meta = s["meta"]
    if meta.get("id") != sid:
        errors.append("meta.json 의 id(%r)가 폴더 이름과 다릅니다." % meta.get("id"))
    if not str(meta.get("title", "")).strip():
        errors.append("meta.json 에 title 이 없습니다.")
    if meta.get("kind") not in KINDS:
        errors.append("meta.json 의 kind 는 session/codetest/mock 중 하나여야 합니다.")
    if not os.path.isfile(os.path.join(set_dir, "README.md")):
        errors.append("README.md(개념 정리)가 없습니다.")
    pids = [p["id"] for p in s["problems"]]
    if pids != ["p%02d" % (i + 1) for i in range(len(pids))]:
        errors.append("문제 폴더는 p01 부터 순서대로여야 합니다: %s" % pids)
    check_quiz(s, errors)
    for p in s["problems"]:
        check_problem(s, p, errors)
    if not s["questions"] and not s["problems"]:
        errors.append("퀴즈도 코드 문제도 없습니다.")
    return errors, s


def main():
    tokens = sys.argv[1:]
    set_ids = [study.resolve_set(t) for t in tokens] if tokens else study.all_set_ids()
    failed = False
    for sid in set_ids:
        errors, s = check_set(sid)
        if errors:
            failed = True
            print("✘ %s — 문제 %d건" % (sid, len(errors)))
            for message in errors:
                print("    - " + message)
        else:
            points = sum(q["points"] for q in s["questions"]) + sum(p["points"] for p in s["problems"])
            kinds = {}
            for p in s["problems"]:
                kinds[p["type"]] = kinds.get(p["type"], 0) + 1
            detail = ", ".join("%s %d" % (study.TYPE_LABEL[k], v) for k, v in sorted(kinds.items()))
            print("✔ %s %s — 퀴즈 %d문항, 코드 %d문제(%s), 총 %d점" % (
                sid, study.set_title(s), len(s["questions"]), len(s["problems"]), detail or "-", points))
    if failed:
        sys.exit(1)
    print("OK — %d개 세트 검사 통과" % len(set_ids))


if __name__ == "__main__":
    main()
