# 11차시 · GUI 프로그래밍(PyQt6 · tkinter)

창(window) 위에 버튼·레이블·입력창 같은 위젯을 올리고, 클릭 같은 이벤트에 함수를 연결하는 차시입니다.
강의 슬라이드는 PyQt6 로, 주간 요약본과 주간 과제는 tkinter 로 정리되어 있습니다. 시험 범위는 둘 다이므로 두 라이브러리의 대응 관계(9절)까지 봐 두세요.

채점 환경에는 GUI 라이브러리가 없어서, 이 세트의 코드 문제는 GUI 동작을 순수 파이썬으로 흉내 낸 것들입니다.
실제 시험에서는 클래스·메서드·시그널의 이름과 코드의 순서를 묻는 객관식·빈칸이 나오기 좋은 단원입니다.

## 1. PyQt6 는 외부 라이브러리

- 파이썬 표준 모듈이 아니므로 설치가 필요합니다. 터미널에서 `pip install PyQt6`
- pip 는 파이썬 패키지 관리자(Package Installer for Python)입니다. `pip install <패키지>` 설치 · `pip uninstall <패키지>` 제거 · `pip list` 설치 목록 확인
- 위젯 클래스들은 `PyQt6.QtWidgets` 안에, 이미지(`QPixmap`)·글꼴(`QFont`)·아이콘(`QIcon`)은 `PyQt6.QtGui` 안에 있습니다.

```python
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt6.QtGui import QPixmap
```

## 2. 기본 창 만들기

```python
import sys
from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget

app = QApplication(sys.argv)      # 애플리케이션 객체. 가장 먼저, 하나만
window = QWidget()                # 최상위 창
button = QPushButton("확인")      # 위젯 생성

layout = QVBoxLayout()            # 레이아웃 생성
layout.addWidget(button)          # 레이아웃에 위젯 추가
window.setLayout(layout)          # 창에 레이아웃 연결

window.show()                     # 창 표시
sys.exit(app.exec())              # 이벤트 루프 시작
```

- `QWidget` 이 "창", `QApplication` 이 "프로그램 전체"입니다. `QApplication(sys.argv)` 를 먼저 만들어야 위젯을 만들 수 있습니다.
- `window.show()` 를 빼면 오류는 없지만 창이 보이지 않습니다.
- `app.exec()` 가 이벤트 루프를 시작해, 창이 닫힐 때까지 마우스·키보드 입력에 응답합니다. 이 줄이 없으면 창이 떴다가 바로 꺼집니다. `sys.exit(...)` 로 감싸서 창이 닫히면 프로그램도 끝나게 합니다.
- 최상위 창으로 `QWidget` 대신 `QMainWindow` 를 써도 됩니다.

## 3. 창 크기·위치·제목

| 코드 | 뜻 |
|---|---|
| `window.setGeometry(100, 100, 400, 300)` | (x=100, y=100) 위치에 가로 400 × 세로 300. 정수 4개, 단위는 픽셀 |
| `window.resize(800, 600)` | 크기만: 가로 800, 세로 600 |
| `window.move(100, 200)` | 위치만: x=100, y=200 |
| `window.setWindowTitle("피자 주문")` | 제목 표시줄 글자 (슬라이드에는 없지만 과제에서 씀) |

`setGeometry(x, y, w, h)` 는 `move(x, y)` + `resize(w, h)` 와 같습니다. 위치 두 개가 먼저, 크기 두 개가 뒤입니다.

## 4. 위젯을 창에 붙이는 방법

- 생성자에 부모(parent)를 지정합니다: `btn = QPushButton("클릭", window)` 또는 `QPushButton("클릭", parent=window)`. 이어서 `btn.move(x, y)` 로 절대 좌표에 배치합니다.
- 레이아웃을 거쳐 자동으로 연결합니다: `layout.addWidget(btn)` → `window.setLayout(layout)`. 부모-자식 관계가 자동으로 만들어집니다.

## 5. 레이아웃 관리자(Layout manager)

| 종류 | 추가 메서드 | 배치 방식 |
|---|---|---|
| `QVBoxLayout()` | `addWidget(위젯)` | 세로(V = Vertical): 위 → 아래, 추가한 순서대로 |
| `QHBoxLayout()` | `addWidget(위젯)` | 가로(H = Horizontal): 왼쪽 → 오른쪽 |
| `QGridLayout()` | `addWidget(위젯, row, column)` | 격자. `addWidget(btn, 1, 0)` = 2번째 행, 1번째 열 (0부터 셈) |
| (레이아웃 없음) | `위젯.move(x, y)` | 절대 좌표(픽셀). 창 크기가 바뀌어도 따라 움직이지 않아 잘 쓰지 않음 |

