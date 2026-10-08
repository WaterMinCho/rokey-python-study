# -*- coding: utf-8 -*-
"""실행기 테스트. 실제로 설치하거나 창을 띄우지 않고 결정 로직만 확인함.

프로세스 실행, 가상 환경 생성, 입력 같은 바깥 동작은 FakeHost 가 대신하면서 부른 순서를 기록함.
실행: python -m unittest discover -s tests
"""
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import bootstrap  # noqa: E402
import study  # noqa: E402

GOOD = {"version": (3, 14), "bits64": True, "platform": "win-amd64", "prefix": "/usr"}
PIP_NO_WHEEL = ("ERROR: Could not find a version that satisfies the requirement PyQt6 (from versions: none)\n"
                "ERROR: No matching distribution found for PyQt6\n")
PIP_OFFLINE = ("WARNING: Retrying (Retry(total=0, connect=None, read=None, redirect=None, status=None)) after "
               "connection broken by 'NameResolutionError(\"HTTPSConnection(host='pypi.org', port=443): "
               "Failed to resolve 'pypi.org'\")': /simple/pyqt6/\n") + PIP_NO_WHEEL


class FakeHost:
    """bootstrap.Host 대역. calls 에 바깥 동작을 부른 순서대로 남김."""

    def __init__(self, pyqt=False, info=None, healthy=False, venv_module=True, tty=True, answer="y",
                 create_error=None, pip=(0, ""), exit_code=0, gui=None):
        self.pyqt, self.info, self.healthy, self.venv_module, self.tty = pyqt, dict(info or GOOD), healthy, venv_module, tty
        self.answer, self.create_error, self.pip, self.exit_code, self.gui = answer, create_error, pip, exit_code, gui
        self.calls, self.said = [], []

    def python_info(self):
        return self.info

    def pyqt_error(self):
        return None if self.pyqt else "ModuleNotFoundError: No module named 'PyQt6'"

    def gui_main(self):
        self.calls.append(("gui",))
        if isinstance(self.gui, Exception):
            raise self.gui
        return lambda: self.gui

    def can_venv(self):
        return self.venv_module

    def isatty(self):
        return self.tty

    def say(self, text):
        self.said.append(text)

    def ask(self, prompt):
        self.calls.append(("ask",))
        self.said.append(prompt)
        return self.answer

    def probe(self, python):
        self.calls.append(("probe", python))
        return self.healthy

    def create_venv(self, path):
        self.calls.append(("create", path))
        if self.create_error:
            raise self.create_error

    def pip_install(self, python):
        self.calls.append(("pip", python))
        return self.pip

    def remove(self, path):
        self.calls.append(("remove", path))

    def call(self, command):
        self.calls.append(("call", list(command)))
        return self.exit_code

    def names(self):
        return [c[0] for c in self.calls]

    def text(self):
        return "\n".join(self.said)


