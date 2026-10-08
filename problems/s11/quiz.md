# 11차시 퀴즈: GUI 프로그래밍(PyQt6 · tkinter)

> 코드를 실행하지 말고 눈으로 풀어 보세요. 답은 `submissions/<내 ID>/s11/quiz.py` 에 적습니다.
> PyQt6 코드가 나오는 문항은 `import sys` 와 필요한 `from PyQt6.QtWidgets import ...` 가 이미 되어 있다고 가정합니다.

## Q1 (객관식 · 2점)

PyQt6 에 대한 설명으로 옳지 **않은** 것은?

1. 파이썬 표준 모듈이 아니어서 `pip install PyQt6` 로 설치해야 쓸 수 있다.
2. 설치되어 있는 패키지 목록은 `pip list` 로 확인한다.
3. `from PyQt6.QtWidgets import QWidget` 처럼 필요한 클래스만 골라 가져올 수 있다.
4. 파이썬에 기본으로 들어 있는 라이브러리라서 설치 없이 `import PyQt6` 만 쓰면 바로 사용할 수 있다.

## Q2 (객관식 · 2점)

다음 설명에 해당하는 PyQt6 클래스는?

> 프로그램에서 가장 먼저 하나 만들어야 하며, `sys.argv` 를 인수로 받는다. 이벤트 루프를 관리하고, `exec()` 를 호출하면 프로그램이 종료될 때까지 사용자 입력에 응답한다.

1. `QWidget`
2. `QApplication`
3. `QMainWindow`
4. `QVBoxLayout`

## Q3 (객관식 · 2점)

다음 프로그램은 오류 없이 실행되지만 창이 화면에 나타나지 않습니다. `sys.exit(...)` 바로 앞에 추가해야 할 문장은?

```python
app = QApplication(sys.argv)
window = QWidget()
window.resize(300, 200)
sys.exit(app.exec())
```

1. `app.show()`
2. `window.show()`
3. `window.exec()`
4. `QWidget.display(window)`

## Q4 (객관식 · 2점)

`window.setGeometry(50, 80, 640, 480)` 에 대한 설명으로 옳은 것은?

1. 너비 50, 높이 80 인 창을 화면의 (640, 480) 위치에 놓는다.
2. `window.move(50, 80)` 과 `window.resize(640, 480)` 을 모두 실행한 것과 같다.
3. 네 값의 단위는 화면 크기에 대한 퍼센트(%)이다.
4. 크기만 바꾸고 싶으면 `window.setGeometry(640, 480)` 처럼 인수 두 개만 넘겨도 된다.

## Q5 (객관식 · 2점)

버튼 `btn` 을 클릭할 때 아래 `order` 함수가 실행되도록 올바르게 연결한 문장은?

```python
def order():
    print("주문 접수")
```

1. `btn.clicked.connect(order())`
2. `btn.clicked.connect(order)`
3. `btn.connect(clicked, order)`
4. `btn.clicked(order)`

## Q6 (객관식 · 2점)

다음 프로그램을 실행한 뒤 사용자가 버튼을 두 번 클릭하고 창을 닫았습니다. 콘솔에 출력된 내용을 순서대로 적은 것은?

```python
def order():
    print("주문 접수")

app = QApplication(sys.argv)
window = QWidget()
btn = QPushButton("주문")
btn.clicked.connect(order)
print("준비 완료")

layout = QVBoxLayout()
layout.addWidget(btn)
window.setLayout(layout)
window.show()
sys.exit(app.exec())
```

1. `주문 접수` → `준비 완료` → `주문 접수`
2. `준비 완료` → `주문 접수` → `주문 접수`
3. `준비 완료` 한 줄만 출력된다
4. `주문 접수` → `준비 완료`

## Q7 (객관식 · 2점)

`layout` 이 `QGridLayout()` 일 때, `layout.addWidget(btn, 2, 0)` 의 뜻으로 옳은 것은?