- 레이아웃 안에 다른 레이아웃을 넣을 때는 `addWidget` 이 아니라 `layout.addLayout(서브_레이아웃)` 을 씁니다.
- 위젯이 놓이는 순서는 변수를 만든 순서가 아니라 `addWidget`·`addLayout` 을 호출한 순서입니다.
- 격자 좌표는 `(행, 열)` 순서이고 픽셀이 아닙니다. `move(x, y)` 가 픽셀입니다.
- 격자에서 `addWidget` 으로 채우지 않은 칸은 비어 있습니다. 같은 열 번호에 행 번호가 1 큰 위젯이 "바로 아래" 위젯입니다.
- 격자의 행 수는 가장 큰 행 번호 + 1, 열 수는 가장 큰 열 번호 + 1 입니다. 위젯 하나를 `(2, 1)` 에 놓으면 3행 2열 격자의 마지막 칸에 들어갑니다.

```python
row = QHBoxLayout()               # 가로 한 줄: 확인 | 취소
row.addWidget(btn_ok)
row.addWidget(btn_cancel)

layout = QVBoxLayout()            # 세로로 쌓기
layout.addWidget(label)           # 윗줄: 라벨
layout.addLayout(row)             # 아랫줄: 위에서 만든 가로 한 줄
window.setLayout(layout)
```

## 6. 시그널과 슬롯: 이벤트 연결

- 시그널(Signal): 클릭·입력 같은 이벤트가 생겼을 때 위젯이 보내는 신호 (`clicked`, `textChanged`, …)
- 슬롯(Slot): 그 신호가 왔을 때 실행될 함수(콜백 함수)
- 연결: `시그널.connect(슬롯_함수)`. 함수 이름을 괄호 없이 넘깁니다.

```python
def order():
    print("주문하세요")

btn = QPushButton("주문")
btn.clicked.connect(order)      # 클릭할 때마다 order 실행
# btn.clicked.connect(order())  # 오류: order() 가 지금 실행되고 반환값 None 이 연결됨
```

- 함수에 인수를 넘기고 싶으면 익명 함수로 감쌉니다: `btn.clicked.connect(lambda: greet("Python"))`. 강의 자료는 인수를 받지 않는 `lambda:` 형태로 쓰라고 안내합니다.
- `lambda:` 안쪽은 연결할 때가 아니라 클릭할 때 실행됩니다. `lambda: show(size, count)` 처럼 변수를 쓰면 클릭 시점의 값을 읽으므로, 연결 뒤에 변수가 바뀌면 바뀐 값이 쓰입니다. `lambda: label.setText(entry.text())` 가 클릭 순간의 입력창 글자를 읽는 것과 같은 원리입니다.
- 메서드도 그대로 연결할 수 있습니다. `entry.textChanged.connect(label.setText)` 로 연결하면 입력창 글자가 바뀔 때마다 바뀐 글자가 `label.setText(글자)` 로 전달되어 라벨이 즉시 갱신됩니다.
- `connect` 는 연결만 합니다. 실행은 이벤트가 생길 때마다 한 번씩이고, 프로그램 시작 시 바로 실행되지는 않습니다.
- 시그널은 `connect` 로 받은 함수를 목록에 넣어 두었다가, 이벤트가 생기면 그 함수들을 호출하는 객체로 보면 됩니다. p10 이 이 구조를 순수 파이썬 클래스로 흉내 냅니다. `QLineEdit` 의 `textChanged` 는 글자가 실제로 바뀌었을 때 발생하고, 슬롯이 실행되는 시점에 `entry.text()` 는 이미 새 글자입니다.

| 위젯 | 자주 쓰는 시그널 |
|---|---|
| `QPushButton` | `clicked` |
| `QLineEdit` | `textChanged` |
| `QRadioButton` | `toggled` |
| `QCheckBox` | `stateChanged` (또는 `checkStateChanged`) |
| `QComboBox` | `currentTextChanged` |

## 7. 위젯 모음

| 위젯 | 만들기 | 주요 메서드 |
|---|---|---|
| `QPushButton` 버튼 | `QPushButton("텍스트")` | `setText()` / `text()`, `setEnabled(True/False)`, `setFixedSize(w, h)`, `setIcon(QIcon("경로"))`, `setFont(QFont("글꼴", 크기))`, `setStyleSheet("...")` |
| `QLabel` 레이블 | `QLabel("텍스트")`, 비워 두려면 `QLabel()` | `setText()` / `text()`, `setPixmap(QPixmap("경로"))`(이미지), `setAlignment(Qt.AlignmentFlag.AlignCenter)`, `setWordWrap(True)` |
| `QLineEdit` 한 줄 입력창 | `QLineEdit()` | `text()`, 시그널 `textChanged` |
| `QRadioButton` 라디오 버튼 | `QRadioButton("텍스트")` | `setChecked(True)`, `isChecked()` |
| `QCheckBox` 체크박스 | `QCheckBox("텍스트")` | `setChecked(True/False)`, `isChecked()` |
| `QComboBox` 드롭다운 | `QComboBox()` | `addItems(리스트)`, `addItem("하나")`, `currentText()`, `currentIndex()` |

