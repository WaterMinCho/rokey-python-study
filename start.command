#!/bin/sh
# macOS: 더블클릭하면 터미널이 열리고 스터디 화면(창)이 뜹니다.
cd "$(dirname "$0")" || exit 1
python3 study.py