1. 세 번째 행(row=2), 첫 번째 열(column=0) 칸에 `btn` 을 놓는다.
2. 창 안의 x=2, y=0 픽셀 위치에 `btn` 을 놓는다.
3. 첫 번째 행(row=0), 세 번째 열(column=2) 칸에 `btn` 을 놓는다.
4. `btn` 의 크기를 가로 2, 세로 0 으로 바꾼다.

## Q8 (객관식 · 2점)

다음 코드로 만든 창에서 버튼 세 개의 배치로 옳은 것은?

```python
btn_a = QPushButton("A")
btn_b = QPushButton("B")
btn_c = QPushButton("C")

layout = QHBoxLayout()
layout.addWidget(btn_a)
layout.addWidget(btn_b)
layout.addWidget(btn_c)
window.setLayout(layout)
```

1. 위에서 아래로 A, B, C 가 세로로 쌓인다.
2. 왼쪽에서 오른쪽으로 A, B, C 가 가로로 나란히 놓인다.
3. 나중에 추가한 C 가 A, B 를 덮어서 C 하나만 보인다.
4. 행과 열을 지정하지 않았으므로 오류가 발생한다.

## Q9 (객관식 · 2점)

`move()` 를 이용한 절대 좌표 배치에 대한 설명으로 옳지 **않은** 것은?

1. 레이아웃 관리자 없이 `btn.move(10, 60)` 처럼 x, y 픽셀 위치를 직접 지정한다.
2. `QPushButton("PUSH", window)` 처럼 위젯을 만들 때 부모 창을 넘겨 주어야 그 창 안에 나타난다.
3. 창 크기가 바뀌면 위젯의 위치도 자동으로 다시 계산된다.
4. 창 크기 변경에 반응하지 않아 레이아웃 관리자보다 사용률이 낮다.

## Q10 (객관식 · 2점)

`QRadioButton` 과 `QCheckBox` 에 대한 설명으로 옳지 **않은** 것은?

1. `QRadioButton` 은 같은 창(부모)에 놓이면 자동으로 묶여서 하나를 선택하면 나머지는 해제된다.
2. `QCheckBox` 는 같은 레이아웃에 있어도 서로 독립적이라 여러 개를 동시에 선택할 수 있다.
3. 두 위젯 모두 `isChecked()` 가 선택 여부를 `True`/`False` 로 반환한다.
4. `setChecked(True)` 는 `QCheckBox` 에만 있는 메서드라서 `QRadioButton` 에는 쓸 수 없다.

## Q11 (객관식 · 2점)

다음 프로그램을 실행한 뒤, 라디오 버튼을 하나도 건드리지 않고 `선택` 버튼만 한 번 클릭했습니다. 콘솔에 출력되는 것은?

```python
def choose():
    if r_small.isChecked():
        print("S 사이즈")
    elif r_medium.isChecked():
        print("M 사이즈")
    elif r_large.isChecked():
        print("L 사이즈")

app = QApplication(sys.argv)
window = QWidget()

r_small = QRadioButton("S")
r_medium = QRadioButton("M")
r_large = QRadioButton("L")
r_large.setChecked(True)

btn = QPushButton("선택")
btn.clicked.connect(choose)

layout = QVBoxLayout()
layout.addWidget(r_small)
layout.addWidget(r_medium)
layout.addWidget(r_large)
layout.addWidget(btn)
window.setLayout(layout)
window.show()
sys.exit(app.exec())
```

1. `S 사이즈`
2. `M 사이즈`
3. `L 사이즈`
4. 아무것도 출력되지 않는다

## Q12 (객관식 · 2점)

`QComboBox` 에 대한 설명으로 옳지 **않은** 것은?

1. `combo.addItems(["소", "중", "대"])` 로 여러 항목을 한 번에 추가한다.
2. 항목을 하나만 추가할 때는 `combo.addItem("특대")` 를 쓴다.
3. `combo.currentText()` 는 현재 선택된 항목의 문자열을 반환한다.
4. `combo.currentIndex()` 는 현재 선택된 항목의 문자열을 반환한다.

## Q13 (객관식 · 2점)

창 `window` 에 이미지 파일 `robot.png` 를 표시하는 코드로 옳은 것은? (`QPixmap` 은 import 되어 있습니다)