- `setText(문자열)` 은 바꾸는 메서드, `text()` 는 현재 글자를 문자열로 돌려주는 메서드입니다. 버튼을 눌렀을 때 입력창 글자를 라벨에 옮기려면 `label.setText(entry.text())` 입니다. `entry.text` 처럼 괄호를 빼면 글자가 아니라 메서드 자체가 넘어가 오류가 납니다. `text()` 는 숫자처럼 보여도 항상 문자열이라 계산하려면 `int()` 가 필요합니다.
- 스타일은 CSS 처럼 문자열로 지정합니다: `label.setStyleSheet("background-color: red; color: white;")`. `background-color` 가 배경색, `color` 가 글자색입니다.
- `setEnabled(False)` 는 버튼을 비활성화하고 `setEnabled(True)` 는 다시 활성화합니다. `setFixedSize(w, h)` 와 `resize(w, h)` 는 폭, 높이 순서로 받습니다.
- 이미지 전용 위젯은 없습니다. `QPixmap("img.png")` 을 만들어 `QLabel` 에 `setPixmap()` 으로 올립니다. `QPixmap` 은 `PyQt6.QtGui` 에서 가져옵니다.

## 8. 라디오 버튼과 체크박스의 판별 코드

| | `QRadioButton` | `QCheckBox` |
|---|---|---|
| 선택 개수 | 범주 중 하나만 | 여러 개 |
| 묶임 | 같은 부모(창)에 놓이면 자동으로 묶여(autoExclusive) 하나를 고르면 나머지가 풀림 | 서로 독립 |
| 판별 | `if … elif … elif` (하나만 걸림) | 체크박스마다 독립된 `if` |

```python
def order():                          # 라디오: if-elif
    if r_a.isChecked():
        print("A 런치")
    elif r_b.isChecked():
        print("B 런치")

def order_all():                      # 체크박스: 독립 if
    selected = []
    if chk1.isChecked():
        selected.append("아메리카노")
    if chk2.isChecked():
        selected.append("라떼")
    if selected:
        print(f"주문 항목: {', '.join(selected)}")
    else:
        print("선택된 메뉴가 없습니다.")
```

- `isChecked()` 는 메서드라 괄호가 필요하고 `True`/`False` 를 반환합니다.
- `setChecked(True)` 로 기본 선택을 만들 수 있습니다. 라디오에 기본 선택을 해 두면 아무것도 누르지 않고 주문 버튼을 눌러도 그 항목이 출력됩니다.
- `', '.join(리스트)` 는 13차시에서 자세히 배우지만 11차시 예제에 먼저 나옵니다. `["a", "b"]` → `"a, b"` 처럼 리스트의 문자열들을 구분자로 이어 붙인 한 문자열을 돌려줍니다.
- 출력 순서는 `if` 문이 적힌 순서입니다. 사용자가 체크한 순서와는 상관없습니다.

## 9. tkinter: 요약본·주간 과제 쪽

| | PyQt6 (강의 슬라이드) | tkinter (주간 요약본) |
|---|---|---|
| 설치 | 외부 라이브러리, `pip install PyQt6` | 표준 라이브러리, 설치 없이 `import tkinter` |
| 최상위 창 | `QWidget()` (`QApplication` 이 먼저 필요) | `Tk()`. 가장 상위층(Toplevel) 위젯을 만든다 |
| 위젯 만들기 | `QPushButton("텍스트")` | `tkinter.Button(부모, text="텍스트", command=함수명)`. 첫 인수가 부모 인스턴스, 나머지는 `옵션=값` |
| 배치 | `layout.addWidget()` / `위젯.move()` | `위젯.pack()`, `위젯.grid()`, `위젯.place()` |
| 클릭 연결 | `btn.clicked.connect(함수명)` | 만들 때 `command=함수명` (역시 괄호 없이) |
| 창 제목·크기 | `setWindowTitle()`, `resize()` | `root.title("제목")`, `root.geometry("300x200")` |
| 이벤트 루프 | `sys.exit(app.exec())` | `root.mainloop()` |

```python
import tkinter as tk
from tkinter import messagebox

def on_order():
    messagebox.showinfo("주문", "주문이 접수되었습니다")

root = tk.Tk()                    # 최상위 창
root.title("주문 창")             # 제목
root.geometry("300x200")          # 크기는 "가로x세로" 문자열
btn = tk.Button(root, text="주문", command=on_order)
btn.pack(pady=20)                 # 배치
root.mainloop()                   # 이벤트 루프 시작
```

