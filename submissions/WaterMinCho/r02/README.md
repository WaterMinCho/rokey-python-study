# 2회차 미니 모의고사

> 프로그램(`python study.py`)에서 풀면 이 폴더의 `quiz.py` 와 `.py` 파일에 답이 자동으로 저장됩니다.

문항 18개(보강할 단원 13개) · 평균 레벨 1.8 · 단원: s11 3, s14 3, s04 2, s05 2, s08 2, s16 2, s01 1, s06 1, s10 1, s15 1

## s04_Q3 (리스트와 딕셔너리 · 객관식 · 2점)

`a = [1, 2]` 를 실행한 다음 아래 코드 중 하나를 실행하고 `print(a)` 를 했습니다.
출력이 `[1, 2, 3, 4]` 가 되는 것은?

1. `a.append([3, 4])`
2. `a.extend([3, 4])`
3. `a.insert(2, [3, 4])`
4. `a.append(3, 4)`

## s04_Q8 (리스트와 딕셔너리 · 출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
box = [7, "seven", 7.5]
print(box)
print(box[1])
print(box[0] + box[2])
```

## s05_Q12 (반복문 · 출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
n = 0
while True:
    n += 3
    if n > 10:
        break
    print(n)
print("끝", n)
```

## s06_Q8 (함수(1) · 객관식 · 2점)

`return` 에 대한 설명으로 옳은 것을 **모두** 고르세요.

1. `return` 문이 실행되면 함수가 그 자리에서 끝나고, 아래에 남은 함수 코드는 실행되지 않는다.
2. `return` 문이 없는 함수를 호출해 그 결과를 변수에 담으면 `None` 이 저장된다.
3. 함수 안에는 `return` 문이 반드시 하나 있어야 한다.
4. `return 값` 은 그 값을 화면에 출력한 뒤 함수를 끝낸다.

## s08_Q15 (자료구조와 알고리즘 · 출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
def fch(x):
    x["kim"] = 95
    x["park"] = 70

score = {"kim": 80, "lee": 90}
backup = score
fch(backup)
print(score)
print(len(score))
```

## s11_Q22 (GUI 프로그래밍(PyQt6 · tkinter) · 객관식 · 2점)

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

## s11_Q28 (GUI 프로그래밍(PyQt6 · tkinter) · 단답 · 3점)

`QComboBox` 의 선택 항목이 바뀔 때마다 바뀐 항목의 문자열이 라벨에 표시되게 하려 합니다. `combo.____.connect(label.setText)` 의 빈칸에 들어갈 시그널의 이름을 적으세요.

## s14_Q2 (정규표현식 · 객관식 · 2점)

정규식 `go{2,3}d` 를 `re.match` 로 조사했을 때 매치되는 문자열을 **모두 고르세요**.

1. `god`
2. `good`
3. `goood`
4. `gooood`

## s14_Q9 (정규표현식 · 출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
import re
p = re.compile("[a-z]+")
m = p.match("42 apples")
print(m)
s = p.search("42 apples")
print(s.group())
print(s.start(), s.end())
print(s.span())
```