1. `label = QLabel(window)` 다음 `label.setPixmap(QPixmap("robot.png"))`
2. `label = QLabel(window)` 다음 `label.setText(QPixmap("robot.png"))`
3. `img = QImageLabel("robot.png")` 다음 `layout.addWidget(img)`
4. `pixmap = QPixmap("robot.png")` 다음 `layout.addWidget(pixmap)`

## Q14 (객관식 · 2점)

tkinter 와 PyQt6 를 비교한 설명으로 옳지 **않은** 것은?

1. tkinter 는 파이썬 표준 라이브러리라서 따로 설치하지 않고 `import tkinter` 로 쓴다.
2. PyQt6 의 `QWidget` 처럼, tkinter 에서는 `Tk` 클래스가 가장 상위층(Toplevel) 창을 만든다.
3. tkinter 위젯은 `pack()`, `grid()`, `place()` 메서드로 배치한다.
4. tkinter 버튼의 클릭 동작은 PyQt6 와 똑같이 `btn.clicked.connect(함수명)` 으로 연결한다.

## Q15 (객관식 · 2점)

창의 제목 표시줄 글자를 `주문` 으로 설정하는 코드를 **모두 고르세요**. (`window` 는 PyQt6 의 `QWidget` 객체, `root` 는 tkinter 의 `Tk` 객체입니다)

1. `window.setWindowTitle("주문")`
2. `root.title("주문")`
3. `window.setText("주문")`
4. `root.setTitle("주문")`

## Q16 (출력 예측 · 3점)

`connect(함수명)` 처럼 함수를 괄호 없이 넘기면 어떤 일이 생기는지 흉내 낸 코드입니다. 출력 결과를 그대로 적으세요. (여러 줄이면 `"""` 로 감싸서 줄을 나눠 적습니다)

```python
def hello():
    print("hello there")

def order():
    print("주문하세요")

slots = []
slots.append(hello)
slots.append(order)
slots.append(hello)
print(len(slots))
for slot in slots:
    slot()
```

## Q17 (출력 예측 · 3점)

GUI 없이 체크박스를 흉내 낸 코드입니다. 출력 결과를 그대로 적으세요.

```python
class CheckBox:
    def __init__(self, text, checked=False):
        self.text = text
        self.checked = checked

    def isChecked(self):
        return self.checked

    def setChecked(self, value):
        self.checked = value

def order():
    selected = []
    if chk1.isChecked():
        selected.append("치즈")
    if chk2.isChecked():
        selected.append("불고기")
    if chk3.isChecked():
        selected.append("페퍼로니")
    if selected:
        print("주문 항목: " + ", ".join(selected))
    else:
        print("선택된 메뉴가 없습니다.")

chk1 = CheckBox("치즈")
chk2 = CheckBox("불고기", True)
chk3 = CheckBox("페퍼로니")
order()
chk3.setChecked(True)
chk1.setChecked(True)
order()
chk1.setChecked(False)
chk2.setChecked(False)
chk3.setChecked(False)
order()
```

## Q18 (출력 예측 · 3점)

`entry.textChanged.connect(label.setText)` 처럼 메서드를 괄호 없이 넘기는 상황을 흉내 낸 코드입니다. 출력 결과를 그대로 적으세요.

```python
class Label:
    def __init__(self):
        self.content = ""

    def setText(self, s):
        self.content = s

    def text(self):
        return self.content

label = Label()
slot = label.setText
for typed in ["R", "RO", "ROK"]:
    slot(typed)
    print(label.text(), len(label.text()))
print(label.text())
```

## Q19 (단답 · 3점)

`QRadioButton` 과 `QCheckBox` 에서 현재 선택되어 있는지를 `True`/`False` 로 돌려주는 메서드의 이름을 적으세요. (괄호는 빼도 됩니다)

## Q20 (단답 · 3점)

`QLineEdit` 입력창의 글자가 바뀔 때마다 발생하는 시그널의 이름을 적으세요. (`entry.____.connect(label.setText)` 의 빈칸)

