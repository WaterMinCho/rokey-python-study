# -*- coding: utf-8 -*-
"""제출(git) 테스트. 임시 폴더에 bare 원격, GitHub 역할 클론, 스터디원 클론을 만들어 시나리오를 돌림.

실제 저장소와 GitHub 에는 아무것도 보내지 않음. 클론의 origin 주소는 가짜 GitHub 주소이고, git 의 insteadOf 설정이
그것을 임시 폴더의 bare 저장소로 돌림. 풀이는 실제 session.Session 으로 임시 클론 안에 만들어서 profile.json 도 진짜와 같음.
동작마다 "로컬 풀이가 바이트 단위로 같은가", "PR 변경 범위가 submissions/<ID> 뿐인가"를 보고,
끝날 때 금지 명령(push --force, reset --hard, clean, stash)을 쓰지 않았는지 명령 기록으로 확인함.
git 이 없거나 2.38 보다 오래됐으면 검사에 쓰는 merge-tree --write-tree 가 없어서 건너뜀.

실행: python -m unittest discover -s tests
"""
import hashlib
import http.server
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import gitflow  # noqa: E402
import session  # noqa: E402
import study  # noqa: E402

OWNER, REPO = "study-owner", "study-repo"
FAKE_URL = "https://github.com/%s/%s.git" % (OWNER, REPO)
NEW_PR = "https://github.com/%s/%s/compare/main...study/alice?quick_pull=1&title=alice+%%ED%%92%%80%%EC%%9D%%B4" % (OWNER, REPO)
OPEN_PR = "https://github.com/%s/%s/pull/7" % (OWNER, REPO)
KEYS = {"status", "message", "detail", "pr_url", "restart", "changed", "backup"}
FORBIDDEN = [r"^git push\b.*(--force|\s-f\b|\s\+)", r"^git reset\b.*--hard", r"^git clean\b", r"^git stash\b",
             r"^git checkout\b.*\s(-f|--force)\b", r"^git branch\b.*\s-D\b"]
IDENTITY = "[user]\n\tname = tester\n\temail = tester@example.invalid\n"
COMMON = "[init]\n\tdefaultBranch = main\n[advice]\n\tdetachedHead = false\n[core]\n\tautocrlf = false\n"


def git_version():
    if not shutil.which("git"):
        return (0, 0)
    found = re.search(r"(\d+)\.(\d+)", subprocess.run(["git", "--version"], stdout=subprocess.PIPE, text=True).stdout)
    return (int(found.group(1)), int(found.group(2))) if found else (0, 0)


def git(cwd, *args, check=True):
    """손으로 치는 git, 검사용 조회, GitHub 역할이 쓰는 git."""
    done = subprocess.run(["git", "-c", "core.quotepath=false"] + list(args), cwd=cwd, stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace",
                          env=dict(os.environ, GIT_TERMINAL_PROMPT="0", LC_ALL="C", GIT_MERGE_AUTOEDIT="no"))
    if check and done.returncode != 0:
        raise AssertionError("git %s → %d\n%s%s" % (" ".join(args), done.returncode, done.stdout, done.stderr))
    return done


def write(path, text, mode="w"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode, encoding="utf-8", newline="\n") as f:
        f.write(text)


def blob_sha(data):
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def digest(files):
    """{경로: 내용} 을 git 의 blob 해시로 바꿈. 원격의 트리와 비교할 수 있고 실패 메시지도 짧아짐."""
    return {rel: blob_sha(data) for rel, data in files.items()}


class Server:
    """GitHub 역할: main 에 문제를 올리고 PR(study/* 브랜치)을 머지함."""

    def __init__(self, tmp, origin):
        self.origin, self.dir = origin, os.path.join(tmp, "github")
        git(tmp, "clone", "-q", origin, self.dir)

    def refresh(self):
        git(self.dir, "fetch", "-q", "--prune", "origin")

    def _main(self):
        self.refresh()
        git(self.dir, "checkout", "-q", "-B", "main", "origin/main")

    def add_problems(self, sid, tool=True):
        """새 문제 세트와 기존 문제의 오타 수정을 main 에 올림. tool 이면 도구 파일도 바꿈."""
        self._main()
        write(os.path.join(self.dir, "problems", sid, "quiz.md"), "# %s\n" % sid)
        write(os.path.join(self.dir, "problems", "s01", "quiz.md"), "오타 수정 %s\n" % sid, "a")
        if tool:
            write(os.path.join(self.dir, "study.py"), "# 도구 갱신 %s\n" % sid, "a")
        git(self.dir, "add", "-A")
        git(self.dir, "commit", "-q", "-m", "문제 세트 %s 추가" % sid)
        git(self.dir, "push", "-q", "origin", "main")

    def merge(self, branch, method="squash", delete=False):
        self._main()
        if method == "squash":
            git(self.dir, "merge", "--squash", "origin/" + branch)
            git(self.dir, "commit", "-q", "-m", "%s (squash)" % branch)
        else:
            git(self.dir, "merge", "-q", "--no-ff", "--no-edit", "origin/" + branch)
        git(self.dir, "push", "-q", "origin", "main")
        if delete:
            git(self.dir, "push", "-q", "origin", "--delete", branch)

    def other_user(self, name):
        """다른 스터디원의 PR 이 먼저 머지됨."""
        self._main()
        git(self.dir, "checkout", "-q", "-B", "study/" + name, "origin/main")
        write(os.path.join(self.dir, "submissions", name, "profile.json"), '{"user": "%s", "rounds": [], "attempts": []}\n' % name)
        git(self.dir, "add", "-A")
        git(self.dir, "commit", "-q", "-m", "%s 풀이" % name)
        git(self.dir, "push", "-q", "origin", "study/" + name)
        self.merge("study/" + name, delete=True)

    def rewrite_main(self):
        """스터디장이 main 기록을 다시 씀. 내용은 같고 이전 커밋과 이어지지 않음."""
        tree = git(self.origin, "rev-parse", "main^{tree}").stdout.strip()
        git(self.origin, "update-ref", "refs/heads/main", git(self.origin, "commit-tree", tree, "-m", "다시 쓴 기록").stdout.strip())

    def update_branch(self, branch):
        """PR 화면의 Update branch 버튼. main 을 PR 브랜치에 병합한 커밋이 원격에 생기고, 이미 최신이면 빈 커밋이 생김."""
        self.refresh()
        git(self.dir, "checkout", "-q", "-B", "_update", "origin/" + branch)
        git(self.dir, "merge", "-q", "--no-ff", "--no-edit", "origin/main")
        git(self.dir, "commit", "-q", "--allow-empty", "-m", "Update branch")
        git(self.dir, "push", "-q", "origin", "_update:refs/heads/" + branch)

    # 아래 조회는 bare 원격을 직접 봄

    def rev(self, branch):
        """원격 브랜치의 커밋. 없으면 ""."""
        return git(self.origin, "rev-parse", "-q", "--verify", "refs/heads/" + branch, check=False).stdout.strip()

    def folder(self, branch, user):
        """그 브랜치에 든 submissions/<user> 의 {경로: blob 해시}."""
        found = {}
        for record in git(self.origin, "ls-tree", "-r", "-z", branch, "--", "submissions/" + user).stdout.split("\0"):
            if record:
                meta, path = record.split("\t", 1)
                found[path] = meta.split()[2]
        return found

    def pr_files(self, branch):
        """CI 가 보는 목록: main 과 'PR 을 main 에 합친 결과'의 차이. 충돌이 나면 git 이 실패해서 테스트도 실패함."""
        tree = git(self.origin, "merge-tree", "--write-tree", "main", branch).stdout.split()[0]
        return [name for name in git(self.origin, "diff", "--name-only", "-z", "main", tree).stdout.split("\0") if name]

    def pr_commits(self, branch):
        return int(git(self.origin, "rev-list", "--count", "main.." + branch).stdout)

    def is_ancestor(self, old, new):
        return git(self.origin, "merge-base", "--is-ancestor", old, new, check=False).returncode == 0