class LaunchCase(unittest.TestCase):
    """실제 홈 폴더의 전용 환경을 건드리지 않게 STUDY_VENV 를 임시 폴더 아래로 돌림."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="boot_test_")
        self.venv = os.path.join(os.path.realpath(self.tmp), "venv")
        self.python = bootstrap.venv_python(self.venv)
        patcher = mock.patch.dict(os.environ, {"STUDY_VENV": self.venv})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def make_venv(self):
        os.makedirs(self.venv)
        open(os.path.join(self.venv, "pyvenv.cfg"), "w").close()

    def assert_guidance(self, host, code):
        """실패 안내 확인. 0 이 아닌 코드로 끝나고, 다시 시도 방법과 go 를 알리고, 재실행하지 않음."""
        self.assertNotEqual(code, 0)
        self.assertIn("다시 시도", host.text())
        self.assertIn("python study.py go", host.text())
        self.assertNotIn("call", host.names())
        self.assertNotIn("!", host.text())


class PythonCheckTest(unittest.TestCase):
    def problem(self, version, bits64=True, platform="win-amd64"):
        return bootstrap.python_problem({"version": version, "bits64": bits64, "platform": platform, "prefix": ""})

    def test_supported_range(self):
        for version in ((3, 10), (3, 11), (3, 12), (3, 13), (3, 14)):
            self.assertIsNone(self.problem(version), version)
        self.assertIsNone(self.problem((3, 12), platform="macosx-11.0-arm64"))

    def test_too_old_and_too_new(self):
        self.assertIn("3.10 이상", self.problem((3, 9)))
        message = self.problem((3, 15))
        self.assertIn("3.15", message)
        self.assertIn("아직", message)  # 3.15 용 휠이 아직 없다고 알려야 함

    def test_32bit(self):
        self.assertIn("32비트", self.problem((3, 12), bits64=False, platform="win32"))

    def test_windows_arm64_needs_311(self):
        self.assertIn("3.11 이상", self.problem((3, 10), platform="win-arm64"))
        self.assertIsNone(self.problem((3, 11), platform="win-arm64"))


class PathTest(unittest.TestCase):
    def test_default_venv_is_outside_repo(self):
        with mock.patch.dict(os.environ):
            os.environ.pop("STUDY_VENV", None)
            path = bootstrap.venv_dir()
        self.assertEqual(path, os.path.join(os.path.expanduser("~"), ".rokey-study", "venv"))
        self.assertFalse(path.startswith(os.path.join(ROOT, "")))

    def test_env_overrides_venv(self):
        with mock.patch.dict(os.environ, {"STUDY_VENV": os.path.join("~", "elsewhere")}):
            self.assertEqual(bootstrap.venv_dir(), os.path.join(os.path.expanduser("~"), "elsewhere"))

    def test_venv_python_is_inside_venv(self):
        python = bootstrap.venv_python("/x/venv")
        self.assertTrue(python.startswith(os.path.join("/x/venv", "")))
        self.assertIn("python", os.path.basename(python))
        with mock.patch.object(os, "name", "nt"):
            self.assertEqual(bootstrap.venv_python("venv"), os.path.join("venv", "Scripts", "python.exe"))


class LaunchTest(LaunchCase):
    # 바로 실행, 재실행

    def test_pyqt_present_runs_gui_directly(self):
        host = FakeHost(pyqt=True, gui=0)
        self.assertEqual(bootstrap.launch([], host), 0)
        self.assertEqual(host.names(), ["gui"])  # 점검·설치·재실행 없음
        self.assertEqual(host.said, [bootstrap.OPENING])

    def test_gui_exit_code_is_returned(self):
        self.assertEqual(bootstrap.launch([], FakeHost(pyqt=True, gui=3)), 3)
        self.assertEqual(bootstrap.launch([], FakeHost(pyqt=True, gui=None)), 0)

    def test_pyqt_present_wins_over_unsupported_python(self):
        host = FakeHost(pyqt=True, gui=0, info=dict(GOOD, version=(3, 15)))
        self.assertEqual(bootstrap.launch([], host), 0)

    def test_missing_gui_module_is_reported(self):
        host = FakeHost(pyqt=True, gui=ModuleNotFoundError("No module named 'gui'"))
        code = bootstrap.launch([], host)
        self.assert_guidance(host, code)
        self.assertIn("gui/app.py", host.text())

    def test_healthy_venv_reruns_study_with_its_python(self):
        self.make_venv()
        host = FakeHost(healthy=True, exit_code=7)
        self.assertEqual(bootstrap.launch([], host), 7)  # 자식의 종료 코드를 그대로 돌려줌
        self.assertEqual(host.calls, [("probe", self.python), ("call", [self.python, bootstrap.STUDY])])
        self.assertEqual(host.said, [bootstrap.OPENING])  # 묻지 않음

    def test_rerun_keeps_arguments(self):
        self.make_venv()
        host = FakeHost(healthy=True)
        bootstrap.launch(["gui"], host)
        self.assertEqual(host.calls[-1], ("call", [self.python, bootstrap.STUDY, "gui"]))

    def test_healthy_venv_wins_over_unsupported_python(self):
        """3.14 로 만든 전용 환경이 있으면 나중에 3.15 로 실행해도 화면이 열림."""
        self.make_venv()
        host = FakeHost(healthy=True, info=dict(GOOD, version=(3, 15)))
        self.assertEqual(bootstrap.launch([], host), 0)
        self.assertEqual(host.names(), ["probe", "call"])

    def test_rerun_side_opens_quietly(self):
        """전용 환경의 파이썬으로 다시 실행된 쪽은 안내를 되풀이하지 않고 화면만 띄움."""
        host = FakeHost(pyqt=True, gui=0, info=dict(GOOD, prefix=self.venv))
        self.assertEqual(bootstrap.launch([], host), 0)
        self.assertEqual((host.names(), host.said), (["gui"], []))

    def test_no_rerun_loop_inside_venv(self):
        """전용 환경의 파이썬으로 돌고 있는데도 PyQt6 가 없으면 다시 실행하지 않음."""
        self.make_venv()
        host = FakeHost(healthy=True, info=dict(GOOD, prefix=self.venv))
        code = bootstrap.launch([], host)
        self.assert_guidance(host, code)
        self.assertEqual(host.calls, [])

    # 새로 설치

    def test_consent_creates_installs_then_reruns(self):
        host = FakeHost(answer="y", exit_code=0)
        self.assertEqual(bootstrap.launch([], host), 0)
        self.assertEqual(host.calls, [("ask",), ("create", self.venv), ("pip", self.python),
                                      ("call", [self.python, bootstrap.STUDY])])

    def test_consent_text_says_what_where_and_how_big(self):
        host = FakeHost(answer="n")
        bootstrap.launch([], host)
        text = host.text()
        for part in ("PyQt6", "85MB", "250MB", self.venv, "시스템 파이썬", "저장소"):
            self.assertIn(part, text)

    def test_only_explicit_yes_installs(self):
        def created(answer):
            host = FakeHost(answer=answer)
            bootstrap.launch([], host)
            return "create" in host.names()
        for answer in ("y", "Y", " yes ", "ㅛ", "네"):
            self.assertTrue(created(answer), answer)
        for answer in ("", "n", "no", "아니오", "q"):
            self.assertFalse(created(answer), answer)

    def test_decline_installs_nothing(self):
        host = FakeHost(answer="n")
        code = bootstrap.launch([], host)
        self.assert_guidance(host, code)
        self.assertEqual(host.names(), ["ask"])

    def test_pip_command_installs_wheels_only(self):
        self.assertEqual(bootstrap.PIP_INSTALL[:3], ["-m", "pip", "install"])
        self.assertIn("--only-binary=:all:", bootstrap.PIP_INSTALL)
        self.assertEqual(bootstrap.PIP_INSTALL[-1], "PyQt6")

    def test_not_a_terminal_never_installs(self):
        host = FakeHost(tty=False)
        code = bootstrap.launch([], host)
        self.assert_guidance(host, code)
        self.assertEqual(host.calls, [])  # 묻지도 만들지도 않음
        self.assertIn("터미널", host.text())

    def test_unsupported_python_never_installs(self):
        for info in (dict(GOOD, version=(3, 15)), dict(GOOD, version=(3, 9)),
                     dict(GOOD, bits64=False, platform="win32"), dict(GOOD, version=(3, 10), platform="win-arm64")):
            host = FakeHost(info=info)
            code = bootstrap.launch([], host)
            self.assert_guidance(host, code)
            self.assertEqual(host.calls, [], info)
            self.assertIn("파이썬 3.14(64비트)를 설치", host.text())
            self.assertIn("python.org", host.text())

    def test_unsupported_python_retry_command_per_os(self):
        for name, command in (("nt", "py -3.14 study.py"), ("posix", "python3.14 study.py")):
            host = FakeHost(info=dict(GOOD, version=(3, 15)))
            with mock.patch.object(os, "name", name):
                bootstrap.launch([], host)
            self.assertIn(command, host.text())

    def test_no_venv_module(self):
        host = FakeHost(venv_module=False)
        code = bootstrap.launch([], host)
        self.assert_guidance(host, code)
        self.assertEqual(host.calls, [])
        self.assertIn("python3-venv", host.text())

    def test_venv_creation_failure(self):
        error = subprocess.CalledProcessError(1, ["python", "-m", "ensurepip"])
        host = FakeHost(create_error=error)
        code = bootstrap.launch([], host)
        self.assert_guidance(host, code)
        self.assertEqual(host.names(), ["ask", "create"])
        self.assertIn("전용 환경을 준비하지 못했습니다", host.text())

    def test_pip_failure_offline(self):
        host = FakeHost(pip=(1, PIP_OFFLINE))
        code = bootstrap.launch([], host)
        self.assert_guidance(host, code)
        self.assertEqual(host.names(), ["ask", "create", "pip"])
        self.assertIn("인터넷", host.text())

    def test_pip_failure_no_wheel(self):
        host = FakeHost(pip=(1, PIP_NO_WHEEL))
        code = bootstrap.launch([], host)
        self.assert_guidance(host, code)
        self.assertIn("맞는 PyQt6 설치 파일이 없습니다", host.text())
        self.assertNotIn("인터넷", host.text())

    def test_pip_failure_other(self):
        host = FakeHost(pip=(1, "ERROR: Could not install packages due to an OSError: [Errno 28] No space left on device\n"))
        self.assert_guidance(host, bootstrap.launch([], host))
        self.assertIn("pip 메시지", host.text())

    # 깨진 전용 환경

    def test_broken_venv_is_replaced_after_consent(self):
        self.make_venv()
        host = FakeHost(healthy=False, answer="y")
        self.assertEqual(bootstrap.launch([], host), 0)
        self.assertEqual(host.names(), ["probe", "ask", "remove", "create", "pip", "call"])
        self.assertEqual(host.calls[2], ("remove", self.venv))
        self.assertIn("온전하지 않습니다", host.text())

    def test_broken_venv_is_kept_when_declined(self):
        self.make_venv()
        host = FakeHost(healthy=False, answer="n")
        code = bootstrap.launch([], host)
        self.assert_guidance(host, code)
        self.assertEqual(host.names(), ["probe", "ask"])

    def test_broken_venv_without_terminal(self):
        self.make_venv()
        host = FakeHost(healthy=False, tty=False)
        code = bootstrap.launch([], host)
        self.assert_guidance(host, code)
        self.assertEqual(host.names(), ["probe"])

    def test_folder_that_is_not_a_venv_is_never_removed(self):
        os.makedirs(self.venv)
        open(os.path.join(self.venv, "내 파일.txt"), "w").close()
        host = FakeHost(answer="y")
        code = bootstrap.launch([], host)
        self.assert_guidance(host, code)
        self.assertEqual(host.calls, [])
        self.assertIn("STUDY_VENV", host.text())

    def test_empty_folder_counts_as_missing(self):
        os.makedirs(self.venv)
        host = FakeHost(answer="y")
        self.assertEqual(bootstrap.launch([], host), 0)
        self.assertEqual(host.names(), ["ask", "create", "pip", "call"])


class HostTest(unittest.TestCase):
    """진짜 Host 중 설치 없이 확인할 수 있는 부분."""

    def test_python_info(self):
        info = bootstrap.Host().python_info()
        self.assertEqual(info["version"], sys.version_info[:2])
        self.assertEqual(set(info), {"version", "bits64", "platform", "prefix"})

    def test_probe_of_missing_python_is_false(self):
        self.assertFalse(bootstrap.Host().probe(os.path.join(tempfile.gettempdir(), "no", "such", "python")))

    def test_probe_matches_this_python(self):
        host = bootstrap.Host()
        code = subprocess.run([sys.executable, "-c", "import PyQt6.QtWidgets"], stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL).returncode
        self.assertEqual(host.probe(sys.executable), code == 0)

    def test_gui_main_returns_entry_point(self):
        app = mock.Mock()
        with mock.patch.dict(sys.modules, {"gui": mock.Mock(app=app), "gui.app": app}):
            self.assertIs(bootstrap.Host().gui_main(), app.main)

    def test_missing_gui_package_is_import_error(self):
        with mock.patch.dict(sys.modules, {"gui": None}):
            with self.assertRaises(ImportError):
                bootstrap.Host().gui_main()

    def test_pip_install_returns_exit_code_and_error_text(self):
        """pip 대신 표준 오류에 한 줄 남기고 실패하는 명령을 돌림."""
        fake_pip = ["-c", "import sys; sys.stderr.write('ERROR: boom\\n'); sys.exit(3)"]
        shown = io.StringIO()
        with mock.patch.object(bootstrap, "PIP_INSTALL", fake_pip), contextlib.redirect_stderr(shown):
            code, log = bootstrap.Host().pip_install(sys.executable)
        self.assertEqual((code, log), (3, "ERROR: boom\n"))
        self.assertEqual(shown.getvalue(), log)  # 오류는 화면에도 똑같이 나옴

    def test_ask_treats_closed_input_and_ctrl_c_as_no_answer(self):
        for error in (EOFError, KeyboardInterrupt):
            with mock.patch("builtins.input", side_effect=error), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(bootstrap.Host().ask("? "), "")


class EntryTest(LaunchCase):
    """study.main 은 인수가 없거나 gui 면 화면을, go 면 터미널 모드를 실행함."""

    def run_main(self, argv, host=None, launch_code=0):
        go = mock.Mock()
        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch.object(study, "cmd_go", go))
            stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
            if host is None:
                launch = stack.enter_context(mock.patch.object(bootstrap, "launch", return_value=launch_code))
            else:
                launch = None
                stack.enter_context(mock.patch.object(bootstrap, "Host", lambda: host))
            try:
                study.main(argv)
                code = None
            except SystemExit as error:
                code = error.code
        return go, launch, code

    def test_no_argument_and_gui_launch_the_window(self):
        for argv in ([], ["gui"]):
            go, launch, code = self.run_main(argv, launch_code=5)
            launch.assert_called_once_with(argv)
            go.assert_not_called()
            self.assertEqual(code, 5)

    def test_go_is_terminal_mode(self):
        go, launch, code = self.run_main(["go"])
        go.assert_called_once()
        launch.assert_not_called()
        self.assertIsNone(code)

    def test_no_argument_never_grades(self):
        """화면을 띄우든 못 띄우든 인수 없는 실행은 cmd_go(채점)를 부르지 않음."""
        self.make_venv()
        hosts = [
            FakeHost(pyqt=True, gui=0),
            FakeHost(pyqt=True, gui=ModuleNotFoundError("No module named 'gui'")),
            FakeHost(healthy=True, exit_code=0),
            FakeHost(healthy=True, exit_code=134),  # 화면이 죽은 경우
            FakeHost(healthy=False, answer="n"),
            FakeHost(healthy=False, answer="y", pip=(1, PIP_OFFLINE)),
            FakeHost(healthy=False, answer="y", create_error=OSError("디스크가 가득 찼습니다")),
            FakeHost(healthy=False, tty=False),
            FakeHost(healthy=False, venv_module=False),
            FakeHost(healthy=False, info=dict(GOOD, version=(3, 15))),
            FakeHost(healthy=True, info=dict(GOOD, prefix=self.venv)),
        ]
        for index, host in enumerate(hosts):
            go, _, code = self.run_main([], host=host)
            go.assert_not_called()
            self.assertIsNotNone(code, index)

    def test_help_explains_both_modes(self):
        parser = study.build_parser()
        self.assertIn("화면", parser.description)
        self.assertIn("go", parser.description)
        text = parser.format_help()
        self.assertRegex(text, r"gui +\(기본\) 화면")
        self.assertRegex(text, r"go +터미널 모드")


LOADED_SCRIPT = r"""
import json, os, sys
root, tmp, runs = sys.argv[1], sys.argv[2], json.loads(sys.argv[3])
sys.path.insert(0, root)
import study
study.SUBMISSIONS_DIR = os.path.join(tmp, "submissions")
study.USER_FILE = os.path.join(tmp, ".study_user")
codes = []
for argv in runs:
    try:
        study.main(argv)
        codes.append(0)
    except SystemExit as error:
        codes.append(error.code or 0)
