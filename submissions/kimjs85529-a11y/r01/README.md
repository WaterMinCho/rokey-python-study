# 1회차 미니 모의고사

> 프로그램(`python study.py`)에서 풀면 이 폴더의 `quiz.py` 와 `.py` 파일에 답이 자동으로 저장됩니다.

문항 18개(보강할 단원 16개) · 평균 레벨 1.6 · 단원: s04 2, s09 2, s10 2, s11 2, s14 2, s01 1, s02 1, s05 1, s06 1, s08 1, s12 1, s13 1, s15 1

## s01_Q5 (파이썬 소개 및 환경설정 · 객관식 · 2점)

VSCode 에 대한 설명으로 **옳지 않은** 것은?

1. macOS·Linux·Windows 에서 실행되는 무료 코드 편집기이다.
2. 메뉴를 한국어로 보려면 확장(Extensions)에서 Korean Language Pack 을 설치한다.
3. Python 확장은 VSCode 에 처음부터 포함되어 있어서 따로 설치할 필요가 없다.
4. 탐색기에서 `.py` 파일을 우클릭해 [터미널에서 Python 파일 실행]을 고르면 실행 결과가 터미널에 나타난다.
5. 실행할 때 Python 인터프리터가 선택되지 않으면, 파이썬 설치 여부와 환경 변수 Path 설정을 확인한다.

## s02_Q4 (프로그래밍 기초 · 객관식 · 2점)

다음 코드에서 변수 `a`, `b`, `c` 의 자료형을 순서대로 바르게 적은 것은?

```python
a = 10.0
b = "True"
c = False
```

1. int, bool, bool
2. float, bool, bool
3. float, str, bool
4. float, str, str

## s04_Q4 (리스트와 딕셔너리 · 객관식 · 2점)

다음 중 `print(type(v))` 의 출력이 `<class 'tuple'>` 이 **아닌** 것은?

1. `v = ()`
2. `v = ("a")`
3. `v = "a",`
4. `v = "a", "b"`

## s04_Q15 (리스트와 딕셔너리 · 단답 · 3점)

다음 코드를 실행했을 때 화면에 출력되는 값을 적으세요.

```python
menu = ["김밥", "라면", "김밥", "떡볶이"]
menu.remove("김밥")
print(menu[1])
```

## s05_Q3 (반복문 · 객관식 · 2점)

다음 코드를 실행했더니 아래와 같이 출력되었습니다. 빈칸(`____`)에 들어갈 조건으로 알맞은 것은?

```python
count = 5
while ____:
    count -= 1
    print(count)
```

```
4
3
2
```

1. `count > 2`
2. `count >= 2`
3. `count > 3`
4. `count != 3`

## s09_Q7 (클래스(1) · 객관식 · 2점)

다음 클래스로 객체를 올바르게 생성하는 문장은?

```python
class Train:
    def __init__(self, line, cars):
        self.line = line
        self.cars = cars
```

1. `t = Train()`
2. `t = Train(2, 10)`
3. `t = Train(self, 2, 10)`
4. `t = Train.__init__(2, 10)`

## s10_Q13 (클래스(2) · 출력 예측 · 3점)

다음 코드를 파일로 저장한 뒤 **직접 실행**했을 때의 출력 결과를 그대로 적으세요.

```python
def plus(a, b):
    return a + b


print("모듈 시작")

if __name__ == "__main__":
    print(plus(2, 3))

print(__name__)
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

## s12_Q5 (파일 처리 · 객관식 · 2점)

현재 폴더에 `data.txt` 파일이 **없을 때**, 실행하면 오류가 발생하는 것은?

1. `f = open("data.txt", "w")`
2. `f = open("data.txt", "a")`
3. `f = open("data.txt")`
4. `f = open("data.txt", "w", encoding="utf-8")`

## s13_Q16 (예외 처리·문자열·람다·map · 객관식 · 2점)

다음 함수에 대한 설명으로 옳지 **않은** 것은?

```python
def read_score(text):
    try:
        score = int(text)
        print("점수:", score)
    except ValueError:
        print("잘못된 점수")
        score = 0
    print("처리 끝")
    return score
```

1. `read_score("90")` 은 `점수: 90`, `처리 끝` 을 차례로 출력하고 `90` 을 반환한다.
2. `read_score("A")` 는 `잘못된 점수`, `처리 끝` 을 차례로 출력하고 `0` 을 반환한다.
3. `read_score("A")` 에서 `print("점수:", score)` 는 실행되지 않는다.
4. `read_score("3.5")` 는 `점수: 3`, `처리 끝` 을 차례로 출력하고 `3` 을 반환한다.

## s15_Q16 (고급 함수 · 출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
def letters():
    yield "x"
    yield "y"

g = letters()
h = (c for c in "xy")
print(type(g))
print(type(h))
print(next(g), next(h))
print(next(g) + next(h))
```

## s06_p07 (함수(1) · 반환값 · 공백을 뺀 글자 수 · 6점)

파일: `s06_p07.py`

문자열 `text` 가 주어질 때, 공백(`" "`)을 제외한 글자의 수를 반환하는 `solution` 함수를 완성하세요.

- 함수 이름과 매개변수는 바꾸지 않습니다.
- 반환값은 정수(int)입니다.

