# 1회차 미니 모의고사

> 프로그램(`python study.py`)에서 풀면 이 폴더의 `quiz.py` 와 `.py` 파일에 답이 자동으로 저장됩니다.

문항 18개(보강할 단원 16개) · 평균 레벨 1.4 · 단원: s11 4, s03 3, s02 2, s05 2, s13 2, s14 2, s06 1, s07 1, s10 1

## s02_Q15 (프로그래밍 기초 · 단답 · 3점)

값이나 변수의 자료형이 무엇인지 확인할 때 쓰는 파이썬 내장 함수의 이름을 적으세요.

## s03_Q2 (조건식과 제어문 · 출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
a = 30
b = 45
print(a == b)
print(a != b)
print(a >= 30)
print(b < 45)
print("Robot" == "robot")
```

## s03_Q7 (조건식과 제어문 · 객관식 · 2점)

제어문과 조건문에 대한 설명으로 **옳지 않은** 것은?

1. 프로그램은 기본적으로 위에서 아래로 차례대로 실행되고, 제어문은 이 흐름을 바꾼다.
2. 제어문에는 조건문과 반복문이 있다.
3. `else` 뒤에도 `elif` 처럼 조건식을 적어야 한다.
4. `elif` 와 `else` 는 `if` 없이 단독으로 쓸 수 없다.

## s03_Q8 (조건식과 제어문 · 객관식 · 2점)

`score = 85` 가 먼저 실행되었다고 할 때, 아래 (가)~(라) 중 **오류 없이** 실행되어 `통과` 를 출력하는 코드는?

(가)

```python
if score >= 80
    print("통과")
```

(나)

```python
if score = 85:
    print("통과")
```

(다)

```python
if score >= 80:
    print("통과")
```

(라)

```python
if score >= 80:
print("통과")
```

1. (가)
2. (나)
3. (다)
4. (라)

## s05_Q13 (반복문 · 출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.
(주간 요약본 예제처럼 f-string 을 썼습니다. `f"..."` 안의 `{i}` 자리에는 변수 `i` 의 값이 들어갑니다.)

```python
for i in range(2):
    for j in range(2):
        print(f"i={i}, j={j}")
```

## s05_Q16 (반복문 · 출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
for n in range(0, 31, 5):
    if n % 3 == 0:
        print(n, end=" ")
print("끝")
```

## s07_Q8 (함수(2) · 출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
def swap(pa, pb):
    temp = pa
    pa = pb
    pb = temp
    print("함수 안:", pa, pb)

na = 3
nb = 8
swap(na, nb)
print("함수 밖:", na, nb)
na, nb = nb, na
print("교환 후:", na, nb)
```

## s10_Q2 (클래스(2) · 객관식 · 2점)

다음과 같은 모듈 `tools.py` 가 있습니다.

```python
# tools.py
def plus(a, b):
    return a + b
```

다른 파일에서 아래와 같이 작성했을 때, **오류가 발생하는** 것은?

**1번**

```python
import tools
print(tools.plus(1, 2))
```

**2번**

```python
from tools import plus
print(plus(1, 2))
```

**3번**

```python
import tools as t
print(t.plus(1, 2))
```

**4번**

```python
import tools
print(plus(1, 2))
```

## s11_Q5 (GUI 프로그래밍(PyQt6 · tkinter) · 객관식 · 2점)

버튼 `btn` 을 클릭할 때 아래 `order` 함수가 실행되도록 올바르게 연결한 문장은?

```python
def order():
    print("주문 접수")
```

1. `btn.clicked.connect(order())`
2. `btn.clicked.connect(order)`
3. `btn.connect(clicked, order)`
4. `btn.clicked(order)`

## s13_Q19 (예외 처리·문자열·람다·map · 출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
codes = ["12", "ab", "0", "7"]
ok = 0
for c in codes:
    try:
        n = 100 // int(c)
    except (ValueError, ZeroDivisionError):
        print("건너뜀:", c)
        continue
    ok = ok + 1
    print(n)
print("성공", ok, "건")
```

## s14_Q2 (정규표현식 · 객관식 · 2점)

정규식 `go{2,3}d` 를 `re.match` 로 조사했을 때 매치되는 문자열을 **모두 고르세요**.

1. `god`
2. `good`
3. `goood`
4. `gooood`

## s02_p04 (프로그래밍 기초 · 빈칸 채우기 · 볼트 상자 포장 · 4점)

파일: `s02_p04.py`