loaded = sorted(name for name in sys.modules if name.split(".")[0] in ("PyQt6", "gui", "bootstrap"))
sys.stderr.write("RESULT=" + json.dumps({"codes": codes, "loaded": loaded}))
"""


class NoGuiImportTest(unittest.TestCase):
    """CI 에는 PyQt6 가 없어서 터미널 명령과 채점 자식 프로세스는 PyQt6 를 import 하면 안 됨."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="boot_test_")
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def run_study(self, *runs):
        env = dict(os.environ, STUDY_USER="tester", PYTHONIOENCODING="utf-8")
        proc = subprocess.run([sys.executable, "-c", LOADED_SCRIPT, ROOT, self.tmp, json.dumps(list(runs))],
                              capture_output=True, env=env, cwd=self.tmp, stdin=subprocess.DEVNULL)
        err = proc.stderr.decode("utf-8", "replace")
        self.assertIn("RESULT=", err, err)
        result = json.loads(err.rsplit("RESULT=", 1)[1])
        self.assertEqual(result["loaded"], [])
        return result["codes"], proc.stdout.decode("utf-8", "replace")

    def test_go_and_grade(self):
        codes, out = self.run_study(["go"], ["grade", "d1"], ["me"])
        self.assertEqual(codes, [0, 0, 0])
        self.assertIn("진단", out)
        self.assertTrue(os.path.isfile(os.path.join(self.tmp, "submissions", "tester", "d1", "quiz.py")))

    def test_child_runner(self):
        source = os.path.join(self.tmp, "p01.py")
        job = {"source": source, "mode": "print", "cases": [], "workdir": self.tmp,
               "result": os.path.join(self.tmp, "result.json")}
        job_path = os.path.join(self.tmp, "job.json")
        with open(source, "w", encoding="utf-8") as f:
            f.write("print(1)\n")
        with open(job_path, "w", encoding="utf-8") as f:
            json.dump(job, f)
        codes, _ = self.run_study(["_run", job_path])
        self.assertEqual(codes, [0])
        self.assertTrue(os.path.isfile(job["result"]))

    def test_help(self):
        codes, out = self.run_study(["--help"])
        self.assertEqual(codes, [0])
        self.assertIn("터미널 모드", out)


if __name__ == "__main__":
    unittest.main()
