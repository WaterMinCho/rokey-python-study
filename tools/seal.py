#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""정답·해설을 sealed.json 으로 묶고 푸는 출제자용 도구. 명령은 USAGE 에 있음."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import study  # noqa: E402

NOTE = "정답·해설 묶음입니다(스포일러 방지용). 해설은 `python study.py explain <세트> <문항>` 으로 보세요."
USAGE = """정답·해설 봉인 도구 (출제자용)

정답(quiz_key.json)·모범 답안(solution.py)·해설(explain.md)은 평문으로 커밋하지 않고 세트마다 sealed.json 하나로 묶어 커밋합니다.
암호화는 아니고, 실수로 답을 미리 보지 않게 가려 두는 용도입니다.

  python tools/seal.py seal [세트...]     평문 → sealed.json (평문 삭제, --keep 이면 평문 유지)
  python tools/seal.py unseal [세트...]   sealed.json → 평문 (수정할 때)
  python tools/seal.py check              봉인 안 된 평문이 남아 있으면 실패
"""


def target_sets(tokens):
    return [study.resolve_set(t) for t in tokens] if tokens else study.all_set_ids()


def seal(sid, keep=False):
    set_dir = os.path.join(study.PROBLEMS_DIR, sid)
    files = study.load_secrets(set_dir)
    pids = set(study.problem_ids(set_dir))
    has_quiz = os.path.isfile(os.path.join(set_dir, "quiz.md"))
    # 사라진 문제·퀴즈의 묵은 항목은 버림
    files = {rel: text for rel, text in files.items()
             if (rel == study.SECRET_QUIZ and has_quiz) or rel.split("/")[0] in pids}
    study.write_text(os.path.join(set_dir, "sealed.json"),
                     json.dumps({"note": NOTE, "blob": study.seal_blob(files)}, ensure_ascii=False, indent=1) + "\n")
    if not keep:
        for rel in study.plain_secret_paths(set_dir):
            os.remove(os.path.join(set_dir, *rel.split("/")))
    print("봉인: %s (%d개 파일%s)" % (sid, len(files), ", 평문 유지" if keep else ""))


def unseal(sid):
    set_dir = os.path.join(study.PROBLEMS_DIR, sid)
    files = study.load_secrets(set_dir)
    for rel, text in files.items():
        folder = os.path.join(set_dir, *rel.split("/")[:-1])
        if os.path.isdir(folder):
            study.write_text(os.path.join(set_dir, *rel.split("/")), text)
    print("봉인 해제: %s (%d개 파일). 수정한 뒤 verify_bank → seal 순서로 마무리하세요." % (sid, len(files)))


def check():
    dirty = []
    for sid in study.all_set_ids():
        set_dir = os.path.join(study.PROBLEMS_DIR, sid)
        dirty += ["%s/%s" % (sid, rel) for rel in study.plain_secret_paths(set_dir)]
    if dirty:
        print("봉인되지 않은 평문 파일이 있습니다. `python tools/seal.py seal` 을 실행하세요:")
        for path in dirty:
            print("  problems/" + path)
        sys.exit(1)
    print("OK: 모든 정답·해설이 봉인되어 있습니다.")


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("seal", "unseal", "check"):
        print(USAGE)
        sys.exit(2)
    command, tokens = sys.argv[1], sys.argv[2:]
    keep = "--keep" in tokens
    tokens = [t for t in tokens if t != "--keep"]
    if command == "check":
        check()
        return
    for sid in target_sets(tokens):
        if command == "seal":
            seal(sid, keep)
        else:
            unseal(sid)


if __name__ == "__main__":
    main()