class PC:
    """스터디원 컴퓨터 한 대: 저장소 클론과 그 폴더를 보는 GitFlow."""

    def __init__(self, tmp, origin, name, user="alice", clone_options=()):
        self.path, self.user = os.path.join(tmp, name), user
        git(tmp, "clone", "-q", *clone_options, origin, self.path)
        git(self.path, "config", "remote.origin.url", FAKE_URL)  # 주소는 GitHub, 실제 통신은 임시 폴더의 bare 저장소
        git(self.path, "config", "url.%s.insteadOf" % origin, FAKE_URL)
        self.origin = origin
        self.folder = os.path.join(self.path, "submissions", user)
        self.flow = gitflow.GitFlow(self.path, user)
        self.flow.find_pr = self.find_pr
        self.flow.pr_wait = 0  # 자동으로 만들어지는 PR 을 기다리지 않음. 기다리는 경우는 따로 테스트함
        self.open_pr, self.lookups = None, []

    def find_pr(self, owner, repo, branch):
        self.lookups.append((owner, repo, branch))
        return self.open_pr

    def session(self):
        study.SUBMISSIONS_DIR = os.path.join(self.path, "submissions")
        study.USER_FILE = os.path.join(self.path, ".study_user")
        return session.Session(self.user)

    def solve(self, correct=False, grade=True):
        """지금 회차의 퀴즈 세 문항에 답하고 회차를 제출함. 시도 기록이 늘고 다음 회차가 생김.
        grade=False 면 풀던 중에 화면이 자동 저장한 것처럼 답만 적어 둠."""
        sess = self.session()
        rnd, _ = sess.ensure_round()
        for view in [v for v in sess.open_round(rnd["id"])["items"] if v["kind"] == "quiz"][:3]:
            q = sess.cat[view["key"]]["q"]
            if not correct:
                answer = 9 if q["type"] == "choice" else "틀린 답"
            elif q["type"] == "choice":
                answer = q["answer"]
            else:
                answer = q["answer"] if q["type"] == "output" else q["answer"][0]
            sess.set_answer(rnd["id"], view["id"], answer)
        if grade:
            sess.grade(rnd["id"], finalize=True)
        return self.read()

    def read(self):
        """내 폴더의 {저장소 기준 경로: 내용}."""
        found = {}
        for base, dirs, files in os.walk(self.folder):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for name in files:
                full = os.path.join(base, name)
                with open(full, "rb") as f:
                    found[os.path.relpath(full, self.path).replace(os.sep, "/")] = f.read()
        return found

    def attempts(self):
        with open(os.path.join(self.folder, "profile.json"), encoding="utf-8") as f:
            return len(json.load(f)["attempts"])

    def state(self):
        """브랜치·커밋·작업 폴더 상태. 원격을 얼마나 따라갔는지는 뺌. 제출이 이 컴퓨터를 바꾸지 않았는지 볼 때 씀."""
        lines = git(self.path, "status", "--porcelain=v2", "--branch").stdout.splitlines()
        return [line for line in lines if not line.startswith(("# branch.upstream", "# branch.ab"))]

    def gitdir(self, *parts):
        return os.path.join(self.path, ".git", *parts)

    def offline(self, off=True):
        git(self.path, "config", "--unset-all", "url.%s.insteadOf" % (self.origin + ("" if off else ".offline")))
        git(self.path, "config", "url.%s.insteadOf" % (self.origin + (".offline" if off else "")), FAKE_URL)

    def backup_text(self, result):
        """이번 결과의 보관함에 든 파일 내용 전부."""
        texts = []
        for base, _, files in os.walk(result["backup"]):
            for name in files:
                with open(os.path.join(base, name), encoding="utf-8", errors="replace") as f:
                    texts.append(f.read())
        return "\n".join(texts)


