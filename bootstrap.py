#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""실행기 — `python study.py` 로 화면(창)을 띄우기까지의 준비.

1) 지금 파이썬에 PyQt6 가 있으면 그대로 화면을 연다(수업에서 이미 설치한 경우).
2) 없으면 전용 가상 환경(~/.rokey-study/venv, 환경 변수 STUDY_VENV 로 변경)이 온전한지 보고,
   온전하면 그 파이썬으로 study.py 를 다시 실행한다.
3) 전용 환경이 없거나 깨졌으면 터미널에서 동의를 받아 만들고 PyQt6 를 설치한 뒤 다시 실행한다.
   설치할 수 없는 파이썬(3.10~3.14·64비트가 아님)이면 설치를 시도하지 않고 안내만 한다.

어느 단계에서 막히든 원인과 선택지만 알리고 0 이 아닌 코드로 끝낸다. 터미널 모드(go)로 넘어가지 않는다 —
go 는 실행하자마자 채점하므로, 화면에서 풀다 만 답이 첫 시도로 기록돼 버린다.

표준 라이브러리만 쓴다. PyQt6 는 Host.pyqt_error 와 Host.gui_main 안에서만 import 한다.
"""
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import sysconfig

ROOT = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.join(ROOT, "study.py")
MIN_VERSION, MAX_VERSION = (3, 10), (3, 14)  # PyQt6 설치 파일(휠)이 있는 파이썬 범위. 3.15 용은 아직 없다(2026-10)
PROBE_TIMEOUT = 60  # 전용 환경 점검 제한 시간(초). 설치 직후 첫 import 는 백신 검사로 느릴 수 있어 넉넉히 둔다
# 휠만 받는다 — 소스 빌드로 빠지면 한참 뒤에 알아보기 어려운 오류로 끝난다
PIP_INSTALL = ["-m", "pip", "install", "--disable-pip-version-check", "--only-binary=:all:", "PyQt6"]
PYTHON_URL = "https://www.python.org/downloads/latest/python3.14/"  # python.org 첫 화면의 단추는 최신판(곧 3.15)을 준다
RETRY = "python study.py"
OPENING = "화면을 엽니다. 쓰는 동안 이 터미널 창은 닫지 말아 주세요(닫으면 화면도 함께 닫힙니다)."
YES = ("y", "yes", "ㅛ", "예", "네")  # ㅛ: 한글 입력 상태에서 y 를 누른 경우


class Host:
    """실행기가 바깥에 하는 일 전부(입력·출력·프로세스·설치). 테스트는 이것을 가짜로 바꾼다."""

    def python_info(self):
        return {"version": sys.version_info[:2], "bits64": sys.maxsize > 2 ** 32,
                "platform": sysconfig.get_platform(), "prefix": sys.prefix}

    def pyqt_error(self):
        """지금 파이썬에서 PyQt6 를 못 쓰는 이유. 쓸 수 있으면 None."""
        try:
            import PyQt6.QtWidgets  # noqa: F401
        except Exception as error:  # 없음(ImportError) 말고도 sip 버전이 안 맞으면 다른 예외가 난다
            return "%s: %s" % (type(error).__name__, error)
        return None

    def gui_main(self):
        import gui.app
        return gui.app.main

    def can_venv(self):
        """Ubuntu·Debian 은 venv·ensurepip 가 별도 패키지(python3-venv)라 없을 수 있다."""
        return all(importlib.util.find_spec(name) for name in ("venv", "ensurepip"))

    def isatty(self):
        return bool(sys.stdin) and sys.stdin.isatty()

    def say(self, text):
        print(text, flush=True)

    def ask(self, prompt):
        try:
            return input(prompt)
        except (EOFError, KeyboardInterrupt):  # 입력이 닫혔거나 Ctrl+C — 거절로 본다
            print()
            return ""

    def probe(self, python):
        """그 파이썬으로 PyQt6 를 불러올 수 있는지 별도 프로세스에서 확인한다."""
        try:
            return subprocess.run([python, "-c", "import PyQt6.QtWidgets"], timeout=PROBE_TIMEOUT,
                                  stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL).returncode == 0
        except (OSError, subprocess.TimeoutExpired):  # 기반 파이썬이 지워졌거나 응답이 없다
            return False

    def create_venv(self, path):
        import venv
        venv.EnvBuilder(with_pip=True, symlinks=os.name != "nt").create(path)  # `python -m venv` 의 기본값과 같게

    def pip_install(self, python):
        """PyQt6 를 설치한다. 진행 표시(표준 출력)는 그대로 보이고, 오류(표준 오류)는 보여 주면서 모아 둔다.
        (종료 코드, 오류 글) 반환."""
        lines = []
        with subprocess.Popen([python] + PIP_INSTALL, stderr=subprocess.PIPE, text=True, errors="replace") as proc:
            for line in proc.stderr:
                print(line, end="", file=sys.stderr, flush=True)
                lines.append(line)
        return proc.returncode, "".join(lines)

    def remove(self, path):
        shutil.rmtree(path)

    def call(self, command):
        """os.execv 를 쓰지 않는다 — Windows 에서는 부모가 먼저 끝나 콘솔과 종료 코드를 잃는다."""
        return subprocess.call(command)


def venv_dir():
    """전용 환경 위치. 저장소 밖이라 OneDrive 동기화·경로 길이·폴더 이동의 영향을 받지 않는다."""
    path = os.environ.get("STUDY_VENV") or os.path.join("~", ".rokey-study", "venv")
    return os.path.abspath(os.path.expanduser(path))


def venv_python(venv):
    return os.path.join(venv, "Scripts", "python.exe") if os.name == "nt" else os.path.join(venv, "bin", "python")


def venv_state(path):
    """none: 없음(빈 폴더 포함) / venv: 가상 환경 / other: 다른 것이 든 폴더 — 지우면 안 된다."""
    if os.path.isfile(os.path.join(path, "pyvenv.cfg")):
        return "venv"
    if not os.path.exists(path) or (os.path.isdir(path) and not os.listdir(path)):
        return "none"
    return "other"


def same_path(a, b):
    return os.path.normcase(os.path.realpath(a)) == os.path.normcase(os.path.realpath(b))


def python_problem(info):
    """이 파이썬에 PyQt6 를 설치할 수 없는 이유. 설치할 수 있으면 None."""
    version = info["version"]
    name = "%d.%d" % version
    if not info["bits64"]:
        return "지금 파이썬은 32비트인데, PyQt6 는 64비트 파이썬에만 설치됩니다."
    if version > MAX_VERSION:
        return "지금 파이썬은 %s 인데, PyQt6 가 아직 %s 용으로 나오지 않았습니다." % (name, name)
    oldest = (3, 11) if info["platform"] == "win-arm64" else MIN_VERSION
    if version < oldest:
        return "지금 파이썬은 %s 인데, PyQt6 는 파이썬 %d.%d 이상에만 설치됩니다." % (name, oldest[0], oldest[1])
    return None


def pip_failure(log):
    """pip 가 남긴 오류 글에서 사용자에게 알릴 원인을 고른다."""
    if re.search(r"connection|timed out|could not fetch", log, re.IGNORECASE):
        return "인터넷 연결 문제로 PyQt6 를 내려받지 못했습니다. 연결을 확인해 주세요."
    if "No matching distribution" in log:
        return "이 컴퓨터(운영체제·파이썬)에 맞는 PyQt6 설치 파일이 없습니다."
    return "PyQt6 설치 중 오류가 났습니다. 위의 pip 메시지를 확인해 주세요."


def fail(host, reason, retry=RETRY):
    """원인과 선택지만 알리고 끝낸다."""
    host.say(reason)
    host.say("  다시 시도     : %s" % retry)
    host.say("  터미널로 쓰기 : python study.py go")
    return 1


def consent(host, venv, broken):
    """무엇을 어디에 설치하는지 알리고 동의를 받는다."""
    if broken:
        host.say("전용 환경이 온전하지 않습니다(설치가 중간에 끊겼거나, 설치에 쓴 파이썬이 지워졌을 수 있습니다).")
        host.say("지우고 다시 설치합니다.")
    else:
        host.say("화면(창)을 띄우는 데 필요한 PyQt6 가 지금 파이썬에 없습니다.")
        host.say("이 프로그램만 쓰는 전용 환경을 만들어 그 안에 설치합니다.")
    host.say("  설치하는 것   : PyQt6 (창을 그리는 라이브러리)")
    host.say("  용량          : 내려받기 약 85MB, 설치 후 약 250MB")
    host.say("  설치 위치     : %s" % venv)
    host.say("  건드리지 않음 : 시스템 파이썬, 이 저장소 폴더")
    host.say("  지우는 방법   : 설치 위치의 폴더를 삭제")
    return host.ask("설치할까요? [y/N] ").strip().lower() in YES


def launch(argv=None, host=None):
    """화면을 띄운다. 종료 코드를 돌려준다(띄우지 못하면 0 이 아닌 값)."""
    argv = list(argv or [])
    host = host or Host()
    info = host.python_info()
    venv = venv_dir()
    rerun = same_path(info["prefix"], venv)  # 전용 환경의 파이썬으로 다시 실행된 쪽인가
    error = host.pyqt_error()
    if error is None:
        try:
            main = host.gui_main()
        except ImportError as import_error:
            return fail(host, "화면 모듈(gui/app.py)을 불러오지 못했습니다: %s" % import_error)
        if not rerun:  # 다시 실행된 쪽이면 부모가 이미 알렸다
            host.say(OPENING)
        return int(main() or 0)
    if rerun:  # 여기서 또 다시 실행하면 끝없이 돈다
        return fail(host, "전용 환경(%s)에서 PyQt6 를 불러오지 못했습니다. %s" % (venv, error))

    python = venv_python(venv)
    state = venv_state(venv)
    if state == "venv" and host.probe(python):
        host.say(OPENING)
        return host.call([python, STUDY] + argv)

    # 여기부터는 새로 설치해야 하는 경우
    problem = python_problem(info)
    if problem:
        command = "py -3.14 study.py" if os.name == "nt" else "python3.14 study.py"
        return fail(host, "%s 파이썬 3.14(64비트)를 설치해 주세요: %s" % (problem, PYTHON_URL),
                    retry="파이썬 3.14 설치 후 %s" % command)
    if state == "other":
        return fail(host, "%s 는 가상 환경 폴더가 아니어서 건드리지 않았습니다. 환경 변수 STUDY_VENV 를 확인해 주세요." % venv)
    if not host.can_venv():
        return fail(host, "이 파이썬에는 가상 환경 모듈(venv·ensurepip)이 없습니다. "
                          "Ubuntu·Debian 은 `sudo apt install python3-venv` 로 설치한 뒤 다시 실행해 주세요.")
    if not host.isatty():
        return fail(host, "화면에 필요한 PyQt6 를 설치해야 합니다. 설치 전에 동의를 받아야 하니 터미널에서 직접 실행해 주세요.")
    if not consent(host, venv, broken=state == "venv"):
        return fail(host, "PyQt6 를 설치하지 않아 화면을 열 수 없습니다.")

    try:
        if state == "venv":
            host.remove(venv)
        host.say("전용 환경을 만드는 중입니다.")
        host.create_venv(venv)
    except (OSError, subprocess.CalledProcessError) as os_error:
        return fail(host, "전용 환경을 준비하지 못했습니다(%s). %s" % (venv, os_error))
    host.say("PyQt6 를 내려받아 설치합니다.")
    code, log = host.pip_install(python)
    if code != 0:
        return fail(host, pip_failure(log))
    host.say("설치가 끝났습니다. " + OPENING)
    return host.call([python, STUDY] + argv)
