#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GitHub Actions 용 채점 리포트.

- PR: 이 PR 에서 풀이가 바뀐 사람만 채점해 report.md 로 남긴다.
      풀이 PR 은 자기 폴더(submissions/<ID>/)만 건드려야 한다(규칙 위반 시 실패).
- main 푸시: 전체 현황판을 남긴다.
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import study  # noqa: E402


def changed_files(base_ref):
    out = subprocess.run(
        ["git", "-c", "core.quotepath=false", "diff", "--name-only", "origin/%s...HEAD" % base_ref],
        cwd=study.ROOT, check=True, stdout=subprocess.PIPE,
    ).stdout.decode("utf-8")
    return [line for line in out.splitlines() if line.strip()]


def main():
    base_ref = os.environ.get("GITHUB_BASE_REF")  # PR 일 때만 값이 있다
    problems = []
    if base_ref:
        files = changed_files(base_ref)
        users = sorted({f.split("/")[1] for f in files if f.startswith("submissions/") and f.count("/") >= 2})
        others = [f for f in files if not f.startswith("submissions/")]
        if len(users) > 1:
            problems.append("한 PR 에는 한 사람의 풀이만 담아 주세요: " + ", ".join(users))
        if users and others:
            problems.append("풀이 PR 에서는 `submissions/<내 ID>/` 밖의 파일을 바꿀 수 없습니다: " + ", ".join(others[:5]))
        parts = []
        if not users:
            parts.append("이 PR 에는 풀이(submissions/) 변경이 없습니다.\n")
        for user in users:
            if os.path.isdir(os.path.join(study.SUBMISSIONS_DIR, user)):
                parts.append(study.render_markdown(user, study.grade_user(user)))
        report = "\n".join(parts)
    else:
        report = "### 스터디 현황판\n\n" + study.render_board()

    if problems:
        report = "### PR 규칙 확인\n\n" + "\n".join("- " + p for p in problems) + "\n\n" + report
    study.write_text(os.path.join(study.ROOT, "report.md"), report)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(report + "\n")
    print(report)
    if problems:
        sys.exit(1)


if __name__ == "__main__":
    main()