@unittest.skipUnless(git_version() >= (2, 38), "git 2.38 이상이 필요합니다")
class GitFlowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = tempfile.mkdtemp(prefix="study_git_")
        cls.env = {name: os.environ.get(name) for name in ("GIT_CONFIG_GLOBAL", "GIT_CONFIG_NOSYSTEM", "STUDY_USER")}
        cls.config = os.path.join(cls.base, "gitconfig")
        cls.config_no_identity = os.path.join(cls.base, "gitconfig_no_identity")
        write(cls.config, IDENTITY + COMMON)
        write(cls.config_no_identity, "[user]\n\tuseConfigOnly = true\n" + COMMON)
        os.environ.update(GIT_CONFIG_GLOBAL=cls.config, GIT_CONFIG_NOSYSTEM="1")  # 이 컴퓨터의 git 설정과 섞이지 않게
        os.environ.pop("STUDY_USER", None)
        seed = os.path.join(cls.base, "seed")
        os.makedirs(seed)
        shutil.copyfile(os.path.join(ROOT, ".gitignore"), os.path.join(seed, ".gitignore"))
        for rel, text in (("README.md", "# 스터디\n"), ("study.py", "# 도구\n"), ("gui/app.py", "# 화면\n"),
                          ("problems/s01/quiz.md", "# s01\n"), ("problems/s02/quiz.md", "# s02\n"), ("submissions/.gitkeep", "")):
            write(os.path.join(seed, rel), text)
        git(seed, "init", "-q")
        git(seed, "add", "-A")
        git(seed, "commit", "-q", "-m", "문제 은행")
        cls.seed = seed

    @classmethod
    def tearDownClass(cls):
        for name, value in cls.env.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
        shutil.rmtree(cls.base, ignore_errors=True)

    def setUp(self):
        self._study = (study.SUBMISSIONS_DIR, study.USER_FILE)
        self.tmp = tempfile.mkdtemp(prefix="run_", dir=self.base)
        self.origin = os.path.join(self.tmp, "origin.git")
        git(self.tmp, "clone", "-q", "--bare", self.seed, self.origin)
        git(self.origin, "config", "receive.denyNonFastForwards", "true")  # 강제 푸시는 서버가 거부함
        self.server = Server(self.tmp, self.origin)
        self.pcs = []
        self.pc = self.new_pc("pc1")

    def tearDown(self):
        study.SUBMISSIONS_DIR, study.USER_FILE = self._study
        os.environ["GIT_CONFIG_GLOBAL"] = self.config
        used = [line for pc in self.pcs for line in pc.flow.log]
        shutil.rmtree(self.tmp, ignore_errors=True)
        self.assertEqual([line for line in used if any(re.search(p, line) for p in FORBIDDEN)], [])

    def new_pc(self, name, *clone_options):
        pc = PC(self.tmp, self.origin, name, clone_options=clone_options)
        self.pcs.append(pc)
        return pc

    # 동작 + 검사

    def call(self, pc, what, expect, after=None, *args):
        """GitFlow 를 부르고 상태를 확인함. 내 폴더는 after(없으면 부르기 전 내용)와 바이트 단위로 같아야 함."""
        before = pc.read()
        result = getattr(pc.flow, what)(*args)
        self.assertEqual(set(result), KEYS)
        self.assertEqual(result["status"], expect, result)
        self.assertNotRegex(result["message"], "[!\U0001F300-\U0001FAFF]")
        self.assertEqual(digest(pc.read()), digest(before if after is None else after), "내 폴더가 기대와 다릅니다")
        for name in ("MERGE_HEAD", "rebase-merge", "rebase-apply", "CHERRY_PICK_HEAD", "study-index"):
            self.assertFalse(os.path.exists(pc.gitdir(name)), name)
        return result

    def sync(self, pc=None, expect="ok", after=None):
        pc = pc or self.pc
        result = self.call(pc, "sync", expect, after)
        if expect == "ok":  # 내 폴더 밖 = 원격의 최신 main, 브랜치 = study/<ID>. 받지 못했으면 git 이 그 커밋을 몰라 diff 가 실패함
            outside = git(pc.path, "diff", "--name-only", self.server.rev("main"), "--", ".", ":(exclude)submissions/" + pc.user)
            self.assertEqual(outside.stdout, "")
            self.assertIn("# branch.head study/" + pc.user, pc.state())
        return result

    def submit(self, pc=None, expect="ok", after=None):
        pc = pc or self.pc
        state = pc.state()
        result = self.call(pc, "submit", expect, after)
        if expect == "ok":
            self.check_remote(pc)
            self.assertTrue(result["pr_url"])
        if after is None:
            self.assertEqual(pc.state(), state, "제출이 이 컴퓨터의 브랜치·커밋·작업 폴더를 바꿨습니다")
        return result

    def check_remote(self, pc):
        """원격 브랜치의 내 폴더 = 내 컴퓨터, PR 변경 범위 = 내 폴더뿐(충돌 없이 합쳐짐)."""
        self.assertEqual(self.server.folder("study/" + pc.user, pc.user), digest(pc.read()))
        files = self.server.pr_files("study/" + pc.user)
        self.assertTrue(files)
        self.assertEqual([f for f in files if not f.startswith("submissions/%s/" % pc.user)], [])

    def merge(self, pc=None, method="squash", delete=False):
        """PR 을 머지함. main 에 들어간 내 폴더는 마지막으로 제출한 것과 같아야 함."""
        pc = pc or self.pc
        submitted = self.server.folder("study/" + pc.user, pc.user)
        self.server.merge("study/" + pc.user, method, delete)
        self.assertEqual(self.server.folder("main", pc.user), submitted)

    def cycle(self, method, delete):
        """제출 → 머지 → 계속 풀기를 세 번 함. 두 번째 머지는 리뷰를 기다리는 동안 더 풀어 둔 상태에서 일어남."""
        pc = self.pc
        pc.solve(); self.submit()
        self.merge(method=method, delete=delete)
        pc.solve()  # 머지된 뒤 새 회차
        self.sync(); self.submit()
        pc.solve()  # 제출해 둔 채로 다음 회차까지 풂(아직 제출 안 함)
        self.merge(method=method, delete=delete)  # 그 사이 PR 이 머지됨 → main 의 내 폴더가 내 컴퓨터보다 옛것
        self.sync()
        pc.solve(grade=False); self.submit()  # 풀던 중인 답(자동 저장)까지
        pc.solve(); self.submit()
        self.merge(method=method, delete=delete)
        self.sync()  # 머지 직후 받기
        self.submit(expect="nothing")

    # 제출

    def test_first_submit(self):
        pc = self.pc
        self.assertEqual(self.sync()["message"], gitflow.M_LATEST)  # 받자마자(내 폴더도 없음)
        self.assertEqual(self.submit(expect="nothing")["message"], gitflow.M_EMPTY)
        os.makedirs(pc.folder)  # 화면이 ID 를 저장하면 빈 폴더가 생김
        self.submit(expect="nothing")
        pc.solve()
        result = self.submit()
        self.assertEqual((result["pr_url"], result["message"]), (NEW_PR, gitflow.M_OPEN_PR))
        self.assertEqual(pc.lookups, [(OWNER, REPO, "study/alice")])
        self.assertEqual(self.server.pr_commits("study/alice"), 1)
        tip = self.server.rev("study/alice")
        pc.open_pr = OPEN_PR
        result = self.submit()  # 바뀐 것 없이 한 번 더 누르면 원격 브랜치가 안 움직임
        self.assertEqual((result["pr_url"], result["message"]), (OPEN_PR, gitflow.M_SAME))
        self.assertEqual(self.server.rev("study/alice"), tip)
        self.merge()
        self.assertEqual(self.submit(expect="nothing")["message"], gitflow.M_NOTHING)  # 이미 main 에 들어간 뒤
        self.sync()

    def test_more_work_goes_to_the_open_pr(self):
        pc = self.pc
        pc.solve(); self.submit()
        first = self.server.rev("study/alice")
        pc.open_pr = OPEN_PR
        pc.solve()
        result = self.submit()
        self.assertEqual((result["pr_url"], result["message"]), (OPEN_PR, gitflow.M_ADDED))
        self.assertTrue(self.server.is_ancestor(first, "study/alice"))  # fast-forward 로 이어짐
        self.assertEqual(self.server.pr_commits("study/alice"), 2)
        pc.solve(grade=False); self.submit()
        self.sync()  # 받을 것이 없을 때도 ok 여야 함
        pc.solve(); self.submit()
        self.merge()

    def test_resubmit_after_squash_merge(self):
        self.cycle("squash", delete=False)

    def test_resubmit_after_merge_commit(self):
        self.cycle("merge", delete=False)

    def test_resubmit_after_remote_branch_deleted(self):
        self.cycle("squash", delete=True)
        self.assertEqual(self.server.rev("study/alice"), "")

    def test_nothing_to_submit_keeps_remote_untouched(self):
        self.pc.solve(); self.submit(); self.merge(delete=True)
        self.assertEqual(self.submit(expect="nothing")["pr_url"], None)
        self.assertEqual(self.server.rev("study/alice"), "")  # 올릴 것이 없으면 브랜치도 만들지 않음

    # 문제 받기

    def test_new_problems_on_main(self):
        pc = self.pc
        pc.solve()  # 아직 한 번도 제출하지 않음
        self.server.add_problems("s17")
        result = self.sync()
        self.assertEqual((result["changed"], result["restart"], result["message"]), (True, True, gitflow.M_RESTART))
        self.assertTrue(os.path.isfile(os.path.join(pc.path, "problems", "s17", "quiz.md")))
        self.submit()
        self.server.add_problems("s18", tool=False)  # PR 이 열린 채로 새 세트
        pc.solve()
        result = self.sync()
        self.assertEqual((result["changed"], result["restart"], result["message"]), (True, False, gitflow.M_NEW))
        result = self.sync()
        self.assertEqual((result["changed"], result["restart"], result["backup"]), (False, False, None))
        pc.solve(); self.submit()
        self.merge()

    def test_commit_on_main_by_mistake(self):
        pc = self.pc
        pc.solve()
        write(os.path.join(pc.path, "problems", "s01", "quiz.md"), "실수로 고친 줄\n", "a")
        git(pc.path, "add", "-A"); git(pc.path, "commit", "-q", "-m", "내 풀이")  # 문제 파일까지 main 에 커밋
        self.server.add_problems("s17")  # main 도 같은 파일을 고침
        self.submit()  # PR 에는 내 폴더만 실림
        pc.solve()
        result = self.sync()
        self.assertIn("실수로 고친 줄", pc.backup_text(result))
        self.submit()
        self.merge()

    def test_edits_outside_my_folder(self):
        pc = self.pc
        pc.solve()
        write(os.path.join(pc.path, "problems", "s01", "quiz.md"), "실수로 입력한 글자\n", "a")  # 추적 파일 수정
        write(os.path.join(pc.path, "study.py"), "# 실수로 입력\n", "a")
        write(os.path.join(pc.path, "메모.txt"), "내 메모\n")  # 겹치지 않는 내 파일
        write(os.path.join(pc.path, "problems", "s17", "quiz.md"), "내가 만든 파일\n")  # main 이 곧 만들 경로
        write(os.path.join(pc.path, "새 파일.md"), "올려 두기만 한 파일\n")
        git(pc.path, "add", "새 파일.md")
        os.remove(os.path.join(pc.path, "problems", "s02", "quiz.md"))  # 문제 파일을 지움
        self.submit()  # 제출은 밖 파일을 건드리지도 싣지도 않음
        self.server.add_problems("s17")
        result = self.sync()
        self.assertEqual((result["changed"], result["restart"]), (True, True))
        self.assertIn(gitflow.M_PARKED % 5, result["message"])
        saved = pc.backup_text(result)
        for text in ("실수로 입력한 글자", "# 실수로 입력", "내가 만든 파일", "올려 두기만 한 파일"):
            self.assertIn(text, saved)
        self.assertTrue(result["backup"].startswith(pc.gitdir("study-backup")))
        self.assertTrue(os.path.isfile(os.path.join(pc.path, "problems", "s02", "quiz.md")))
        for name, text in (("메모.txt", "내 메모\n"), ("새 파일.md", "올려 두기만 한 파일\n")):
            with open(os.path.join(pc.path, name), encoding="utf-8") as f:
                self.assertEqual(f.read(), text)
        pc.solve()
        write(os.path.join(pc.path, "problems", "s02", "quiz.md"), "또 실수\n", "a")  # 받을 것이 없을 때의 밖 수정
        self.submit()
        result = self.sync()
        self.assertEqual((result["changed"], result["restart"]), (True, False))
        self.merge()

    def test_waits_for_the_pull_request_the_repository_opens_by_itself(self):
        """올린 뒤 저장소의 Actions 가 만든 PR(refs/pull/N/head)을 기다려 그 주소를 돌려줌."""
        self.pc.solve()
        flow, waits = self.pc.flow, []

        def robot_opens_pr(seconds):  # 두 번째 확인 직전에 PR 이 생김
            waits.append(seconds)
            if len(waits) == 2:
                tip = git(self.pc.origin, "rev-parse", "refs/heads/study/alice").stdout.strip()
                git(self.pc.origin, "update-ref", "refs/pull/12/head", tip)

        flow.pr_wait, flow.sleep = gitflow.PR_WAIT, robot_opens_pr
        result = flow.submit()
        self.assertEqual((result["status"], result["message"]), ("ok", gitflow.M_CREATED))
        self.assertEqual(result["pr_url"], "https://github.com/%s/%s/pull/12" % (OWNER, REPO))
        self.assertEqual(len(waits), 2)
        # PR 이 끝내 만들어지지 않으면 기다린 뒤 '직접 만들기' 화면 주소로 대신함
        self.pc.solve()
        waits.clear()
        flow.sleep = waits.append
        result = flow.submit()
        self.assertEqual((result["status"], result["message"], result["pr_url"]), ("ok", gitflow.M_OPEN_PR, NEW_PR))
        self.assertEqual(sum(waits), gitflow.PR_WAIT)
        # 올릴 것이 없을 때는 기다리지 않음
        waits.clear()
        self.assertEqual(flow.submit()["status"], "ok")
        self.assertEqual(waits, [])

    def test_pull_request_closed_without_merging(self):
        """PR 이 머지 없이 닫힌 뒤: 올리지 않았으면 올렸다고 하지 않고, 닫힌 PR 의 주소를 새 PR 로 알리지 않음."""
        pc, flow, waits = self.pc, self.pc.flow, []
        pc.solve(); self.submit()
        self.sync()  # 프로그램을 다시 켠 상태: 로컬 브랜치가 올린 커밋에 있음
        closed = self.server.rev("study/alice")
        git(pc.origin, "update-ref", "refs/pull/5/head", closed)  # GitHub 는 닫힌 PR 의 참조를 지우지 않음
        flow.pr_wait, flow.sleep = gitflow.PR_WAIT, waits.append
        result = self.submit()  # 브랜치가 남아 있어 올릴 것이 없음
        self.assertEqual((result["message"], result["pr_url"], waits), (gitflow.M_NO_OPEN_PR, NEW_PR, []))
        git(pc.origin, "update-ref", "-d", "refs/heads/study/alice")  # 브랜치까지 지워져 같은 커밋을 다시 올림

        def robot_opens_pr(seconds):  # 두 번째 확인 직전에 새 PR 이 생김
            waits.append(seconds)
            if len(waits) == 2:
                git(pc.origin, "update-ref", "refs/pull/6/head", closed)

        flow.sleep = robot_opens_pr
        result = self.submit()
        self.assertEqual(self.server.rev("study/alice"), closed)
        self.assertEqual((result["message"], result["pr_url"]), (gitflow.M_CREATED, "https://github.com/%s/%s/pull/6" % (OWNER, REPO)))
        self.assertEqual(len(waits), 2)

    def test_open_pull_request_found_without_the_api(self):
        """익명 조회가 막혀도(한도 초과 등) 올린 뒤 끝이 옮겨진 PR 은 '열려 있던 PR'로 알림."""
        pc, flow = self.pc, self.pc.flow
        pc.solve(); self.submit()
        git(pc.origin, "update-ref", "refs/pull/7/head", self.server.rev("study/alice"))
        pc.solve()

        def github_moves_the_ref(seconds):
            git(pc.origin, "update-ref", "refs/pull/7/head", self.server.rev("study/alice"))

        flow.pr_wait, flow.sleep = gitflow.PR_WAIT, github_moves_the_ref
        result = self.submit()
        self.assertEqual((result["message"], result["pr_url"]), (gitflow.M_ADDED, OPEN_PR))

    def test_main_history_rewritten(self):
        """스터디장이 main 기록을 다시 써서 내 브랜치와 이어지지 않게 된 경우. 풀이를 둔 채 새 main 위로 옮기고 제출도 이어짐."""
        pc = self.pc
        mine = pc.solve(); self.sync()
        self.server.rewrite_main()
        self.server.add_problems("s17")
        result = self.sync(after=mine)
        self.assertEqual((result["restart"], result["backup"]), (True, None))
        self.assertEqual(git(pc.path, "merge-base", "--is-ancestor", "origin/main", "HEAD", check=False).returncode, 0)
        pc.solve(); self.submit()
        self.assertEqual(self.server.pr_commits("study/alice"), 1)
        self.merge()

    def test_main_history_rewritten_while_my_pr_is_open(self):
        """열려 있는 PR 이 옛 기록 위에 있어도 받기와 제출이 이어지고, PR 의 변경 범위는 내 폴더뿐임."""
        pc = self.pc
        pc.solve(); self.submit()
        self.server.rewrite_main()
        self.sync()
        pc.solve(); self.submit()
        self.merge()

    def test_other_people_merged_first(self):
        pc = self.pc
        self.server.other_user("bob")  # 내가 시작하기도 전에 bob 것이 머지됨
        pc.solve(); self.submit()
        self.server.other_user("carol")  # 내 PR 이 열린 동안 carol 것이 먼저 머지됨
        pc.solve(); self.submit()
        self.server.other_user("dave")
        self.sync()
        self.merge()
        for other in ("bob", "carol", "dave"):
            self.assertTrue(self.server.folder("main", other), other)

    def test_update_branch_button(self):
        pc = self.pc
        pc.solve(); self.submit()
        self.server.add_problems("s17")
        self.server.update_branch("study/alice")
        pc.solve(); self.submit()
        self.merge()

    def test_remote_moves_between_fetch_and_push(self):
        pc = self.pc
        pc.solve(); self.submit()
        self.server.add_problems("s17")
        pc.solve()
        push, calls = pc.flow._push, []

        def racing_push(commit):
            if not calls:
                self.server.update_branch("study/alice")  # 받아 온 직후 원격의 내 브랜치가 바뀜
            calls.append(commit)
            return push(commit)
        pc.flow._push = racing_push
        self.submit()
        self.assertEqual(len(calls), 2)  # 거부 → 다시 받고 한 번만 재시도

        def losing_push(commit):
            self.server.update_branch("study/alice")  # 올릴 때마다 원격이 먼저 바뀜
            calls.append(commit)
            return push(commit)
        pc.flow._push = losing_push
        pc.solve()
        self.assertEqual(self.submit(expect="error")["message"], gitflow.M_BEHIND)
        self.assertEqual(len(calls), 4)
        pc.flow._push = push
        self.submit()

    # 다른 컴퓨터

    def test_new_computer_continues_remote_work(self):
        pc = self.pc
        pc.solve(); self.submit()
        mine = pc.solve(); self.submit()  # PR 이 열린 채(아직 main 에 없음)
        pc2 = self.new_pc("pc2")
        result = self.sync(pc2, after=mine)  # 앱을 켜면 먼저 받기 → 원격의 내 풀이를 이어받음
        self.assertEqual((result["changed"], result["backup"], result["message"]), (True, None, gitflow.M_TOOK + " " + gitflow.M_LATEST))
        pc2.solve(); self.submit(pc2)
        self.merge(pc2)

    def test_new_computer_that_already_made_an_empty_profile(self):
        pc, pc2 = self.pc, self.new_pc("pc2")
        mine = pc.solve(); self.submit(); self.merge(delete=True)  # 풀이는 main 에만 있음
        pc2.solve(grade=False)  # 받기 전에 진단 회차가 먼저 만들어짐
        result = self.submit(pc2, expect="nothing", after=mine)  # 제출부터 눌러도 옛 풀이를 덮어쓰지 않음
        self.assertEqual(result["changed"], True)
        self.assertIn('"attempts": []', pc2.backup_text(result))

    def test_id_differs_only_in_case_from_merged_folder(self):
        """main 에 내 풀이가 다른 철자(Alice)로 들어가 있으면 받기도 제출도 아무것도 바꾸지 않고 멈춤."""
        pc = self.pc
        pc.solve()
        self.server.other_user("Alice")
        state = pc.state()
        for result in (self.sync(pc, expect="blocked"), self.submit(pc, expect="blocked")):
            self.assertIn("Alice", result["message"])
            self.assertIsNone(result["backup"])
        self.assertEqual(pc.state(), state)
        self.assertEqual(self.server.rev("study/alice"), "")

    def test_other_branches_differing_only_in_case(self):
        """남의 브랜치 둘이 대소문자만 달라도 내 받기와 제출은 그대로 됨(남의 브랜치는 받지 않음)."""
        pc = self.pc
        self.sync(pc)
        git(self.origin, "pack-refs", "--all")  # 원격(GitHub)은 대소문자를 구분함. 묶인 참조로 두 이름을 함께 둠
        main = self.server.rev("main")
        with open(os.path.join(self.origin, "packed-refs"), "a", encoding="utf-8") as f:
            f.write("%s refs/heads/study/Kim\n%s refs/heads/study/kim\n" % (main, main))
        for _ in range(3):
            self.sync(pc)
        pc.solve(); self.submit(pc)
        self.assertEqual(git(pc.path, "for-each-ref", "--format=%(refname)", "refs/remotes/origin/study").stdout.split(),
                         ["refs/remotes/origin/study/alice"])

    def test_single_branch_clone(self):
        pc = self.pc
        mine = pc.solve(); self.submit()
        pc2 = self.new_pc("pc2", "--single-branch")  # main 만 받아 오는 방식으로 clone 한 새 컴퓨터
        self.sync(pc2, after=mine)
        pc2.solve(); self.submit(pc2)
        self.merge(pc2, delete=True)
        pc2.solve(); self.sync(pc2); self.submit(pc2)

    def diverge(self, merged=False, theirs=1, mine=2):
        """두 컴퓨터가 같은 회차부터 따로 풂(pc2 는 theirs 회차, pc1 은 mine 회차). pc2 가 먼저 제출했고
        (merged 면 머지·브랜치 삭제까지) pc1 은 그것을 모름."""
        pc = self.pc
        pc.solve(); self.submit()
        pc2 = self.new_pc("pc2")
        self.sync(pc2, after=pc.read())
        for _ in range(theirs):
            pc2.solve(correct=True)
        self.submit(pc2)
        if merged:
            self.merge(pc2, delete=True)
        for _ in range(mine):
            pc.solve()
        ref = "main" if merged else "study/alice"
        remote = self.server.folder(ref, "alice")
        self.assertIn("이어지지 않습니다", self.submit(expect="diverged")["message"])  # 덮어쓰지 않고 멈춤
        self.sync(expect="diverged")
        self.assertEqual(self.server.folder(ref, "alice"), remote)
        return pc, pc2

    def test_diverged_take_remote(self):
        pc, pc2 = self.diverge()  # pc1 에는 원격에 없는 회차 폴더까지 있음
        mine = pc.read()
        result = self.call(pc, "resolve", "ok", pc2.read(), "remote")  # 원격에 없는 파일까지 지워 원격과 같게 만듦
        self.assertEqual((result["changed"], result["message"]), (True, gitflow.M_TOOK_OVER))
        with open(os.path.join(result["backup"], "replaced", "profile.json"), "rb") as f:
            self.assertEqual(f.read(), mine["submissions/alice/profile.json"])
        self.sync()
        self.assertEqual(self.submit()["message"], gitflow.M_NO_OPEN_PR)  # 원격과 같으므로 새로 올리지 않음
        pc.solve(); self.submit()
        self.merge()

    def test_diverged_keep_local(self):
        pc, pc2 = self.diverge()
        theirs = self.server.rev("study/alice")
        result = self.call(pc, "resolve", "ok", None, "local")
        self.assertEqual(result["pr_url"], NEW_PR)
        self.check_remote(pc)
        self.assertTrue(self.server.is_ancestor(theirs, "study/alice"))  # 강제 푸시가 아니라 이어 붙임
        self.sync()
        self.merge()

    def test_diverged_from_main_keep_local(self):
        pc, pc2 = self.diverge(merged=True, theirs=3, mine=1)  # main 에 들어간 쪽의 기록이 더 많음
        self.assertGreater(pc2.attempts(), pc.attempts())
        self.call(pc, "resolve", "ok", None, "local")
        self.check_remote(pc)
        self.sync()  # 올린 뒤에는 main 에 있는 다른 판과 다시 비교하지 않음. 비교하면 머지될 때까지 계속 멈춤
        pc.solve(); self.submit()
        self.merge()

    def test_resolve_without_remote_copy(self):
        mine = self.pc.solve()
        self.assertEqual(self.call(self.pc, "resolve", "nothing", mine, "remote")["backup"], None)
        self.assertEqual(self.call(self.pc, "resolve", "error", mine, "theirs")["pr_url"], None)

    # 손으로 git 을 쓴 폴더

    def stalled_pull(self, *options):
        """PR 이 squash 머지된 뒤 예전 안내대로 손으로 커밋하고 git pull 해서 충돌로 멈추게 함. 멈추기 전의 내 폴더를 돌려줌."""
        pc = self.pc
        pc.solve(); self.submit(); self.merge()
        mine = pc.solve()
        git(pc.path, "add", "-A"); git(pc.path, "commit", "-q", "-m", "2회차")
        self.assertNotEqual(git(pc.path, "pull", *options, "origin", "main", check=False).returncode, 0)
        self.assertNotEqual(pc.read(), mine)  # 충돌 표시가 들어감
        return mine

    def test_stalled_merge_from_manual_pull(self):
        mine = self.stalled_pull("--no-rebase")
        self.assertTrue(os.path.exists(self.pc.gitdir("MERGE_HEAD")))
        doctor = self.pc.flow.doctor()
        self.assertEqual((doctor["ok"], len(doctor["problems"])), (True, 1))
        result = self.sync(after=mine)
        self.assertIn(gitflow.M_UNSTALLED_KEPT, result["message"])
        self.assertTrue(os.path.isfile(os.path.join(result["backup"], "stalled", "profile.json")))
        self.submit()
        self.merge()

    def test_stalled_merge_in_a_copied_folder(self):
        """멈춘 병합이 있는 폴더를 통째로 복사해 온 경우. 인덱스의 파일 정보가 낡아 git merge --abort 가 거부함."""
        pc = self.pc
        mine = pc.solve()
        git(pc.path, "add", "-A"); git(pc.path, "commit", "-q", "-m", "내 풀이")
        self.server.add_problems("s17")
        git(pc.path, "fetch", "-q", "origin")
        git(pc.path, "merge", "--no-commit", "--no-ff", "origin/main")
        for base, dirs, files in os.walk(pc.path):
            dirs[:] = [d for d in dirs if d != ".git"]
            for name in files:
                os.utime(os.path.join(base, name), (1, 1))
        result = self.sync(after=mine)
        self.assertIn(gitflow.M_UNSTALLED_KEPT, result["message"])

    def test_stalled_rebase_from_manual_pull(self):
        mine = self.stalled_pull("--rebase")
        self.assertTrue(os.path.exists(self.pc.gitdir("rebase-merge")))
        result = self.submit(after=mine)  # 받기를 거치지 않고 제출부터 눌러도 됨
        self.assertIn(gitflow.M_UNSTALLED_KEPT, result["message"])
        self.sync(); self.merge()

    def test_stalled_pull_on_old_personal_branch(self):
        """예전 안내대로 만든 개인 브랜치(<ID>/day1)에서 git pull 이 병합 메시지 편집기에서 멈춘 경우.
        내 폴더 밖이 달라 보이는 것은 받아 오던 main 때문이라 개발 폴더로 보지 않고, 되돌린 뒤 받음."""
        pc = self.pc
        git(pc.path, "switch", "-q", "-c", pc.user + "/day1")
        mine = pc.solve()
        git(pc.path, "add", "-A"); git(pc.path, "commit", "-q", "-m", "1일차")
        self.server.add_problems("s17")
        git(pc.path, "fetch", "-q", "origin", "main")
        git(pc.path, "merge", "--no-commit", "--no-ff", "FETCH_HEAD")  # 편집기를 닫지 못하고 터미널을 끈 것과 같은 상태
        self.assertTrue(os.path.exists(pc.gitdir("MERGE_HEAD")))
        result = self.sync(after=mine)
        self.assertIn(gitflow.M_UNSTALLED_KEPT, result["message"])
        self.assertEqual(result["restart"], True)
        self.submit(); self.merge()

    def test_renamed_id_folder(self):
        """ID 를 잘못 넣고 풀다가 폴더 이름과 ID 를 고친 경우. study/<옛 ID> 브랜치에 남아 있어도 개발 폴더로 보지 않고 받음."""
        pc = self.pc
        pc.solve(); self.sync()  # study/alice 에 내 폴더가 커밋돼 있음
        renamed = os.path.join(pc.path, "submissions", "alicia")
        os.rename(pc.folder, renamed)
        flow = gitflow.GitFlow(pc.path, "alicia")
        flow.find_pr, flow.pr_wait = pc.find_pr, 0
        result = flow.sync()
        pc.flow.log += flow.log  # 금지 명령 검사에 포함
        self.assertEqual(result["status"], "ok", result)
        self.assertEqual(git(pc.path, "symbolic-ref", "--short", "HEAD").stdout.strip(), "study/alicia")
        self.assertFalse(os.path.exists(pc.folder))
        self.assertTrue(os.path.isfile(os.path.join(renamed, "profile.json")))
        self.assertEqual(flow.submit()["status"], "ok")
        self.assertTrue(self.server.folder("study/alicia", "alicia"))

    def test_manual_switch_to_main(self):
        pc = self.pc
        pc.solve(); self.submit(); self.merge()  # 1차 풀이는 main 에 들어감
        mine = pc.solve(); self.sync(); self.submit()  # 2차 풀이는 PR 로 열려 있음
        git(pc.path, "switch", "-q", "main")  # 예전 안내 습관: git switch main → git pull
        git(pc.path, "pull", "-q", "--ff-only", "origin", "main")
        self.assertNotEqual(pc.read(), mine)  # 내 폴더가 옛 상태로 바뀜
        result = self.sync(after=mine)  # 2차 풀이가 돌아옴
        self.assertEqual(result["changed"], True)
        pc.solve(); self.submit()
        self.merge()

    def test_detached_head(self):
        pc = self.pc
        self.server.add_problems("s17"); self.server.add_problems("s18")
        git(pc.path, "pull", "-q", "origin", "main")
        git(pc.path, "checkout", "-q", "--detach", "HEAD~1")  # 옛 커밋을 구경하다 그대로 둠
        pc.solve()
        self.sync(); self.submit()
        self.merge()

    def test_dev_branch(self):
        pc = self.pc
        pc.solve()
        git(pc.path, "switch", "-q", "-c", "feature/gui")
        write(os.path.join(pc.path, "study.py"), "# 개발 중(커밋함)\n", "a")
        git(pc.path, "commit", "-q", "-am", "GUI 개발")
        write(os.path.join(pc.path, "gui", "app.py"), "# 개발 중(커밋 안 함)\n", "a")
        state = pc.state()
        self.submit()  # 제출은 이 컴퓨터를 바꾸지 않으므로 개발 브랜치에서도 됨(내 폴더만 올라감)
        result = self.sync(expect="blocked")  # 받기는 문제·도구 파일을 바꾸므로 멈춤
        self.assertEqual(result["message"], gitflow.M_DEV % "feature/gui")
        self.assertEqual(pc.state(), state)
        self.merge()

    def test_stalled_work_on_dev_branch_is_left_alone(self):
        pc = self.pc
        pc.solve()
        git(pc.path, "switch", "-q", "-c", "feature/gui")
        write(os.path.join(pc.path, "problems", "s01", "quiz.md"), "개발 브랜치의 수정\n", "a")
        git(pc.path, "commit", "-q", "-am", "문제 수정")
        self.server.add_problems("s17")
        self.assertNotEqual(git(pc.path, "pull", "--no-rebase", "origin", "main", check=False).returncode, 0)
        state = pc.state()
        result = pc.flow.submit()  # 스터디장이 충돌을 풀던 중
        self.assertEqual((result["status"], result["backup"]), ("ok", None))
        self.assertEqual(pc.flow.sync()["status"], "blocked")
        self.assertEqual(pc.state(), state)
        self.assertTrue(os.path.exists(pc.gitdir("MERGE_HEAD")))
        git(pc.path, "merge", "--abort")
        self.check_remote(pc)

    # 올리지 못하는 경우

    def test_offline(self):
        pc = self.pc
        pc.solve(); self.submit()
        pc.offline()
        pc.solve()
        self.assertEqual(self.sync(expect="offline")["message"], gitflow.M_OFFLINE["sync"])
        self.assertEqual(self.submit(expect="offline")["message"], gitflow.M_OFFLINE["submit"])
        pc.solve()
        self.submit(expect="offline")
        self.server.add_problems("s17"); self.merge()  # 오프라인인 동안에도 원격은 움직임
        pc.offline(False)
        self.submit()
        self.merge()

    def test_git_identity_not_configured(self):
        os.environ["GIT_CONFIG_GLOBAL"] = self.config_no_identity
        pc = self.pc
        pc.solve()
        self.sync(); self.submit()
        os.environ["GIT_CONFIG_GLOBAL"] = self.config
        author = git(self.origin, "log", "-1", "--format=%an <%ae> / %cn <%ce>", "study/alice").stdout.strip()
        self.assertEqual(author, "alice <alice@users.noreply.github.com> / alice <alice@users.noreply.github.com>")
        self.assertEqual(git(pc.path, "config", "--local", "user.name", check=False).stdout, "")  # 설정은 건드리지 않음

    def test_broken_files_are_not_uploaded(self):
        pc = self.pc
        pc.solve(); self.submit()
        tip = self.server.rev("study/alice")
        mine = pc.solve()
        quiz = os.path.join(pc.folder, "r01", "quiz.py")
        write(quiz, "s01_Q1 = (\n", "a")
        result = self.submit(expect="blocked")
        self.assertRegex(result["message"], r"r01/quiz\.py \d+번째 줄")
        write(os.path.join(pc.folder, "profile.json"), "{")
        result = self.submit(expect="blocked")
        self.assertIn("profile.json", result["message"])
        self.assertEqual(len(result["detail"].splitlines()), 2)
        self.assertEqual(self.sync(expect="blocked")["message"], gitflow.M_BROKEN_PROFILE)
        self.assertEqual(self.server.rev("study/alice"), tip)
        for rel in ("profile.json", "r01/quiz.py"):
            with open(os.path.join(pc.folder, rel), "wb") as f:
                f.write(mine["submissions/alice/" + rel])
        self.submit()

    def test_login_needed_and_permission_denied(self):
        pc = self.pc
        pc.solve()

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):  # push 가 처음 보내는 요청(info/refs)에 GitHub 처럼 답함
                if self.server.code is None:
                    self.server.release.wait(30)
                    return
                self.send_response(self.server.code)
                if self.server.code == 401:
                    self.send_header("WWW-Authenticate", 'Basic realm="GitHub"')
                self.send_header("Content-Length", "0")
                self.end_headers()

            def log_message(self, *args):
                pass

        web = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        web.daemon_threads, web.release = True, threading.Event()
        threading.Thread(target=web.serve_forever, daemon=True).start()
        self.addCleanup(web.server_close)
        self.addCleanup(web.shutdown)
        self.addCleanup(web.release.set)
        git(pc.path, "config", "remote.origin.pushurl", "http://127.0.0.1:%d/%s/%s.git" % (web.server_address[1], OWNER, REPO))
        git(pc.path, "config", "http.proxy", "")
        web.code = 401  # 로그인한 적 없음
        result = self.submit(expect="auth")
        self.assertEqual(result["message"], gitflow.M_LOGIN % "올리지")
        self.assertIn("terminal prompts disabled", result["detail"])
        web.code = 403  # 초대 수락 전이거나 다른 계정
        result = self.submit(expect="auth")
        self.assertEqual(result["message"], gitflow.M_DENIED % ("올리지", "alice"))
        web.code = None  # 응답이 없음
        with mock.patch.object(gitflow, "PUSH_PATIENCE", 0.01):
            self.assertEqual(self.submit(expect="offline")["message"], gitflow.M_SLOW)
        git(pc.path, "config", "--unset", "remote.origin.pushurl")
        self.assertEqual(self.server.rev("study/alice"), "")
        self.submit()

    def test_index_lock_left_behind(self):
        pc = self.pc
        pc.solve(); self.sync(); self.submit()
        self.server.add_problems("s17")
        pc.solve()
        write(pc.gitdir("index.lock"), "")  # 다른 git 프로그램이 돌고 있거나 비정상 종료로 남은 잠금
        self.submit()  # 제출은 진짜 인덱스를 쓰지 않음
        result = self.sync(expect="error")  # 받기는 멈추지만 풀이는 안 바뀜
        self.assertIn("index.lock", result["detail"])
        os.remove(pc.gitdir("index.lock"))
        self.sync()

    @unittest.skipIf(os.name == "nt" or (hasattr(os, "geteuid") and os.geteuid() == 0), "읽기 전용 폴더로 파일 잠금을 흉내 낼 수 없는 환경입니다")
    def test_file_that_cannot_be_replaced(self):
        pc = self.pc
        pc.solve(); self.submit()
        self.server.add_problems("s17")
        locked = os.path.join(pc.path, "problems", "s01")
        os.chmod(locked, stat.S_IRUSR | stat.S_IXUSR)  # 백신·편집기가 파일을 잡고 있는 상황을 흉내
        try:
            result = self.call(pc, "sync", "blocked")
        finally:
            os.chmod(locked, stat.S_IRWXU)
        self.assertIn("problems/s01/quiz.md", result["message"])
        self.assertEqual((result["restart"], result["changed"]), (True, True))  # 도구 파일은 이미 새 버전으로 바뀜
        pc.solve()  # 사용자는 계속 풂
        self.sync()  # 다시 누르면 회복
        self.assertTrue(os.path.isfile(os.path.join(pc.path, "problems", "s17", "quiz.md")))
        self.submit()

    # 환경 점검

    def test_doctor(self):
        pc = self.pc
        self.assertEqual(pc.flow.doctor(), {"ok": True, "git": True, "repo": True, "remote": "%s/%s" % (OWNER, REPO),
                                            "branch": "main", "problems": []})
        git(pc.path, "config", "remote.origin.url", self.origin)  # GitHub 가 아닌 원격: 올릴 수는 있지만 PR 주소가 없음
        doctor = pc.flow.doctor()
        self.assertEqual((doctor["ok"], doctor["remote"], len(doctor["problems"])), (True, None, 1))
        pc.solve()
        result = self.call(pc, "submit", "ok")
        self.assertEqual((result["pr_url"], result["message"]), (None, gitflow.M_PUSHED % "study/alice"))
        git(pc.path, "remote", "remove", "origin")
        self.assertEqual(pc.flow.doctor()["ok"], False)
        self.assertEqual(pc.flow.submit()["status"], "not_repo")

    def test_folder_from_zip_and_missing_git(self):
        folder = os.path.join(self.tmp, "zip")
        write(os.path.join(folder, "submissions", "alice", "profile.json"), "{}")
        flow = gitflow.GitFlow(folder, "alice")
        doctor = flow.doctor()
        self.assertEqual((doctor["ok"], doctor["git"], doctor["repo"]), (False, True, False))
        for result in (flow.sync(), flow.submit(), flow.resolve("remote")):
            self.assertEqual((result["status"], result["message"]), ("not_repo", gitflow.M_NOT_REPO % "alice"))
        with mock.patch.object(gitflow.shutil, "which", return_value=None):
            doctor = self.pc.flow.doctor()
            self.assertEqual((doctor["ok"], doctor["git"], doctor["problems"]), (False, False, [gitflow.M_NO_GIT]))
            self.assertEqual(self.pc.flow.sync()["status"], "no_git")
        self.assertEqual(gitflow.GitFlow(self.pc.path, "../bob").submit()["status"], "error")