## Q21 (단답 · 3점)

`QApplication` 객체에서 이벤트 루프를 시작하는 메서드의 이름을 적으세요. (`sys.exit(app.____())` 의 빈칸, 괄호는 빼도 됩니다)

## Q22 (객관식 · 2점)

다음 코드로 만든 격자에서 `entry` 바로 아래 칸(같은 열의 다음 행)에 놓이는 위젯은?

```python
label = QLabel("수량")
entry = QLineEdit()
btn_ok = QPushButton("확인")
btn_cancel = QPushButton("취소")

layout = QGridLayout()
layout.addWidget(label, 0, 0)
layout.addWidget(entry, 0, 1)
layout.addWidget(btn_ok, 1, 1)
layout.addWidget(btn_cancel, 1, 2)
window.setLayout(layout)
```

1. `label`
2. `btn_ok`
3. `btn_cancel`
4. 아무것도 없다(그 칸은 비어 있다)

## Q23 (객관식 · 2점)

버튼 `btn` 을 클릭할 때마다 아래 `greet` 함수가 `"Python"` 을 인수로 받아 실행되도록 연결한 문장은?

```python
def greet(name):
    print("안녕하세요, " + name)
```

1. `btn.clicked.connect(greet("Python"))`
2. `btn.clicked.connect(greet, "Python")`
3. `btn.clicked.connect(lambda: greet("Python"))`
4. `btn.clicked.connect(lambda greet: "Python")`

## Q24 (객관식 · 2점)

`확인` 버튼을 누르면 입력창 `entry` 에 적혀 있는 글자가 라벨 `label` 에 표시되게 하려 합니다. 빈칸에 들어갈 것은?

```python
def show():
    label.setText(____)

entry = QLineEdit()
label = QLabel()
btn = QPushButton("확인")
btn.clicked.connect(show)
```

1. `entry.text`
2. `entry.text()`
3. `entry.textChanged`
4. `entry.setText()`

## Q25 (객관식 · 2점)

다음 프로그램을 실행한 뒤 사용자가 `불고기` 와 `페퍼로니` 를 체크하고 `주문` 버튼을 한 번 클릭했습니다. 콘솔에 출력되는 것은?

```python
def order():
    if chk_cheese.isChecked():
        print("치즈")
    elif chk_bulgogi.isChecked():
        print("불고기")
    elif chk_pepperoni.isChecked():
        print("페퍼로니")

app = QApplication(sys.argv)
window = QWidget()

chk_cheese = QCheckBox("치즈")
chk_bulgogi = QCheckBox("불고기")
chk_pepperoni = QCheckBox("페퍼로니")
btn = QPushButton("주문")
btn.clicked.connect(order)

layout = QVBoxLayout()
layout.addWidget(chk_cheese)
layout.addWidget(chk_bulgogi)
layout.addWidget(chk_pepperoni)
layout.addWidget(btn)
window.setLayout(layout)
window.show()
sys.exit(app.exec())
```

1. `불고기` 한 줄만 출력된다
2. `불고기` → `페퍼로니` 두 줄이 출력된다
3. `페퍼로니` 한 줄만 출력된다
4. `치즈` → `불고기` → `페퍼로니` 세 줄이 출력된다

## Q26 (객관식 · 2점)

다음 다섯 문장으로 창을 띄우려 합니다. 창이 정상적으로 나타나고, 사용자가 닫을 때까지 유지되는 순서는?

```
(ㄱ) window.show()
(ㄴ) app = QApplication(sys.argv)
(ㄷ) window = QWidget()
(ㄹ) sys.exit(app.exec())
(ㅁ) window.resize(300, 200)
```

1. ㄴ → ㄷ → ㅁ → ㄱ → ㄹ
2. ㄷ → ㄴ → ㅁ → ㄱ → ㄹ
3. ㄴ → ㄷ → ㅁ → ㄹ → ㄱ
4. ㄷ → ㅁ → ㄱ → ㄴ → ㄹ

## Q27 (출력 예측 · 3점)

