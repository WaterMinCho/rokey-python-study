# -*- coding: utf-8 -*-
"""오래 걸리는 일(채점·코드 실행·git)을 화면 밖 스레드에서 돌린다. 한 번에 하나만 쓴다."""
import traceback

from PyQt6.QtCore import QThread, pyqtSignal

from session import SessionError


class Job(QThread):
    done = pyqtSignal(object)
    failed = pyqtSignal(str, str)  # (사용자에게 그대로 보여 줄 문구, 트레이스백) — 둘 중 하나만 채운다

    def __init__(self, fn):
        super().__init__()
        self.fn = fn

    def run(self):
        try:
            result = self.fn()
        except SessionError as error:
            self.failed.emit(str(error), "")
        except BaseException:  # SystemExit 포함 — 코어의 die()(sys.exit)가 스레드에서 새면 창이 죽는다
            self.failed.emit("", traceback.format_exc())
        else:
            self.done.emit(result)