볼트의 개수와 상자 하나에 담는 개수를 정수로 차례로 입력받아, 가득 찬 상자의 수와 상자에 담지 못하고 남는 볼트의 수를 출력하는 프로그램입니다. 빈칸(`____`)을 채워 프로그램을 완성하세요.

- **빈칸만** 채웁니다. 다른 줄을 고치거나 줄을 추가하면 오답 처리됩니다.
- 첫째 줄에 볼트의 개수, 둘째 줄에 상자 하나에 담는 개수가 입력됩니다(둘 다 1 이상의 정수).

## 시작 코드

```python
bolts = int(input())
size = int(input())
print("가득 찬 상자:", bolts ____ size)
print("남는 볼트:", bolts ____ size)
```

## 입출력 예

입력

```
47
6
```

출력

```
가득 찬 상자: 7
남는 볼트: 5
```

볼트 47개를 6개씩 담으면 상자 7개가 가득 차고 5개가 남습니다.

- 결과는 소수점 없는 정수로 출력해야 합니다(`7.0` 은 오답).

## s06_p03 (함수(1) · 반환값 · 두 수의 차 · 4점)

파일: `s06_p03.py`

정수 `a`, `b` 가 주어질 때, 큰 수에서 작은 수를 뺀 값을 반환(return)하는 `solution` 함수를 완성하세요.
두 수가 같으면 0 을 반환합니다.

- 함수 이름과 매개변수는 바꾸지 않습니다.
- `print` 로 출력하는 것이 아니라 `return` 으로 돌려줘야 합니다.

## 제한 사항
- -1000 ≤ a, b ≤ 1000

## 입출력 예

| a | b | 반환값 |
|---|---|---|
| 3 | 10 | 7 |
| 10 | 3 | 7 |
| 5 | 5 | 0 |
| -2 | 4 | 6 |

## s11_p01 (GUI 프로그래밍(PyQt6 · tkinter) · 빈칸 채우기 · 버튼 클릭 연결 흉내 · 4점)

파일: `s11_p01.py`

PyQt6 의 `btn.clicked.connect(order)` 가 하는 일을 GUI 없이 흉내 낸 프로그램입니다. 빈칸(`____`) 2곳을 채워 완성하세요.

- `Button` 클래스의 `connect(func)` 는 전달받은 함수를 `self.slot` 에 저장만 합니다.
- `click()` 은 저장해 둔 함수를 호출합니다. 버튼이 클릭된 상황에 해당합니다.
- 프로그램은 클릭 횟수를 한 줄 입력받아, 그 횟수만큼 `click()` 을 호출합니다. 클릭할 때마다 `order` 함수가 실행되어 `주문하세요` 가 한 줄씩 출력되어야 합니다.
- 빈칸만 채웁니다. 다른 줄을 고치거나 줄을 추가하면 오답 처리됩니다.

```python
def order():
    print("주문하세요")


class Button:
    def connect(self, func):
        self.slot = func

    def click(self):
        self.____()


btn = Button()
btn.connect(____)
clicks = int(input())
for i in range(clicks):
    btn.click()
```

## 입출력 예

| 입력 | 출력 |
|---|---|
| `3` | `주문하세요`<br>`주문하세요`<br>`주문하세요` |
| `1` | `주문하세요` |
| `0` | (아무것도 출력하지 않음) |

## s11_p02 (GUI 프로그래밍(PyQt6 · tkinter) · 빈칸 채우기 · 체크박스 흉내 · 4점)

파일: `s11_p02.py`

PyQt6 의 `QCheckBox` 가 하는 일을 GUI 없이 흉내 낸 `CheckBox` 클래스입니다. 빈칸(`____`) 3곳을 채워 완성하세요.

- 객체를 만들면 글자(`text`)를 저장하고, 선택되지 않은 상태로 시작합니다.
- `setChecked(value)` 는 선택 상태를 전달받은 값(`True`/`False`)으로 바꿉니다.
- `isChecked()` 는 현재 선택 상태를 `True` 또는 `False` 로 반환합니다.
- 빈칸만 채웁니다. 다른 줄을 고치거나 줄을 추가하면 오답 처리됩니다.

```python
class CheckBox:
    def __init__(self, text):
        self.text = text
        self.checked = ____

    def setChecked(self, value):
        self.checked = ____

    def isChecked(self):
        return ____
```

## 테스트 코드와 출력 예

```python
c = CheckBox("라떼")
print(c.isChecked())
c.setChecked(True)
print(c.isChecked())
print(c.text)
```

```
False
True
라떼
```

```python
a = CheckBox("A")
b = CheckBox("B")
a.setChecked(True)
print(a.isChecked(), b.isChecked())
```