class HelperTest(unittest.TestCase):
    def test_remote_slug(self):
        for url in ("https://github.com/WaterMinCho/rokey-python-study.git", "https://github.com/WaterMinCho/rokey-python-study",
                    "https://github.com/WaterMinCho/rokey-python-study/", "git@github.com:WaterMinCho/rokey-python-study.git",
                    "ssh://git@github.com/WaterMinCho/rokey-python-study.git", "https://user:token@github.com/WaterMinCho/rokey-python-study.git\n"):
            self.assertEqual(gitflow.remote_slug(url), ("WaterMinCho", "rokey-python-study"), url)
        for url in ("", None, "/tmp/origin.git", "https://gitlab.com/a/b.git", "https://github.com/only-owner"):
            self.assertIsNone(gitflow.remote_slug(url), url)

    def test_new_pr_url(self):
        self.assertEqual(gitflow.new_pr_url(OWNER, REPO, "study/alice", "alice 풀이"), NEW_PR)
        long_title = gitflow.new_pr_url(OWNER, REPO, "study/alice", "가" * 300)
        self.assertEqual(long_title, NEW_PR.split("&")[0])  # 2,000자를 넘기면 제목을 뺌

    def test_remote_problem(self):
        for kind, text in (
                ("login", "fatal: could not read Username for 'https://github.com': terminal prompts disabled"),
                ("login", "remote: Invalid username or password.\nfatal: Authentication failed for 'https://github.com/o/r.git/'"),
                ("login", "git@github.com: Permission denied (publickey).\nfatal: Could not read from remote repository."),
                ("denied", "remote: Permission to o/r.git denied to someone.\nfatal: unable to access 'https://github.com/o/r.git/': The requested URL returned error: 403"),
                ("denied", "ERROR: Permission to o/r.git denied to someone.\nfatal: Could not read from remote repository."),
                ("offline", "fatal: unable to access 'https://github.com/o/r.git/': Could not resolve host: github.com"),
                ("offline", "ssh: Could not resolve hostname github.com: nodename nor servname provided\nfatal: Could not read from remote repository."),
                (None, "fatal: bad object 1234")):
            self.assertEqual(gitflow.remote_problem(text), kind, text)

    def test_find_open_pr_never_raises(self):
        with mock.patch.object(gitflow.urllib.request, "urlopen", side_effect=OSError("오프라인")) as urlopen:
            self.assertIsNone(gitflow.find_open_pr(OWNER, REPO, "study/alice"))
        request = urlopen.call_args[0][0]
        self.assertEqual(request.full_url, "https://api.github.com/repos/%s/%s/pulls?head=study-owner%%3Astudy%%2Falice&state=open" % (OWNER, REPO))
        self.assertEqual(urlopen.call_args[1], {"timeout": 5})
        reply = mock.MagicMock()
        reply.__enter__.return_value.read.return_value = json.dumps([{"html_url": OPEN_PR}]).encode("utf-8")
        with mock.patch.object(gitflow.urllib.request, "urlopen", return_value=reply):
            self.assertEqual(gitflow.find_open_pr(OWNER, REPO, "study/alice"), OPEN_PR)
        reply.__enter__.return_value.read.return_value = b"[]"
        with mock.patch.object(gitflow.urllib.request, "urlopen", return_value=reply):
            self.assertIsNone(gitflow.find_open_pr(OWNER, REPO, "study/alice"))


if __name__ == "__main__":
    unittest.main()
