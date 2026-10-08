# -*- coding: utf-8 -*-
"""채점·코드 실행·git 처럼 오래 걸리는 일을 화면 밖 스레드에서 한 번에 하나씩 돌림."""
import traceback

from PyQt6.QtCore import QThread, pyqtSignal

from session import SessionError


class Job(QThread):
    done = pyqtSignal(object)
    failed = pyqtSignal(str, str)  # (사용자에게 그대로 보여 줄 문구, 트레이스백). 둘 중 하나만 채움

    def __init__(self, fn):
        super().__init__()
        self.fn = fn

    def run(self):
        try:
            result = self.fn()
        except SessionError as error:
            self.failed.emit(str(error), "")
        except BaseException:  # 코어의 die() 가 내는 SystemExit 도 잡음. 스레드에서 새면 창이 죽음
            self.failed.emit("", traceback.format_exc())
        else:
            self.done.emit(result)