```
True False
```

- 출력은 글자 하나까지 같아야 합니다. `False`/`True` 는 불(bool) 값이어야 하며 `0`/`1` 이 출력되면 오답입니다.

## s11_p03 (GUI 프로그래밍(PyQt6 · tkinter) · 반환값 · 콤보박스의 현재 항목 · 4점)

파일: `s11_p03.py`

`QComboBox` 의 `currentText()` 가 하는 일을 흉내 냅니다. 콤보박스의 항목 리스트 `items` 와 현재 선택된 인덱스 `index` 가 주어질 때, 현재 선택된 항목의 문자열을 반환하는 `solution` 함수를 완성하세요.

- `index` 가 `0` 이상이고 항목 개수보다 작으면 그 위치의 항목을 반환합니다.
- 그 밖의 경우(항목이 하나도 없거나, `index` 가 음수이거나, 항목 개수 이상이면) 선택된 항목이 없는 것이므로 빈 문자열 `""` 을 반환합니다.
- 함수 이름과 매개변수는 바꾸지 않습니다. `print` 가 아니라 `return` 으로 돌려줍니다.

## 제한 사항
- `items` 의 길이는 0 이상 10 이하, 원소는 문자열
- -5 ≤ index ≤ 15 인 정수

## 입출력 예

| items | index | 반환값 |
|---|---|---|
| `["소", "중", "대"]` | `1` | `"중"` |
| `["소", "중", "대"]` | `0` | `"소"` |
| `["소", "중", "대"]` | `3` | `""` |
| `[]` | `0` | `""` |
| `["Option 1"]` | `-1` | `""` |

## s13_p15 (예외 처리·문자열·람다·map · 빈칸 채우기 · 이름 목록 다듬기 · 6점)

파일: `s13_p15.py`

쉼표(`,`)로 구분된 이름들이 문자열 `text` 하나로 주어집니다. 이름 앞뒤에는 공백이 섞여 있을 수 있습니다. 각 이름의 **양 끝 공백**을 지운 뒤 이름 사이에 `/` 를 넣어 이어 붙인 문자열을 반환하는 `solution` 함수입니다. 빈칸(`____`) 3곳을 채워 완성하세요.

```python
def solution(text):
    names = text.split(____)
    clean = list(map(lambda s: ____, names))
    return ____.join(clean)
```

- 첫 번째 빈칸: 이름을 나누는 구분자
- 두 번째 빈칸: 문자열 `s` 의 양 끝 공백을 지운 값
- 세 번째 빈칸: 이름 사이에 넣을 문자열
- 이름 가운데에 있는 공백은 지우지 않습니다(`"doosan robotics"` 는 한 이름입니다).
- **빈칸만** 채웁니다. 다른 줄을 고치거나 줄을 추가하면 오답 처리됩니다.

## 제한 사항
- `text` 는 길이 1 이상 100 이하의 문자열이며, 영문 소문자·공백·쉼표로만 이루어져 있습니다.
- 쉼표로 나눈 조각마다 공백이 아닌 글자가 한 글자 이상 들어 있습니다.

## 입출력 예

| 호출 | 반환값 |
|---|---|
| `solution(" kim, lee ,park ")` | `"kim/lee/park"` |
| `solution("robot")` | `"robot"` |
| `solution("  doosan robotics ,rokey  ")` | `"doosan robotics/rokey"` |

## s14_p12 (정규표현식 · 반환값 · 가장 긴 숫자 덩어리 · 6점)

파일: `s14_p12.py`

문자열 `text` 가 주어질 때, 그 안의 연속된 숫자 덩어리 중 **자릿수가 가장 긴** 것을 문자열 그대로
**반환(return)** 하는 `solution` 함수를 완성하세요.

- 비교 기준은 숫자의 크기가 아니라 글자 수입니다. `"0012 99"` 에서는 4자리인 `'0012'` 를 반환합니다.
- 가장 긴 덩어리가 여러 개면 먼저 나온 것을 반환합니다. `"12 34"` → `'12'`.
- 반환값은 문자열입니다. `'0012'` 를 `12` 로 바꾸면 오답입니다.
- 숫자가 하나도 없으면 빈 문자열 `''` 을 반환합니다.
- 함수 이름과 매개변수는 바꾸지 않습니다. `print` 가 아니라 `return` 으로 돌려줍니다.

## 입출력 예

| text | 반환값 |
|---|---|
| `"a12 b345 c6"` | `'345'` |
| `"0012 99"` | `'0012'` |
| `"12 34"` | `'12'` |
| `"no digits"` | `''` |

