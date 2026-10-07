# 모의고사 1회 (1~16차시) — 퀴즈

> 코드를 실행하지 말고 눈으로 풀어 보세요. 답은 `submissions/<내 ID>/m1/quiz.py` 에 적습니다.
> 출력 예측 문항은 여러 줄이면 `"""` 로 감싸서 줄을 나눠 적고, 띄어쓰기와 따옴표까지 정확히 적습니다.

## Q1 (객관식 · 2점)

다음은 `main.py` 를 실행했을 때 나온 오류 메시지입니다. 이에 대한 설명으로 옳은 것은?

```
Traceback (most recent call last):
  File "main.py", line 3, in <module>
    prnt("start")
NameError: name 'prnt' is not defined
```

1. 오류는 `main.py` 의 1번째 줄에서 발생했다.
2. 따옴표를 빼먹어서 생긴 문법 오류(SyntaxError)다.
3. 파이썬이 고친 코드를 마지막 줄에 보여 준다.
4. `prnt` 라는 이름이 정의되어 있지 않아 생긴 오류이며, 3번째 줄의 `prnt("start")` 가 원인이다.

## Q2 (객관식 · 2점)

실행했을 때 `<class 'float'>` 가 출력되는 것은?

1. `print(type(10 // 4))`
2. `print(type(8 / 2))`
3. `print(type("2.5"))`
4. `print(type(3 * 2))`

## Q3 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요. (띄어쓰기까지 정확히 적습니다)

```python
n = 7
price = 2500
print("수량:", n, "개")
print("수량: " + str(n) + "개")
print(f"총액 {price * n}원")
print(price // n, price % n)
```

## Q4 (객관식 · 2점)

다음 코드를 실행했을 때 첫째 줄과 둘째 줄에 출력되는 값을 차례로 적은 것은?

```python
a = 12
b = 5
print(a // b == 2 and a % b != 2)
print(not a > b or b * 3 > a)
```

1. `False`, `True`
2. `True`, `False`
3. `True`, `True`
4. `False`, `False`

## Q5 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
items = [10, 20, 30, 40]
items.insert(1, 15)
items.remove(30)
last = items.pop()
print(items, last)
print(items[1:3])
info = {"name": "로키", "age": 3}
info["age"] = 4
info["city"] = "서울"
print(info)
print(len(info), info.get("job"))
```

## Q6 (객관식 · 2점)

다음 코드를 실행했을 때 출력되는 것은?

```python
a = [5, 10, 15, 20, 25]
del a[1]
b = a[1:3]
b[0] = 0
print(a, b)
```

1. `[5, 0, 20, 25] [0, 20]`
2. `[5, 15, 20, 25] [0, 20]`
3. `[5, 15, 20, 25] [15, 20]`
4. `[5, 10, 15, 20, 25] [0, 20]`

## Q7 (객관식 · 2점)

다음 코드를 실행했을 때 출력되는 값은?

```python
count = 0
for i in range(2, 20, 4):
    if i % 3 == 0:
        continue
    count += 1
print(count)
```

1. `5`
2. `4`
3. `3`
4. `2`

## Q8 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요. (여러 줄이면 `"""` 로 감싸서 줄을 나눠 적습니다)

```python
def countdown(n):
    while n > 0:
        print(n, end=" ")
        n -= 2
    print("발사")
    return n

left = countdown(5)
print(left)
```

## Q9 (객관식 · 2점)

다음 코드를 실행했을 때 첫째 줄과 둘째 줄에 출력되는 값은?

```python
count = 0

def hit():
    global count
    count += 1
    return count * 10

print(hit() + hit())
print(count)
```

1. `20` 과 `2`
2. `30` 과 `0`
3. `20` 과 `0`
4. `30` 과 `2`

## Q10 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
def tweak(data):
    data[0] = 0
    data = [9, 9]
    return data

a = [1, 2, 3]
b = a
c = tweak(a)
print(a)
print(b)
print(c)
print(a == b, a == c)
```

## Q11 (객관식 · 2점)

클래스에 대한 설명으로 옳지 **않은** 것은?

1. `__init__()` 은 객체를 만들 때 자동으로 호출되어 멤버를 초기화한다.
2. `self` 는 메서드를 호출한 객체 자신을 가리키며, 메서드를 정의할 때 첫 번째 매개변수로 적고 호출할 때는 적지 않는다.
3. 인스턴스 변수는 `클래스이름.변수` 로 객체를 만들지 않고도 읽을 수 있다.
4. 클래스 변수는 클래스 안, 메서드 밖에 선언하며 클래스에 하나만 있다.

## Q12 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
class Robot:
    def __init__(self, name):
        self.name = name
        self.battery = 100

    def work(self):
        self.battery -= 30
        print(self.name, "작업", self.battery)


class CleanBot(Robot):
    def __init__(self, name, area):
        super().__init__(name)
        self.area = area

    def work(self):
        super().work()
        print(self.area, "청소 완료")


c = CleanBot("R1", "거실")
c.work()
r = Robot("R2")
r.work()
print(c.battery + r.battery)
```

## Q13 (객관식 · 2점)

PyQt6 에서 버튼 `btn` 을 클릭할 때마다 함수 `order` 가 실행되도록 연결하는 코드로 옳은 것은?

1. `btn.clicked.connect(order)`
2. `btn.clicked.connect(order())`
3. `btn.clicked().connect(order)`
4. `btn.connect(clicked, order)`

## Q14 (객관식 · 2점)

다음 코드를 실행했을 때 출력되는 것은? (`d.txt` 는 처음에 없습니다)

```python
with open("d.txt", "w") as f:
    f.write("1\n2\n")
with open("d.txt", "a") as f:
    f.write("3")
with open("d.txt") as f:
    lines = f.readlines()
print(len(lines), lines[-1])
```

1. `2 3`
2. `3 3`
3. `1 3`
4. 모드를 생략한 세 번째 `open()` 에서 오류가 발생한다

## Q15 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
def parse(text):
    try:
        parts = text.strip().split(",")
        total = 0
        for p in parts:
            total += int(p)
        return total
    except ValueError:
        print("오류:", len(parts))
        return -1
    finally:
        print("검사 완료")

print(parse(" 3,4,5 "))
print(parse("1,x,2"))
```

## Q16 (객관식 · 2점)

다음 코드를 실행했을 때 출력되는 것은?

```python
import re
print(re.findall(r"\w+", "py_3 x-9"))
```

1. `['py', '3', 'x', '9']`
2. `['py_3', 'x-9']`
3. `['py_3', 'x', '9']`
4. `['py_3x9']`

## Q17 (단답 · 3점)

다음 코드를 실행했을 때 출력되는 값을 적으세요.

```python
g = (x * 2 for x in range(1, 5))
next(g)
print(next(g) + next(g))
```

## Q18 (단답 · 3점)

다음 코드를 실행했을 때 출력되는 문자열을 적으세요.

```python
stack = []
for ch in "rokey":
    if ch == "o":
        stack.pop()
    else:
        stack.append(ch)
print("".join(stack))
```