`btn.clicked.connect(lambda: show(size, count))` 처럼 `lambda` 로 감싼 슬롯이 어느 시점의 값을 읽는지 흉내 낸 코드입니다. 출력 결과를 그대로 적으세요. (여러 줄이면 `"""` 로 감싸서 줄을 나눠 적습니다)

```python
class Button:
    def connect(self, func):
        self.slot = func

    def click(self):
        self.slot()

def show(size, count):
    print(size + " " + str(count) + "개")

size = "S"
count = 1
btn = Button()
btn.connect(lambda: show(size, count))
print("연결 완료")
btn.click()
size = "L"
count = count + 2
btn.click()
```

## Q28 (단답 · 3점)

`QComboBox` 의 선택 항목이 바뀔 때마다 바뀐 항목의 문자열이 라벨에 표시되게 하려 합니다. `combo.____.connect(label.setText)` 의 빈칸에 들어갈 시그널의 이름을 적으세요.

## Q29 (단답 · 3점)

tkinter 로 버튼을 만들 때, 클릭하면 실행할 함수를 지정하는 옵션(키워드 인수)의 이름을 적으세요. (`tk.Button(root, text="주문", ____=order)` 의 빈칸)

## Q30 (단답 · 3점)

tkinter 에서 여러 항목 가운데 하나만 고르게 할 때 쓰는 위젯의 클래스 이름을 적으세요. 같은 `variable` 을 넘겨 만든 것들 가운데 하나만 선택되고, 선택하면 그 위젯의 `value` 가 `variable` 에 저장됩니다. (`tk.____(root, text="포장", variable=choice, value=1)` 의 빈칸. 대소문자까지 정확히 적습니다)

## Q31 (객관식 · 2점)

`저장` 버튼을 누를 때마다 알림 창이 뜨는 tkinter 프로그램입니다. (가), (나), (다)에 들어갈 것을 순서대로 적은 것은?

```python
import tkinter as tk
from tkinter import messagebox

def notify():
    messagebox.(가)("안내", "저장했습니다")

root = tk.Tk()
root.title("메모장")
btn = tk.Button(root, text="저장", command=(나))
btn.pack()
root.(다)()
```

1. `showinfo` · `notify` · `mainloop`
2. `showinfo` · `notify()` · `mainloop`
3. `print` · `notify` · `exec`
4. `show` · `notify()` · `show`

## Q32 (객관식 · 2점)

다음 코드로 만든 창에서 위젯 세 개의 배치로 옳은 것은?

```python
label = QLabel("수량을 고르세요")
btn_ok = QPushButton("확인")
btn_cancel = QPushButton("취소")

row = QHBoxLayout()
row.addWidget(btn_cancel)
row.addWidget(btn_ok)

layout = QVBoxLayout()
layout.addLayout(row)
layout.addWidget(label)
window.setLayout(layout)
```

1. 윗줄에 왼쪽부터 `취소`, `확인` 이 나란히 놓이고, 그 아래에 라벨이 놓인다.
2. 맨 위에 라벨이 놓이고, 그 아래 줄에 왼쪽부터 `확인`, `취소` 가 나란히 놓인다.
3. 윗줄에 왼쪽부터 `확인`, `취소` 가 나란히 놓이고, 그 아래에 라벨이 놓인다.
4. `취소`, `확인`, 라벨이 위에서 아래로 한 줄에 하나씩 세로로 쌓인다.

## Q33 (객관식 · 2점)

버튼과 레이블을 설정하는 코드에 대한 설명으로 옳지 **않은** 것은?

1. `btn.setEnabled(False)` 는 버튼을 비활성화 상태로 만든다.
2. `label.setStyleSheet("background-color: blue; color: white;")` 는 레이블의 배경을 파란색, 글자를 흰색으로 지정한다.
3. `QPixmap` 은 위젯 클래스들과 같은 모듈에 있어서 `from PyQt6.QtWidgets import QPixmap` 으로 가져온다.
4. `btn.setFixedSize(120, 40)` 은 버튼의 폭을 120, 높이를 40 으로 지정한다.
