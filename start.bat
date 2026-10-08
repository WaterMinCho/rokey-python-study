@echo off
rem Windows: double-click to open the study window. study.py prints every other message.
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
    py -3 study.py
) else (
    python study.py
)
if %errorlevel%==9009 echo Python 을 찾지 못했습니다. https://www.python.org/downloads/latest/python3.14/ 에서 Python 3.14 를 설치한 뒤 다시 실행해 주세요.
if not %errorlevel%==0 pause
