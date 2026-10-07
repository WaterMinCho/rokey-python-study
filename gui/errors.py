# -*- coding: utf-8 -*-
"""예상하지 못한 오류는 창을 죽이지 않고 기록한 뒤 대화상자로 알림."""
import datetime
import os
import sys
import traceback

from gui import dialogs

ISSUE_URL = "https://github.com/WaterMinCho/rokey-python-study/issues/new/choose"

state = {"log_dir": None, "dialog": None}


def install(log_dir):
    """PyQt6 는 슬롯에서 예외가 새면 프로세스를 끝내므로 전역 훅으로 받아 창을 살림."""
    state["log_dir"] = log_dir
    sys.excepthook = lambda kind, value, tb: report("".join(traceback.format_exception(kind, value, tb)))


def write_log(text):
    """기록 파일 경로를 돌려줌. 쓰지 못하면 None."""
    stamp = datetime.datetime.now()
    try:
        os.makedirs(state["log_dir"], exist_ok=True)
        path = os.path.join(state["log_dir"], "error-%s.log" % stamp.strftime("%Y%m%d"))
        with open(path, "a", encoding="utf-8") as f:
            f.write("[%s]\n%s\n" % (stamp.isoformat(timespec="seconds"), text))
        return path
    except (OSError, TypeError):
        return None


def report(text):
    path = write_log(text)
    if sys.stderr:  # pythonw 로 띄우면 stderr 가 없음
        print(text, file=sys.stderr)
    dialog = state["dialog"]
    if dialog is not None and dialog.isVisible():  # 오류가 연달아 나도 대화상자는 하나만
        dialog.append(text)
        return
    state["dialog"] = dialogs.ErrorDialog(text, path, ISSUE_URL)
    state["dialog"].show()
    state["dialog"].raise_()