## s16_Q7 (알고리즘(1) · 출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
queue = []
queue.append("A")
queue.append("B")
first = queue.pop(0)
queue.append("C")
queue.append("D")
print(first)
print(queue)
print(queue.pop(0))
print(queue)
```

## s16_Q8 (알고리즘(1) · 객관식 · 2점)

다음 코드를 실행한 결과로 옳은 것은?

```python
queue = [1]
queue.pop(0)
print(queue.pop(0))
```

1. `None` 이 출력된다.
2. `1` 이 출력된다.
3. `[]` 이 출력된다.
4. 오류가 발생한다.

## s01_p05 (파이썬 소개 및 환경설정 · 빈칸 채우기 · 이름과 글자 구분하기 · 6점)

파일: `s01_p05.py`

아래 **출력 예**의 두 줄이 그대로 출력되도록 빈칸(`____`)을 채워 프로그램을 완성하세요.

- **빈칸만** 채웁니다. 다른 부분을 고치거나 줄을 추가하면 오답 처리됩니다.
- 첫째 줄에는 `print` 라는 글자 다섯 개가 그대로 출력되어야 합니다.

## 시작 코드

```python
print(____)
____("Hello")
```

## 출력 예

```
print
Hello
```

## s05_p09 (반복문 · 출력 · 구구단 출력 · 6점)

파일: `s05_p09.py`

두 정수 `first`, `last` 를 입력받아 `first` 단부터 `last` 단까지 구구단을 출력하는 프로그램을 작성하세요.

- 한 줄의 형식은 `단 x 곱하는수 = 결과` 입니다. 예) `2 x 3 = 6`
  (`x` 는 영문 소문자 엑스이고, 숫자와 기호 사이에는 공백이 한 칸씩 있습니다)
- 각 단은 1 부터 9 까지 곱합니다.
- 한 단이 끝날 때마다 빈 줄을 하나 출력합니다. (맨 마지막의 빈 줄은 있어도 없어도 정답입니다)
- 입력을 받는 두 줄은 시작 코드에 주어져 있습니다. 그 아래에 코드를 작성하세요.

## 제한 사항
- 1 ≤ first ≤ last ≤ 9

## 입출력 예

입력

```
2
3
```

출력

```
2 x 1 = 2
2 x 2 = 4
2 x 3 = 6
2 x 4 = 8
2 x 5 = 10
2 x 6 = 12
2 x 7 = 14
2 x 8 = 16
2 x 9 = 18

3 x 1 = 3
3 x 2 = 6
3 x 3 = 9
3 x 4 = 12
3 x 5 = 15
3 x 6 = 18
3 x 7 = 21
3 x 8 = 24
3 x 9 = 27
```

## s08_p06 (자료구조와 알고리즘 · 반환값 · 가장 큰 값의 위치 · 6점)

파일: `s08_p06.py`

숫자 리스트 `numbers` 가 주어질 때, 가장 큰 값이 들어 있는 인덱스를 **반환(return)** 하는 `solution` 함수를 완성하세요.

- 함수 이름과 매개변수는 바꾸지 않습니다.
- 가장 큰 값이 여러 번 나오면 그중 가장 앞의 인덱스를 반환합니다.

## 제한 사항
- `numbers` 의 길이는 1 이상 100 이하
- 각 요소는 -1000 이상 1000 이하의 정수

## 입출력 예

| numbers | 반환값 | 설명 |
|---|---|---|
| `[12, 30, 25, 41, 8]` | `3` | 가장 큰 값 41 은 인덱스 3 에 있습니다. |
| `[1, 9, 4, 9]` | `1` | 9 가 두 번 나오므로 앞쪽 인덱스 1 을 반환합니다. |
| `[-8, -3, -5]` | `1` | 가장 큰 값은 -3 입니다. |

## s10_p04 (클래스(2) · 빈칸 채우기 · 노트북은 기기다 · 6점)

파일: `s10_p04.py`

제품 이름과 가격을 저장하는 `Device` 클래스와, 이를 **상속받아** 램 용량(`ram`)을 추가한 `Laptop` 클래스입니다.
빈칸(`____`) 3곳을 채워 클래스를 완성하세요.

- `Laptop` 의 `__init__` 은 **부모의 `__init__`** 을 호출해 `name`, `price` 를 저장하게 하고, 이어서 `ram` 을 인스턴스 변수에 저장합니다.
- **빈칸만** 채웁니다. 다른 줄을 고치거나 줄을 추가하면 오답 처리됩니다.

```python
class Device:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def info(self):
        print("제품:", self.name)
        print("가격:", self.price)


class Laptop(____):
    def __init__(self, name, price, ram):
        ____.__init__(name, price)
        self.ram = ____
