#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""화면의 [문제 받기]·[제출] 이 부르는 git 작업.

submissions/<ID>/ 는 나만 쓰므로 작업 폴더의 내용을 정답으로 봄. 그 밖은 origin/main 과 같게 맞춤.
병합하지 않고 "origin/main 의 트리 + 내 폴더"로 커밋을 직접 만들어(임시 인덱스, commit-tree)
study/<ID> 브랜치에 fast-forward 로만 올림. 강제 푸시·reset --hard·clean·stash 는 쓰지 않음.

공개 메서드는 예외를 올리지 않고 dict 를 돌려줌. 브라우저는 화면이 pr_url 로 열고 여기서는 열지 않음.
git 결과는 종료 코드와 --porcelain 출력으로 판정하고, 사람용 문구는 원격 실패 이유를 가릴 때만 봄(remote_problem).
"""
import collections
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import traceback
import urllib.parse
import urllib.request

import study

MAIN = "refs/remotes/origin/main"
MAIN_REFSPEC = "+refs/heads/main:" + MAIN  # --single-branch 로 clone 한 폴더에서도 받게 직접 적음
TOOL_FILES = ("study.py", "adaptive.py", "session.py", "mdlite.py", "gitflow.py", "bootstrap.py")
TOOL_DIRS = ("gui/",)
STALLED = (("MERGE_HEAD", "merge"), ("rebase-merge", "rebase"), ("rebase-apply", "rebase"),
           ("CHERRY_PICK_HEAD", "cherry-pick"), ("REVERT_HEAD", "revert"))
PUSH_PATIENCE = 5  # push 제한 시간 = timeout 의 몇 배. 첫 push 는 브라우저 로그인 창에서 시간이 걸림
FETCH_LIMIT = 20  # fetch 는 로그인 없이 되고, 시작할 때 화면이 이 시간만큼 기다리므로 짧게 잡음
PR_WAIT, PR_POLL = 30, 3  # 올린 뒤 저장소의 Actions 가 PR 을 만들 때까지 기다리는 시간과 확인 간격(초)
URL_LIMIT = 2000
REMOTE_RE = re.compile(r"github\.com[:/]+([^/\s:]+)/([^/\s]+?)(?:\.git)?/?$")
BROKEN = object()  # profile.json 이 있는데 읽지 못함

# 원격 실패 이유를 가리는 문구. LC_ALL=C 의 영어 출력을 소문자로 비교하고, 위에서부터 먼저 맞는 것을 씀
REMOTE_MARKS = (
    ("login", ("terminal prompts disabled", "authentication failed", "error: 401", "permission denied (publickey")),
    ("denied", ("error: 403", "denied to ", "write access to repository not granted")),
    ("offline", ("could not resolve host", "unable to access", "could not read from remote repository",
                 "does not appear to be a git repository", "failed to connect", "timed out")),
)

SAFE = "풀이는 이 컴퓨터에 그대로 있습니다"
M_NO_GIT = "git 이 설치돼 있지 않아 문제 받기와 제출을 할 수 없습니다. 풀이와 채점은 지금도 되니, git 을 설치한 뒤 프로그램을 다시 실행해 주세요."
M_NOT_REPO = ("이 폴더는 저장소를 clone 한 폴더가 아니라(ZIP 으로 받은 폴더 등) 문제 받기와 제출을 할 수 없습니다. "
              "안내대로 clone 한 폴더에서 실행하고, 지금까지 푼 submissions/%s 폴더는 그 폴더로 복사해 주세요.")
M_BAD_USER = "ID 가 올바르지 않아 문제 받기와 제출을 할 수 없습니다: %r"
M_OFFLINE = {"sync": "인터넷에 연결되지 않아 새 문제를 받지 못했습니다. 받아 둔 문제로 계속 풀 수 있습니다.",
             "submit": "인터넷에 연결되지 않아 올리지 못했습니다. %s. 연결한 뒤 [제출]을 다시 눌러 주세요." % SAFE}
M_SLOW = "저장소가 제때 응답하지 않아 멈췄습니다(%s). 인터넷 연결과 로그인 창을 확인한 뒤 다시 눌러 주세요." % SAFE
M_LOGIN = "깃허브 로그인이 필요해 %%s 못했습니다(%s). 스터디장이 안내한 방법으로 로그인한 뒤 다시 눌러 주세요." % SAFE
M_DENIED = ("저장소에 접근할 권한이 없어 %%s 못했습니다(%s). "
            "스터디장의 초대를 수락했는지, 로그인한 깃허브 계정이 %%s 인지 확인한 뒤 다시 눌러 주세요." % SAFE)
M_BEHIND = "원격의 내 브랜치가 방금 또 바뀌어 올리지 못했습니다(%s). 잠시 뒤 [제출]을 다시 눌러 주세요." % SAFE
M_ERROR = {"sync": "문제를 받다가 오류가 났습니다(풀이는 이 컴퓨터에 남아 있습니다). [자세히]의 내용을 스터디장에게 보내 주세요.",
           "submit": "제출하다가 오류가 났습니다(풀이는 이 컴퓨터에 남아 있습니다). [자세히]의 내용을 스터디장에게 보내 주세요."}
M_DIVERGED = "다른 컴퓨터에서 올린 풀이가 있고, 이 컴퓨터의 풀이와 이어지지 않습니다. 덮어쓰지 않고 멈췄으니 어느 쪽을 쓸지 골라 주세요."
M_BROKEN_PROFILE = "풀이 기록 파일(profile.json)을 읽을 수 없어 멈췄습니다. 풀이 폴더는 건드리지 않았습니다."
M_BROKEN = "읽을 수 없는 풀이 파일이 있어 올리지 않았습니다: %s 고친 뒤 [제출]을 다시 눌러 주세요."
M_DEV = "지금 '%s' 에서 문제·도구 파일을 고치는 중이라 [문제 받기]는 하지 않았습니다. 제출은 그대로 할 수 있습니다."
M_LOCKED = "파일 %%d개를 새 버전으로 바꾸지 못했습니다: %%s. 이 파일을 연 프로그램을 닫고 [문제 받기]를 다시 눌러 주세요(%s)." % SAFE
M_UNSTALLED = "멈춰 있던 git 작업을 되돌렸습니다."
M_UNSTALLED_KEPT = "멈춰 있던 git 작업을 되돌렸습니다. 그 전의 풀이 폴더는 보관함에 복사해 두었습니다."
M_TOOK = "올려 둔 풀이를 가져왔습니다."
M_TOOK_OVER = "올려 둔 풀이를 가져왔습니다. 이 컴퓨터에 있던 풀이는 보관함에 복사해 두었습니다."
M_PARKED = "풀이 폴더 밖의 파일 %d개가 바뀌어 있어 원래대로 되돌렸습니다. 바꾼 내용은 보관함에 복사해 두었습니다."
M_RESTART = "프로그램이 새 버전으로 바뀌었습니다. 다시 시작하면 적용됩니다."
M_NEW = "새 문제를 받았습니다."
M_LATEST = "문제가 이미 최신입니다."
M_NOTHING = "새로 제출할 풀이가 없습니다. 지난번에 올린 내용이 이미 반영돼 있습니다."
M_EMPTY = "아직 제출할 풀이가 없습니다. 문제를 푼 뒤 다시 눌러 주세요."
M_ADDED = "제출했습니다. 열려 있는 PR 에 이어서 올라갔습니다."
M_SAME = "이미 제출돼 있습니다. 바뀐 내용이 없어 그대로 두었습니다."
M_CREATED = "제출했습니다. PR 이 자동으로 만들어졌습니다."
M_OPEN_PR = ("올렸습니다. PR 은 잠시 뒤 자동으로 만들어집니다. 브라우저에 열리는 화면에 [View pull request] 가 보이면 그것을, "
             "[Create pull request] 가 보이면 그 단추를 눌러 주세요.")
M_NO_OPEN_PR = ("지난번에 올린 내용과 같아 새로 올리지 않았고, 열려 있는 PR 은 찾지 못했습니다. 브라우저에 열리는 화면에 "
                "[View pull request] 가 보이면 그것을, [Create pull request] 가 보이면 그 단추를 눌러 주세요.")
M_PUSHED = "%s 브랜치에 올렸습니다."
M_SPELLING = ("ID '%%s' 가 이미 있는 풀이 폴더 '%%s' 와 대소문자만 다릅니다(%s). submissions 폴더 안의 '%%s' 폴더 이름을 "
              "'%%s' 로 바꾼 뒤 프로그램을 다시 실행해 주세요.") % SAFE
M_NO_REMOTE_COPY = "가져올 원격 풀이가 없습니다. 이 컴퓨터의 풀이는 그대로 두었습니다."
M_BAD_CHOICE = "고를 수 있는 것은 remote(원격 풀이 가져오기)와 local(이 컴퓨터 풀이로 올리기)입니다: %r"

Run = collections.namedtuple("Run", "args code out err")  # git 한 번의 결과. code 가 None 이면 시간 초과


class GitError(Exception):
    """실패한 git 명령. 문구는 결과의 detail 에 실림."""

    def __init__(self, run):
        how = "시간 초과" if run.code is None else "exit %d" % run.code
        super().__init__("git %s → %s\n%s" % (run.args, how, (run.err or run.out).strip()))


class Stop(Exception):
    """작업을 멈추고 이 상태·문구로 결과를 돌려줌."""

    def __init__(self, status, message, detail=""):
        super().__init__(message)
        self.status, self.message, self.detail = status, message, detail


def remote_slug(url):
    """origin 주소(https·ssh)에서 (owner, repo). GitHub 주소가 아니면 None."""
    m = REMOTE_RE.search((url or "").strip())
    return (m.group(1), m.group(2)) if m else None


def remote_problem(stderr):
    """fetch·push 가 원격 때문에 실패한 이유: 'login' | 'denied' | 'offline' | None.
    git 이 기계가 읽을 형식으로 주지 않아 영어 문구에서 찾음."""
    low = stderr.lower()
    for kind, marks in REMOTE_MARKS:
        if any(mark in low for mark in marks):
            return kind
    return None


def find_open_pr(owner, repo, branch, timeout=5):
    """그 브랜치로 열려 있는 PR 의 주소(익명 GitHub REST). 없거나 조회하지 못하면 None."""
    query = urllib.parse.urlencode({"head": "%s:%s" % (owner, branch), "state": "open"})
    request = urllib.request.Request("https://api.github.com/repos/%s/%s/pulls?%s" % (owner, repo, query),
                                     headers={"Accept": "application/vnd.github+json", "User-Agent": "rokey-python-study"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            pulls = json.loads(response.read().decode("utf-8"))
        return pulls[0]["html_url"] if pulls else None
    except Exception:  # 오프라인이나 조회 한도 초과. 부른 쪽이 새 PR 화면 주소로 대신함
        return None


def new_pr_url(owner, repo, branch, title):
    """브랜치를 올린 뒤에 여는 'PR 만들기' 화면 주소."""
    url = "https://github.com/%s/%s/compare/main...%s?quick_pull=1" % (owner, repo, urllib.parse.quote(branch, safe="/"))
    titled = url + "&title=" + urllib.parse.quote_plus(title)
    return titled if len(titled) <= URL_LIMIT else url


def is_tool(path):
    return path in TOOL_FILES or path.startswith(TOOL_DIRS)


class GitFlow:
    """sync()·submit()·resolve() 는 아래 모양의 dict 를 돌려줌.
        status   ok | nothing | offline | auth | diverged | blocked | no_git | not_repo | error
        message  사용자에게 보여 줄 문구
        detail   디버깅용(명령·stderr)
        pr_url   브라우저로 열 주소 또는 None
        restart  도구 파일이 바뀌어 프로그램을 다시 시작해야 하면 True
        changed  문제·도구 파일이나 내 폴더가 바뀌어 세션을 새로 만들어야 하면 True
        backup   이번에 사본을 보관한 폴더(.git/study-backup/<시각>) 또는 None
    한 번에 한 작업만 부름. 부르는 동안 답안 자동 저장을 멈춰야 쓰다 만 파일이 올라가지 않음.
    find_pr(owner, repo, branch) 는 열린 PR 주소를 찾는 함수고, log 는 부른 git 명령의 기록임."""

    def __init__(self, root, user, timeout=60):
        self.root = os.path.abspath(root)
        self.user = user
        self.timeout = timeout
        self.rel = "submissions/%s" % user
        self.folder = os.path.join(self.root, "submissions", str(user))
        self.branch = "study/%s" % user
        self.tip_ref = "refs/remotes/origin/" + self.branch
        self.outside = [".", ":(exclude)" + self.rel]
        self.find_pr = find_open_pr  # 테스트에서는 네트워크를 타지 않는 함수로 바꿈
        self.fetch_timeout = min(timeout, FETCH_LIMIT)
        self.pr_wait, self.sleep = PR_WAIT, time.sleep
        self.log = []
        self._gitdir_path = None
        self._op, self._notes, self._backup, self._changed = "sync", [], None, False
        self._url = self._base = self._tip = ""  # origin 주소, 받아 온 main 과 원격의 내 브랜치 끝(커밋 해시, 없으면 "")

    # 공개 메서드

    def doctor(self):
        """받기·제출을 할 수 있는 폴더인지 네트워크 없이 확인함.
        ok 는 시도할 수 있는지(git·clone 한 폴더·origin)를 뜻하고, problems 에는 ok 를 막지 않는 알림도 들어감."""
        info = {"ok": False, "git": False, "repo": False, "remote": None, "branch": None, "problems": []}
        problems = info["problems"]
        try:
            info["git"] = bool(shutil.which("git")) and self._git("--version", check=False).code == 0
            if not info["git"]:
                problems.append(M_NO_GIT)
                return info
            info["repo"] = os.path.exists(os.path.join(self.root, ".git")) and self._ok("rev-parse", "--git-dir")
            if not info["repo"]:
                problems.append(M_NOT_REPO % self.user)
                return info
            url = self._out("config", "--get", "remote.origin.url", check=False)
            slug = remote_slug(url)
            info["remote"] = "%s/%s" % slug if slug else None
            info["branch"] = self._branch() or None
            info["ok"] = bool(url)
            if not url:
                problems.append(M_NOT_REPO % self.user)
            elif not slug:
                problems.append("origin 이 GitHub 저장소 주소가 아니라 PR 주소를 만들 수 없습니다.")
            if url and not self._has(MAIN):
                problems.append("아직 main 을 받은 적이 없습니다. [문제 받기]를 누르면 받아 옵니다.")
            stalled = self._stalled()
            if stalled:
                problems.append("멈춰 있는 git 작업(%s)이 있습니다. [문제 받기]를 누르면 풀이를 보관한 뒤 되돌립니다." % ", ".join(stalled))
        except Exception as error:
            info["ok"] = False
            problems.append("git 상태를 확인하지 못했습니다: %s" % error)
        return info

    def sync(self):
        """내 폴더는 그대로 두고 그 밖을 최신 main 으로 맞춤."""
        return self._run("sync", self._sync)

    def submit(self):
        """내 폴더를 study/<ID> 에 올리고 PR 주소를 돌려줌. 이 컴퓨터의 파일·브랜치는 바꾸지 않음.
        멈춘 git 작업이 있거나 원격에 더 새 판이 있을 때만 바꾸고, 그때는 문구와 backup 으로 알림."""
        return self._run("submit", self._submit)

    def resolve(self, choice):
        """"diverged" 로 멈춘 뒤 사용자가 고른 쪽을 적용함.
        "remote" 면 원격 풀이를 가져오고 이 컴퓨터 것은 보관함에 복사함. "local" 이면 이 컴퓨터 풀이를 올림."""
        if choice == "remote":
            return self._run("sync", self._take_remote)
        if choice == "local":
            return self._run("submit", lambda: self._submit(force=True))
        return self._run("sync", lambda: self._result("error", M_BAD_CHOICE % (choice,)))

    # 공통 처리

    def _run(self, op, work):
        self._op, self._notes, self._backup, self._changed = op, [], None, False
        self._url = self._base = self._tip = ""
        try:
            if not study.USER_RE.fullmatch(str(self.user)):
                raise Stop("error", M_BAD_USER % (self.user,))
            if not shutil.which("git"):
                raise Stop("no_git", M_NO_GIT)
            if os.path.exists(os.path.join(self.root, ".git")):
                self._url = self._out("config", "--get", "remote.origin.url", check=False)
            if not self._url:
                raise Stop("not_repo", M_NOT_REPO % self.user)
            return work()
        except Stop as stop:
            return self._result(stop.status, stop.message, stop.detail)
        except Exception as error:
            return self._result("error", M_ERROR[op], str(error) if isinstance(error, GitError) else traceback.format_exc())

    def _result(self, status, message, detail="", pr_url=None, restart=False, changed=False):
        return {"status": status, "message": " ".join(self._notes + [message]).strip(), "detail": detail, "pr_url": pr_url,
                "restart": restart, "changed": changed or self._changed, "backup": self._backup}

    # git 부르기

    def _git(self, *args, check=True, env=None, timeout=None):
        """git 을 한 번 부름. 시간 초과로 git 을 끝냈을 때 남은 자식(git-remote-https 등)이 파이프를 쥐고 있으면
        읽기가 끝나지 않아서, 출력은 파이프 대신 임시 파일로 받음."""
        full = dict(os.environ, GIT_TERMINAL_PROMPT="0", LC_ALL="C")
        full.update(env or {})
        with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
            try:
                code = subprocess.run(["git", "-c", "core.quotepath=false"] + list(args), cwd=self.root, env=full,
                                      stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                      timeout=timeout or self.timeout, creationflags=study.NO_WINDOW).returncode
            except subprocess.TimeoutExpired:
                code = None
            texts = []
            for stream in (out, err):
                stream.seek(0)
                texts.append(stream.read().decode("utf-8", "replace"))
        run = Run(" ".join(args), code, texts[0], texts[1])
        self.log.append("git %s → %s" % (run.args, code))
        if check and code != 0:
            raise GitError(run)
        return run

    def _out(self, *args, **options):
        return self._git(*args, **options).out.strip()

    def _ok(self, *args):
        return self._git(*args, check=False).code == 0

    def _paths(self, *args):
        """-z 로 받은 경로 목록."""
        return [path for path in self._git(*args).out.split("\0") if path]

    def _gitdir(self):
        if self._gitdir_path is None:
            self._gitdir_path = os.path.join(self.root, self._out("rev-parse", "--git-dir"))
        return self._gitdir_path

    def _branch(self):
        """지금 브랜치 이름. 분리된 HEAD 면 ""."""
        return self._out("symbolic-ref", "-q", "--short", "HEAD", check=False)

    def _commit_of(self, rev):
        """커밋 해시. 없으면 ""."""
        return self._out("rev-parse", "-q", "--verify", rev + "^{commit}", check=False)

    def _has(self, rev):
        return bool(self._commit_of(rev))

    def _is_ancestor(self, old, new):
        return self._ok("merge-base", "--is-ancestor", old, new)

    def _folder_tree(self, rev):
        """그 커밋에 든 내 폴더의 트리 해시. 폴더가 없으면 ""."""
        return self._out("rev-parse", "-q", "--verify", "%s:%s" % (rev, self.rel), check=False)

    # 보관함

    def _backup_dir(self):
        """이번 작업의 보관함(.git/study-backup/<시각>). 처음 필요할 때 만듦."""
        if not self._backup:
            base = os.path.join(self._gitdir(), "study-backup", time.strftime("%Y%m%d-%H%M%S"))
            path, n = base, 1
            while os.path.exists(path):
                n += 1
                path = "%s-%d" % (base, n)
            os.makedirs(path)
            self._backup = path
        return self._backup

    def _keep_folder(self, label):
        """내 폴더를 보관함의 label 폴더로 통째로 복사함. 복사할 파일이 없으면 False."""
        if not any(files for _, _, files in os.walk(self.folder)):
            return False
        shutil.copytree(self.folder, os.path.join(self._backup_dir(), label), ignore=shutil.ignore_patterns("__pycache__"))
        return True

    # 단계

    def _stalled(self):
        """멈춰 있는 git 작업의 종류(merge·rebase·cherry-pick·revert)."""
        found = [command for name, command in STALLED if os.path.exists(os.path.join(self._gitdir(), name))]
        return sorted(set(found))

    def _preflight(self):
        """손으로 git 을 쓰다 멈춘 병합·리베이스를 되돌림. 되돌리면 그동안 고친 내용이 사라질 수 있어 내 폴더를 먼저 보관함."""
        stalled = self._stalled()
        if not stalled:
            return
        kept = self._keep_folder("stalled")
        self._git("update-index", "-q", "--refresh", check=False)  # 폴더를 복사해 왔으면 인덱스의 파일 정보가 낡아 --abort 가 거부함
        for command in stalled:
            self._git(command, "--abort")
        self._notes.append(M_UNSTALLED_KEPT if kept else M_UNSTALLED)

    def _dev_branch(self):
        """main·study/<ID> 가 아닌 곳에서 내 폴더 밖을 고치고 있으면(스터디장의 개발 폴더) 그 브랜치 이름, 아니면 None."""
        name = self._branch()
        if name in ("main", self.branch) or name.startswith("study/") or not self._has(MAIN):  # study/* 는 이 프로그램이 만든 브랜치(ID 를 고친 뒤 등)
            return None
        if self._ok("diff", "--quiet", MAIN + "...HEAD", "--", *self.outside) \
                and (self._ok("diff", "--quiet", "HEAD", "--", *self.outside) or self._pulling()):
            return None
        return name or "분리된 HEAD"

    def _pulling(self):
        """손으로 친 git pull 이 병합 도중에 멈춘 상태인지 봄. 내 폴더 밖이 받아 오던 커밋(MERGE_HEAD)과 같으면 개발 중인 수정이 아님."""
        return self._has("MERGE_HEAD") and self._ok("diff", "--quiet", "MERGE_HEAD", "--", *self.outside)

    def _remote_stop(self, kind, text, verb):
        """원격 때문에 실패한 fetch·push 를 사용자 안내로 바꿔 멈춤."""
        if kind == "login":
            raise Stop("auth", M_LOGIN % verb, text)
        if kind == "denied":
            raise Stop("auth", M_DENIED % (verb, self.user), text)
        if kind == "slow":
            raise Stop("offline", M_SLOW, text)
        if kind == "offline":
            raise Stop("offline", M_OFFLINE[self._op], text)
        raise Stop("error", M_BEHIND if kind == "behind" else M_ERROR[self._op], text)

    def _fetch(self):
        """최신 main 과 내 브랜치를 받음. 원격에서 지워진 브랜치는 로컬의 origin/ 참조도 지움.
        남의 브랜치는 받지 않음. 대소문자만 다른 브랜치가 원격에 둘 있으면 Windows·macOS 에서는 fetch 가 통째로 실패함."""
        mine = "+refs/heads/%s*:refs/remotes/origin/%s*" % (self.branch, self.branch)  # 끝의 * 가 있어야 브랜치가 없을 때도 실패하지 않음
        run = self._git("fetch", "--prune", "origin", MAIN_REFSPEC, mine, check=False, timeout=self.fetch_timeout)
        if run.code != 0:
            kind = "slow" if run.code is None else remote_problem(run.err)
            self._remote_stop(kind if kind in ("slow", "login", "denied") else "offline", "git %s\n%s" % (run.args, run.err.strip()), "받지")
        self._base = self._out("rev-parse", MAIN + "^{commit}")
        self._tip = self._commit_of(self.tip_ref)
        self._check_spelling()

    def _check_spelling(self):
        """내 ID 와 대소문자만 다른 풀이 폴더가 이 컴퓨터나 main 에 있으면 아무것도 바꾸기 전에 멈춤.
        Windows·macOS 는 둘을 같은 폴더로 열지만 git 은 다른 경로로 봐서, 내 풀이를 폴더 밖 파일로 알고 되돌림."""
        parent = os.path.dirname(self.folder)
        names = set(os.listdir(parent)) if os.path.isdir(parent) else set()
        names |= {path.rsplit("/", 1)[-1] for path in self._paths("ls-tree", "-z", "--name-only", self._base, "submissions/")}
        others = sorted(name for name in names if name != self.user and name.lower() == self.user.lower())
        if others:
            raise Stop("blocked", M_SPELLING % (self.user, others[0], self.user, others[0]))

    def _attempts(self, ref=None):
        """profile.json 의 시도 기록(덧붙기만 하는 목록). ref 가 없으면 작업 폴더의 것. 파일이 없으면 None, 못 읽으면 BROKEN."""
        if ref is None:
            path = os.path.join(self.folder, "profile.json")
            if not os.path.isfile(path):
                return None
            try:
                text = study.read_text(path)
            except (OSError, ValueError):
                return BROKEN
        else:
            run = self._git("show", "%s:%s/profile.json" % (ref, self.rel), check=False)
            if run.code != 0:
                return None
            text = run.out
        try:
            return [(a["round"], a["item"], a["try"], a.get("ok"), a.get("at")) for a in json.loads(text)["attempts"]]
        except (ValueError, KeyError, TypeError):
            return BROKEN

    def _remote_copies(self):
        """원격에 있는 내 풀이의 [(커밋, 시도 기록)]. 아직 머지되지 않은 내 브랜치가 있으면 그것이 main 보다 새 판이라 main 은 보지 않음."""
        refs = [self._tip] if self._tip else []
        if not self._tip or self._is_ancestor(self._tip, self._base):
            refs.append(self._base)
        return [(ref, attempts) for ref in refs for attempts in [self._attempts(ref)] if isinstance(attempts, list)]

    def _reconcile(self):
        """가장 새 판의 내 풀이가 작업 폴더에 오게 함. 시도 기록은 덧붙기만 하므로 앞부분이 같으면 긴 쪽을 새 판으로 봄.
        작업 폴더가 비었거나 옛 판이면 새 판을 가져오고, 서로 다르게 이어졌으면 덮어쓰지 않고 멈춤."""
        local = self._attempts()
        if local is BROKEN:
            raise Stop("blocked", M_BROKEN_PROFILE)
        copies = self._remote_copies()
        mine = "refs/heads/" + self.branch
        if self._branch() != self.branch and self._has(mine):  # 손으로 브랜치를 옮겨 폴더가 옛 판이 됐을 때만 씀
            attempts = self._attempts(mine)
            if isinstance(attempts, list) and (local is None or attempts[:len(local)] == local):
                copies.append((mine, attempts))
        if not copies:
            return
        ref, newest = max(copies, key=lambda copy: len(copy[1]))
        if local is not None and local[:len(newest)] == newest:
            return
        if local is not None and newest[:len(local)] != local:
            raise Stop("diverged", M_DIVERGED, "원격(%s)의 시도 기록 %d개, 이 컴퓨터 %d개" % (ref, len(newest), len(local)))
        self._take(ref)

    def _take(self, ref, exact=False):
        """내 폴더를 ref 에 있는 판으로 바꾸고 지금 것은 보관함에 복사해 둠.
        exact 면 ref 에 없는 파일(갈라진 뒤 이 컴퓨터에서만 만든 회차)도 지움. 남겨 두면 새 회차의 답으로 읽힘."""
        kept = self._keep_folder("replaced")
        self._git("checkout", "-q", ref, "--", self.rel)
        if exact:
            wanted = set(self._paths("ls-tree", "-r", "-z", "--name-only", ref, "--", self.rel))
            for rel in self._paths("ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", self.rel):
                path = os.path.join(self.root, rel)
                if rel not in wanted and os.path.isfile(path):
                    os.remove(path)
        self._changed = True
        self._notes.append(M_TOOK_OVER if kept else M_TOOK)

    def _drop_index(self):
        index = os.path.join(self._gitdir(), "study-index")
        for path in (index, index + ".lock"):
            if os.path.exists(path):
                os.remove(path)
        return index

    def _snapshot(self, message):
        """origin/main 의 트리에서 내 폴더만 작업 폴더 내용으로 바꾼 커밋을 만듦. 작업 폴더·인덱스·HEAD 는 건드리지 않음."""
        base, tip = self._base, self._tip
        env = {"GIT_INDEX_FILE": self._drop_index()}  # 임시 인덱스를 써서 진짜 인덱스가 잠겨 있어도 됨
        try:
            self._git("read-tree", base, env=env)
            if os.path.isdir(self.folder):
                self._git("add", "-A", "--", self.rel, env=env)  # 삭제까지 포함해 내 폴더를 통째로 담음. .gitignore 는 적용됨
            tree = self._out("write-tree", env=env)
        finally:
            self._drop_index()
        for old in (tip, self._commit_of("HEAD")):  # 바뀐 것이 없으면 새 커밋을 만들지 않음
            if old and self._out("rev-parse", old + "^{tree}") == tree and self._is_ancestor(base, old) \
                    and (not tip or self._is_ancestor(tip, old)):
                return old
        if not tip or self._is_ancestor(tip, base):
            parents = [base]  # 브랜치가 없거나 이미 main 에 들어감 → main 위에 커밋 하나
        elif self._is_ancestor(base, tip):
            parents = [tip]  # PR 이 열려 있고 main 은 안 움직임 → 브랜치에 커밋 하나 추가
        else:
            parents = [tip, base]  # PR 이 열린 동안 main 이 움직임(또는 squash 머지 뒤 브랜치가 남음) → 둘을 이음
        return self._out("commit-tree", tree, *[arg for parent in parents for arg in ("-p", parent)],
                         "-m", message, env=self._identity())

    def _identity(self):
        """git 에 이름·메일을 설정한 적 없는 컴퓨터에서도 커밋이 만들어지게 함. 사용자 설정은 바꾸지 않음."""
        if self._out("config", "user.name", check=False) and self._out("config", "user.email", check=False):
            return {}
        who = {"NAME": self.user, "EMAIL": "%s@users.noreply.github.com" % self.user}
        return {"GIT_%s_%s" % (role, key): value for role in ("AUTHOR", "COMMITTER") for key, value in who.items()}

    def _park_outside(self, target):
        """내 폴더 밖에서 고치거나 지운 파일, target 이 새로 만들 경로를 차지한 미추적 파일을 보관함에 복사하고 원래대로 돌림.
        손으로 커밋해 버린 밖 변경은 브랜치를 옮기면 작업 폴더에서 사라지므로 사본만 남김. 사본을 남긴 경로를 돌려줌."""
        changed = set(self._paths("diff", "--name-only", "-z", "HEAD", "--", *self.outside))
        changed |= set(self._paths("diff", "--name-only", "-z", "--cached", "HEAD", "--", *self.outside))
        committed = set(self._paths("diff", "--name-only", "-z", MAIN + "...HEAD", "--", *self.outside))
        self._copy_out(changed | committed)
        if changed:
            self._git("checkout", "-q", "HEAD", "--", *self.outside)  # 사본을 만든 뒤 추적 파일을 원본으로
            self._git("reset", "-q", "--", *self.outside)  # 손으로 add 해 둔 새 파일은 add 만 취소하고 파일은 남김
        untracked = set(self._paths("ls-files", "-z", "--others", "--exclude-standard", "--", *self.outside))
        incoming = set(self._paths("diff", "--name-only", "-z", "--diff-filter=A", "HEAD", target, "--", *self.outside))
        collide = untracked & incoming
        self._copy_out(collide)
        for rel in collide:
            os.remove(os.path.join(self.root, rel))
        parked = changed | committed | collide
        if parked:
            self._notes.append(M_PARKED % len(parked))
        return parked

    def _copy_out(self, paths):
        for rel in sorted(paths):
            source = os.path.join(self.root, rel)
            if os.path.isfile(source):
                target = os.path.join(self._backup_dir(), "outside", rel)
                os.makedirs(os.path.dirname(target), exist_ok=True)
                shutil.copy2(source, target)

    def _broken_files(self):
        """올리면 안 되는 깨진 파일: JSON 이 아닌 profile.json, 읽히지 않는 회차 답안지(quiz.py)."""
        broken = []
        if self._attempts() is BROKEN:
            broken.append("profile.json 을 읽을 수 없습니다.")
        for name in sorted(os.listdir(self.folder)) if os.path.isdir(self.folder) else []:
            path = os.path.join(self.folder, name, "quiz.py")
            if not os.path.isfile(path):
                continue
            try:
                problem = study.parse_quiz_answers(path)[1]
            except (OSError, ValueError) as error:  # 인코딩이 깨진 파일 등
                problem = "quiz.py 를 읽을 수 없습니다: %s" % error
            if problem:
                broken.append("%s/%s" % (name, problem))
        return broken

    def _push(self, commit):
        """강제 옵션 없이 올림. ('ok' | 'behind' | 'slow' | 'login' | 'denied' | 'offline' | None, git 출력) 을 돌려줌."""
        run = self._git("push", "--porcelain", "origin", "%s:refs/heads/%s" % (commit, self.branch),
                        check=False, timeout=self.timeout * PUSH_PATIENCE)
        text = "git %s\n%s" % (run.args, (run.out + run.err).strip())
        if run.code == 0:
            return "ok", text
        if run.code is None:
            return "slow", text
        if any(line.startswith("!") and "[rejected]" in line for line in run.out.splitlines()):
            return "behind", text  # non-fast-forward · fetch first: 원격의 내 브랜치에 모르는 커밋이 있음
        return remote_problem(run.err), text

    def _pulls(self):
        """원격의 {PR 번호: 그 PR 의 끝 커밋}(refs/pull/N/head). GitHub 는 열린 PR 의 것만 push 때마다 옮기고,
        닫힌 PR 의 것은 닫힐 때의 커밋에 남겨 둠. 조회하지 못하면 {}."""
        run = self._git("ls-remote", "origin", "refs/pull/*/head", check=False, timeout=self.fetch_timeout)
        found = {}
        for line in (run.out if run.code == 0 else "").splitlines():
            sha, _, ref = line.partition("\t")
            if ref.startswith("refs/pull/"):
                found[ref.split("/")[2]] = sha
        return found

    def _pr(self, commit, pushed, before):
        """(PR 주소, 'open' 이미 열려 있었음 | 'created' 방금 자동으로 만들어짐 | 'manual' 직접 만들어야 할 수 있음).
        origin 이 GitHub 주소가 아니면 (None, 'manual'). before 는 올리기 직전의 _pulls()."""
        slug = remote_slug(self._url)
        if not slug:
            return None, "manual"
        url = self.find_pr(slug[0], slug[1], self.branch)
        if url:
            return url, "open"
        waited = 0
        while pushed and waited < self.pr_wait:  # 저장소의 Actions 가 study/* 브랜치에 PR 을 만들어 줌
            self.sleep(PR_POLL)
            waited += PR_POLL
            for number, sha in self._pulls().items():
                if sha == commit and before.get(number) != commit:  # 전부터 이 커밋을 가리키던 것은 닫힌 PR 임
                    return "https://github.com/%s/%s/pull/%s" % (slug[0], slug[1], number), "open" if number in before else "created"
        return new_pr_url(slug[0], slug[1], self.branch, "%s 풀이" % self.user), "manual"

    # 작업

    def _sync(self):
        dev = self._dev_branch()
        if dev:
            raise Stop("blocked", M_DEV % dev)
        self._preflight()
        self._fetch()
        self._reconcile()
        snap = self._snapshot("최신 문제 받기")
        before = self._out("rev-parse", "HEAD^{commit}")
        moved = self._park_outside(snap)
        if before != snap or self._branch() != self.branch:
            if os.path.isdir(self.folder) or self._paths("ls-files", "-z", "--", self.rel):
                self._git("add", "-A", "--", self.rel)  # 인덱스의 내 폴더 = 작업 폴더 = 스냅샷
            self._git("checkout", "-q", "-B", self.branch, snap)  # 덮어쓸 수정이 있으면 git 이 거부함
        moved |= set(self._paths("diff", "--name-only", "-z", before, snap, "--", *self.outside))
        restart = any(is_tool(path) for path in moved)
        changed = restart or any(path.startswith("problems/") for path in moved)
        stale = self._paths("diff", "--name-only", "-z", "HEAD", "--", *self.outside)
        if stale:  # checkout 은 파일을 못 바꿔도 0 으로 끝나서 직접 확인함. 나머지 파일은 이미 바뀌었으니 restart·changed 도 같이 알림
            return self._result("blocked", M_LOCKED % (len(stale), ", ".join(stale[:3])), "\n".join(stale), restart=restart, changed=changed)
        return self._result("ok", M_RESTART if restart else M_NEW if changed else M_LATEST, restart=restart, changed=changed)

    def _submit(self, force=False):
        if not self._dev_branch():  # 개발 중인 폴더의 멈춘 작업은 건드리지 않음
            self._preflight()
        broken = self._broken_files()
        if broken:
            more = " 외 %d개." % (len(broken) - 1) if len(broken) > 1 else ""
            raise Stop("blocked", M_BROKEN % (broken[0] + more), "\n".join(broken))
        self._fetch()
        for attempt in (1, 2):
            if not force:
                self._reconcile()
            snap = self._snapshot("풀이 제출: %s" % self.user)
            mine = self._folder_tree(snap)
            if mine == self._folder_tree(self._base):
                return self._result("nothing", M_NOTHING if mine else M_EMPTY)
            pushed = snap != self._tip
            before = self._pulls() if pushed else {}
            kind, text = self._push(snap) if pushed else ("ok", "")
            if kind == "ok":
                url, state = self._pr(snap, pushed, before)
                if state == "open":
                    message = M_ADDED if pushed else M_SAME
                elif state == "created":
                    message = M_CREATED
                else:
                    message = (M_OPEN_PR if pushed else M_NO_OPEN_PR) if url else M_PUSHED % self.branch
                return self._result("ok", message, text, pr_url=url)
            if kind == "behind" and attempt == 1:
                self._fetch()  # 받아 온 직후 원격이 또 바뀐 경우: 한 번만 다시
                continue
            self._remote_stop(kind, text, "올리지")

    def _take_remote(self):
        if not self._dev_branch():
            self._preflight()
        self._fetch()
        copies = self._remote_copies()
        if not copies:
            return self._result("nothing", M_NO_REMOTE_COPY)
        self._take(max(copies, key=lambda copy: len(copy[1]))[0], exact=True)
        return self._result("ok", "")
