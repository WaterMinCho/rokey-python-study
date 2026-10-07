# -*- coding: utf-8 -*-
"""화면 진입점. `python study.py` 가 bootstrap 을 거쳐 main() 을 부름."""
import os
import subprocess
import sys

from PyQt6.QtCore import QLockFile, QSettings
from PyQt6.QtWidgets import QApplication

import study
from gui import errors, theme
from gui.dialogs import MessageDialog
from gui.window import MainWindow


def main(argv=None):
    app = QApplication(sys.argv[:1] + list(sys.argv[1:] if argv is None else argv))
    app.setApplicationName("ROKEY 파이썬 스터디")
    theme.apply(app)
    errors.install(os.path.join(study.ROOT, ".study_logs"))

    lock = QLockFile(os.path.join(study.ROOT, ".study.lock"))  # 창 두 개가 같은 풀이 기록을 덮어쓰지 않게 하나만 띄움
    lock.setStaleLockTime(0)  # 오래 켜 둬도 잠금이 풀리지 않게 함. 죽은 프로세스의 잠금은 Qt 가 치움
    if not lock.tryLock(0):
        text = "이미 실행 중입니다. 열려 있는 창을 사용해 주세요."
        if sys.stderr:  # pythonw 로 띄우면 stderr 가 없음
            print(text, file=sys.stderr)
        MessageDialog(None, "ROKEY 파이썬 스터디", text).exec()
        return 1

    window = MainWindow(QSettings("rokey-python-study", "study"))
    window.show()
    window.boot()
    code = app.exec()
    lock.unlock()
    if window.restart:  # 도구 파일이 새 버전으로 바뀌었으면 처음 실행한 명령으로 다시 띄움
        subprocess.Popen([sys.executable] + sys.orig_argv[1:])
    return code


if __name__ == "__main__":
    sys.exit(main())