- `messagebox.showinfo(제목, 내용)` 은 알림 창을 띄웁니다. `messagebox` 는 `from tkinter import messagebox` 로 따로 가져옵니다.
- `root.mainloop()` 가 tkinter 의 이벤트 루프를 시작합니다. PyQt6 의 `app.exec()` 에 해당하고, 이 줄이 없으면 창이 유지되지 않습니다.
- tkinter 의 `Radiobutton` 은 `master, text, variable, value` 를 받고, 선택하면 `variable` 에 그 `value` 가 저장됩니다. 같은 `variable` 을 넘긴 버튼들 가운데 하나만 선택됩니다. 클래스 이름은 b 가 소문자인 `Radiobutton` 이고, PyQt6 쪽은 B 가 대문자인 `QRadioButton` 입니다.

## 시험에서 헷갈리기 쉬운 포인트

- `connect(함수)` vs `connect(함수())`: 괄호를 붙이면 그 자리에서 함수가 실행되어 버립니다. 슬롯은 이름만 넘깁니다. tkinter 의 `command=함수명` 도 같습니다.
- `show()` 는 창을 보이게 하고 `exec()` 는 이벤트 루프를 시작합니다. 둘 다 있어야 창이 떠 있습니다. `exec()` 는 `app`(QApplication) 의 메서드, `show()` 는 `window` 의 메서드입니다.
- QVBoxLayout 은 세로, QHBoxLayout 은 가로입니다(V = Vertical, H = Horizontal).
- `QGridLayout.addWidget(위젯, 행, 열)` 은 0부터 세고 픽셀이 아닙니다. `move(x, y)` 가 픽셀입니다.
- `setGeometry(x, y, 가로, 세로)` 는 위치 둘이 먼저, 크기 둘이 뒤인 정수 4개입니다.
- `isChecked()` 는 괄호 있는 메서드, `clicked` 는 괄호 없는 시그널입니다. `btn.clicked().connect(...)` 는 틀립니다.
- 라디오는 `if-elif`, 체크박스는 독립 `if` 로 판별합니다. 체크박스를 `if-elif` 로 쓰면 첫 번째로 체크된 것만 처리됩니다.
- `currentText()` 는 문자열, `currentIndex()` 는 정수(0부터)를 돌려줍니다. `addItems()` 는 리스트, `addItem()` 은 하나를 받습니다.
- 이미지는 `QLabel` + `setPixmap(QPixmap("파일"))` 입니다. `setText` 에 이미지를 넣거나 이미지 전용 위젯을 찾지 마세요.
- PyQt6 는 설치가 필요하고 tkinter 는 표준 라이브러리입니다. "둘 다 pip 로 설치해야 한다" 는 틀린 설명입니다.
- `QApplication(sys.argv)` 가 먼저, 그다음 `QWidget()` 입니다. `import sys` 를 빼면 `sys.argv` 에서 NameError 가 납니다.
- 문장 순서: `QApplication` → `QWidget` → (크기·레이아웃 설정) → `show()` → `app.exec()`. `exec()` 는 이벤트 루프를 돌리느라 그 뒤의 문장으로 넘어가지 않으므로 `show()` 가 `exec()` 뒤에 있으면 창이 나타나지 않습니다.
- `currentTextChanged`(콤보박스)·`textChanged`(입력창)는 바뀐 문자열을 슬롯에 넘겨주므로 `connect(label.setText)` 처럼 문자열을 받는 메서드와 바로 연결할 수 있습니다. tkinter 는 시그널 대신 `command=함수명` 옵션입니다.
- 라디오 버튼은 같은 창에 두면 자동으로 묶이므로 별도 그룹 코드가 필요 없습니다. 체크박스는 같은 창에 두어도 서로 영향이 없습니다.
- 라디오·체크박스 모두 `setChecked(True)` 로 코드에서 선택 상태를 바꿀 수 있습니다.
- 레이아웃에 위젯을 넣을 때는 `addWidget`, 레이아웃을 넣을 때는 `addLayout` 입니다. 놓이는 순서는 이 메서드들을 호출한 순서입니다.
- `QPixmap` 은 `PyQt6.QtWidgets` 가 아니라 `PyQt6.QtGui` 에서 가져옵니다. `QtWidgets` 에는 `QApplication` 과 위젯 클래스(`QLabel`, `QPushButton` 등), 레이아웃 클래스가 있습니다.
- tkinter 의 이벤트 루프는 `root.mainloop()`, PyQt6 는 `app.exec()` 입니다. tkinter 의 라디오 버튼 클래스는 `Radiobutton`(b 소문자)입니다.
- 체크된 것이 없는지를 총가격이 `0` 인지로 판단하면, 가격이 `0` 인 메뉴만 체크했을 때 틀립니다. 체크된 개수나 이름 리스트로 판단합니다.