## 제한 사항
- `text` 의 길이는 0 이상 100 이하입니다. (빈 문자열일 수 있습니다)
- `text` 는 영문자, 숫자, 공백으로만 이루어져 있습니다.

## 입출력 예

| text | 반환값 |
|---|---|
| `"hello world"` | 10 |
| `"abc"` | 3 |
| `" a b "` | 2 |
| `""` | 0 |

## s08_p05 (자료구조와 알고리즘 · 빈칸 채우기 · 선택 정렬 함수 완성 · 6점)

파일: `s08_p05.py`

숫자 리스트 `ca` 를 선택 정렬로 오름차순 정렬하는 함수 `fselsort` 입니다.

- 바깥쪽 반복(`sa`)의 한 단계마다, 인덱스 `sa` 부터 끝까지의 요소 중 가장 작은 값을 찾아 `ca[sa]` 와 맞바꿉니다.
- 한 단계가 끝날 때마다 그때의 리스트를 한 줄씩 출력합니다.
- 넘겨받은 리스트를 직접 정렬하며, 반환값은 없습니다.

빈칸(`____`) 세 곳을 채워 함수를 완성하세요.

- **빈칸만** 채웁니다. 다른 줄을 고치거나 줄을 추가하면 오답 처리됩니다.

## 시작 코드

```python
def fselsort(ca):
    for sa in range(0, len(ca) - 1, 1):
        mina = ca[sa]
        minix = sa
        for sb in range(____, len(ca), 1):
            if mina > ca[sb]:
                mina = ca[sb]
                minix = ____
        temp = ca[sa]
        ca[sa] = ca[minix]
        ca[minix] = ____
        print(ca)
```

## 실행 예

```python
data = [31, 12, 25, 8, 19]
fselsort(data)
```

```
[8, 12, 25, 31, 19]
[8, 12, 25, 31, 19]
[8, 12, 19, 31, 25]
[8, 12, 19, 25, 31]
```

요소가 5개이면 4단계를 수행하므로 4줄이 출력됩니다. (2단계처럼 가장 작은 값이 이미 제자리에 있어도 한 줄을 출력합니다)

## s09_p03 (클래스(1) · 출력 · 커피 클래스 만들기 · 4점)

파일: `s09_p03.py`

다음 속성과 동작을 가진 `Coffee` 클래스를 정의하세요.

| 구분 | 이름 | 내용 |
|---|---|---|
| 속성 | `name` | `"라떼"` |
| 속성 | `size` | `"톨"` |
| 동작 | `taste()` | `고소하다` 를 출력 |

- 두 속성은 **클래스 변수**(클래스 안, 메서드 밖)로 선언합니다.
- 클래스만 정의하면 됩니다. 채점할 때는 아래와 같은 테스트 코드가 객체를 만들어 속성을 출력하고 메서드를 호출합니다.

## 테스트 코드와 출력 예

```python
latte = Coffee()
print(latte.name)
print(latte.size)
latte.taste()
```

```
라떼
톨
고소하다
```

```python
print(Coffee.name, Coffee.size)
```

```
라떼 톨
```

- 출력은 글자 하나까지 같아야 합니다.

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

## s14_p01 (정규표현식 · 빈칸 채우기 · 소문자 단어 뽑기 · 4점)

파일: `s14_p01.py`

한 줄을 입력받아, 영문 소문자가 1개 이상 이어진 덩어리를 모두 찾아 리스트로 출력하고
그 개수를 출력하는 프로그램입니다. 빈칸(`____`) 2곳을 채워 프로그램을 완성하세요.

```python
import re

text = input()
p = re.compile(____)   # 영문 소문자가 1개 이상 이어진 덩어리
words = p.____(text)   # 매치되는 모든 문자열을 리스트로
print(words)
print(len(words))
```

- 첫 번째 빈칸에는 정규식 패턴 문자열, 두 번째 빈칸에는 패턴 객체의 메서드 이름이 들어갑니다.
- 대문자와 숫자는 덩어리에 포함되지 않습니다. 매치되는 것이 없으면 `[]` 와 `0` 을 출력합니다.
- **빈칸만** 채웁니다. 다른 줄을 고치거나 줄을 추가하면 오답 처리됩니다.

## 입출력 예

| 입력 | 출력 |
|---|---|
| `we love regex` | `['we', 'love', 'regex']`<br>`3` |
| `Hi there 2024` | `['i', 'there']`<br>`2` |
| `2024` | `[]`<br>`0` |

## s14_p04 (정규표현식 · 출력 · 첫 번째 숫자 찾기 · 4점)

파일: `s14_p04.py`

한 줄을 입력받아, 문자열 안에서 처음 나오는 숫자 덩어리(연속된 숫자)를 찾습니다.

- 찾으면 `found <숫자덩어리> <시작 인덱스>` 를 한 줄로 출력합니다(공백 하나로 구분).
- 숫자가 하나도 없으면 `none` 을 출력합니다.

## 입출력 예

입력
```
abc 123 def
```
출력
```
found 123 4
```

입력
```
no number
```
출력
```
none
```

- `123` 은 인덱스 4 에서 시작합니다(`a`=0, `b`=1, `c`=2, 공백=3).
- 출력은 글자 하나까지 같아야 합니다(소문자, 띄어쓰기 포함).