```

## 테스트 코드와 출력 예

```python
l = Laptop("그램", 1500000, 16)
l.info()
print(l.ram)
```

```
제품: 그램
가격: 1500000
16
```

```python
l = Laptop("맥북", 2000000, 8)
print(l.name, l.price, l.ram)
```

```
맥북 2000000 8
```

## s11_p08 (GUI 프로그래밍(PyQt6 · tkinter) · 반환값 · 수량 버튼 클릭 흉내 · 6점)

파일: `s11_p08.py`

수량을 표시하는 라벨 옆에 `+`, `-`, `초기화` 버튼이 있는 주문 창을 생각합니다. 각 버튼의 `clicked` 시그널에 연결된 슬롯은 아래 규칙대로 수량을 바꿉니다. 사용자가 클릭한 버튼 이름을 순서대로 담은 리스트 `clicks` 가 주어질 때, 모든 클릭이 끝난 뒤 라벨에 표시될 수량을 정수로 반환하는 `solution` 함수를 완성하세요.

- 창이 처음 열릴 때 수량은 `1` 입니다.
- `"+"`: 수량을 1 늘립니다. 단, 수량이 이미 `10` 이면 그대로 둡니다(최대 10).
- `"-"`: 수량을 1 줄입니다. 단, 수량이 이미 `1` 이면 그대로 둡니다(최소 1).
- `"초기화"`: 수량을 `1` 로 되돌립니다.
- `clicks` 가 빈 리스트이면 아무 버튼도 누르지 않은 것이므로 처음 수량을 반환합니다.
- 함수 이름과 매개변수는 바꾸지 않습니다. `print` 가 아니라 `return` 으로 돌려줍니다.

## 제한 사항
- `clicks` 의 길이는 0 이상 30 이하, 원소는 `"+"`, `"-"`, `"초기화"` 중 하나

## 입출력 예

| clicks | 반환값 |
|---|---|
| `["+", "+", "-"]` | `2` |
| `[]` | `1` |
| `["-", "-", "+"]` | `2` |
| `["+", "+", "+", "초기화", "+"]` | `2` |
| `["+"] * 12` (`+` 12번) | `10` |

## s14_p05 (정규표현식 · 빈칸 채우기 · 숫자 위치 나열 · 6점)

파일: `s14_p05.py`

한 줄을 입력받아, 그 안의 숫자 덩어리마다 `매치된 문자열` 과 `(시작, 끝)` 튜플을 한 줄씩 출력하는
프로그램입니다. 빈칸(`____`) 3곳을 채워 프로그램을 완성하세요.

```python
import re

text = input()
p = re.compile(r"\d+")
for m in p.____(text):            # 매치되는 부분을 match 객체로 하나씩 꺼내기
    print(m.____(), m.____())     # 매치된 문자열, (시작, 끝) 튜플
```

- 첫 번째 빈칸은 패턴 객체의 메서드, 나머지 두 빈칸은 match 객체의 메서드 이름입니다.
- 숫자가 하나도 없으면 아무것도 출력하지 않습니다.
- **빈칸만** 채웁니다. 다른 줄을 고치거나 줄을 추가하면 오답 처리됩니다.

## 입출력 예

입력
```
a1bb22ccc333
```
출력
```
1 (1, 2)
22 (4, 6)
333 (9, 12)
```

입력
```
2024-10-16
```
출력
```
2024 (0, 4)
10 (5, 7)
16 (8, 10)
```

## s15_p10 (고급 함수 · 빈칸 채우기 · 거꾸로 꺼내는 이터레이터 클래스 · 6점)

파일: `s15_p10.py`

전달받은 데이터(리스트나 문자열)의 원소를 **맨 뒤에서부터** 하나씩 돌려주는 이터레이터 클래스 `Rewinder` 입니다.
빈칸(`____`) 2곳을 채워 클래스를 완성하세요.

```python
class Rewinder:
    def __init__(self, data):
        self.data = data
        self.pos = ____

    def __iter__(self):
        return self

    def __next__(self):
        if ____:
            raise StopIteration
        item = self.data[self.pos]
        self.pos = self.pos - 1
        return item
```

- 첫 번째 빈칸에는 처음 꺼낼 원소(마지막 원소)의 인덱스를 구하는 식이 들어갑니다.
- 두 번째 빈칸에는 맨 앞 원소까지 돌려준 뒤에 참이 되는 조건이 들어갑니다. 맨 앞 원소(인덱스 0)는 빠지지 않고 나와야 합니다.
- `data` 가 비어 있으면 아무 값도 돌려주지 않습니다.
- **빈칸만** 채웁니다. 다른 줄을 고치거나 줄을 추가하면 오답 처리됩니다.

## 테스트 코드와 출력 예

```python
for x in Rewinder([1, 2, 3]):
    print(x)
```

```
3
2
1
```

```python
print(list(Rewinder("abc")))
print(list(Rewinder([])))
```

```
['c', 'b', 'a']
[]
```

```python
r = Rewinder([7])
print(next(r))
try:
    next(r)
except StopIteration:
    print("stop")
```

```
7
stop
```

