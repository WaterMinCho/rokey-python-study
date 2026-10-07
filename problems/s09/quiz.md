# 9차시 퀴즈 — 클래스(1)

> 코드를 실행하지 말고 눈으로 풀어 보세요. 답은 `submissions/<내 ID>/s09/quiz.py` 에 적습니다.

## Q1 (객관식 · 2점)

객체 지향 프로그래밍(OOP)에 대한 설명으로 알맞지 **않은** 것은?

1. 현실 세계의 사물을 본떠서 프로그램을 구성한다.
2. 객체의 속성(데이터)과 동작(기능)을 하나로 묶어 클래스로 만든다.
3. 유지보수가 쉽고 코드를 재사용하기 좋다.
4. 작업을 순서대로 처리하는 데 중점을 두며, 처리 속도가 상대적으로 빠르다.

## Q2 (객관식 · 2점)

클래스와 객체에 대한 설명으로 옳지 **않은** 것은?

1. 클래스는 객체를 만들기 위한 틀(설계도)이고, 객체는 그 틀로 만들어진 실체이다.
2. 클래스로부터 객체를 만드는 것을 인스턴스화라고 한다.
3. 멤버 변수는 객체의 동작을, 메서드는 객체의 속성을 나타낸다.
4. 하나의 클래스로 여러 개의 객체를 만들 수 있다.

## Q3 (객관식 · 2점)

다음 중 오류 없이 실행되는 클래스 정의를 **모두 고르세요**.

**1번**

```python
class Phone:
    pass
```

**2번**

```python
class Phone:
    maker = "ROKEY"
```

**3번**

```python
class Phone
    maker = "ROKEY"
```

**4번**

```python
Class Phone:
    pass
```

## Q4 (객관식 · 2점)

`self` 에 대한 설명으로 옳지 **않은** 것은?

1. 메서드를 호출한 객체 자신을 가리킨다.
2. 메서드를 정의할 때 첫 번째 매개변수 자리에 적는다.
3. `self.변수`, `self.메서드()` 처럼 써서 그 객체의 변수와 메서드를 사용할 수 있다.
4. 메서드를 호출할 때는 `obj.method(obj)` 처럼 `self` 에 들어갈 객체를 괄호 안에 직접 적어 줘야 한다.

## Q5 (객관식 · 2점)

다음 코드에 대한 설명으로 옳지 **않은** 것은?

```python
class Player:
    team = "ROKEY"

    def __init__(self, name):
        self.name = name

p = Player("Mina")
```

1. `team` 은 클래스 변수이고, `name` 은 인스턴스 변수이다.
2. 이어서 `print(Player.team)` 을 실행하면 `ROKEY` 가 출력된다.
3. 이어서 `print(p.team)` 을 실행하면 `ROKEY` 가 출력된다.
4. 이어서 `print(Player.name)` 을 실행하면 `Mina` 가 출력된다.

## Q6 (객관식 · 2점)

다음 코드를 실행했을 때의 결과로 옳은 것은?

```python
class Cup:
    def fill(self, amount):
        self.amount = amount

a = Cup()
b = Cup()
a.fill(300)
print(a.amount)    # (가)
print(b.amount)    # (나)
```

1. (가), (나) 모두 `300` 을 출력한다.
2. (가)는 `300`, (나)는 `0` 을 출력한다.
3. (가)는 `300` 을 출력하고, (나)에서 오류가 발생한다.
4. (가)에서 오류가 발생한다.

## Q7 (객관식 · 2점)

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

## Q8 (객관식 · 2점)

내장 클래스에 대한 설명으로 옳지 **않은** 것은?

1. `int`, `float`, `str`, `list` 는 파이썬이 미리 정의해 둔 클래스이다.
2. `na = 10` 은 `na = int(10)` 처럼 int 클래스의 객체를 만드는 것으로 볼 수 있다.
3. `s = str("abc")` 를 실행한 뒤 `s.capitalize()` 를 호출하면 `"Abc"` 가 반환된다.
4. 3번처럼 `s.capitalize()` 를 호출하고 나서 `print(s)` 를 실행하면 `Abc` 가 출력된다.

## Q9 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
class Member:
    gym = "ROKEY"

    def __init__(self, name, level):
        self.name = name
        self.level = level

m1 = Member("Jisoo", 3)
m2 = Member("Hana", 1)
m2.level = m2.level + m1.level

print(Member.gym)
print(m1.gym, m2.gym)
print(m1.name, m1.level)
print(m2.name, m2.level)
```

## Q10 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
class Lamp:
    def __init__(self):
        print("lamp ready")
        self.on = False

    def switch(self):
        self.on = not self.on
        print("on:", self.on)

print("start")
a = Lamp()
a.switch()
a.switch()
```

## Q11 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
class Basket:
    def __init__(self):
        self.items = []

    def put(self, x):
        self.items.append(x)

    def put_twice(self, x):
        self.put(x)
        self.put(x)

b1 = Basket()
b2 = Basket()
b1.put("egg")
b1.put_twice("milk")
b2.put_twice("tea")
print(b1.items)
print(len(b1.items), len(b2.items))
```

## Q12 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
class Pet:
    def __init__(self, age, name):
        self.age = age
        self.name = name

    def intro(self):
        print(str(self.age) + "살 " + self.name + "입니다.")

a = Pet(3, "보리")
b = Pet(7, "콩이")
b.intro()
a.age = a.age + 1
a.intro()
```

## Q13 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
class Box:
    def size(self, w=2, h=5):
        self.w = w
        self.h = h
        self.area = self.w * self.h

b = Box()
b.size(3, 4)
print(b.area)
b.size(3)
print(b.area)
b.size()
print(b.w, b.h, b.area)
```

## Q14 (단답 · 3점)

객체를 생성할 때 자동으로 호출되어 객체를 초기화하는 메서드의 이름을 적으세요. (괄호와 매개변수는 빼고 이름만)

## Q15 (단답 · 3점)

다음 코드가 끝까지 실행되는 동안 `__init__` 메서드는 모두 몇 번 호출될까요? 숫자만 적으세요.

```python
class Dot:
    def __init__(self):
        self.x = 0

dots = []
for i in range(3):
    dots.append(Dot())

first = dots[0]
last = Dot()
first.x = 5
```

## Q16 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
class Ticket:
    def __init__(self, seat, price):
        self.seat = seat
        self.price = price * 2

    def discount(self, price):
        self.price = self.price - price
        print(self.seat, self.price, price)

t = Ticket("A3", 500)
t.discount(100)
t.discount(50)
```

## Q17 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
class Score:
    def __init__(self, base):
        self.total = base

    def add(self, n):
        self.total = self.total + n
        return self.total

    def add_bonus(self, n):
        first = self.add(n)
        second = self.add(n * 2)
        print(first, second)

s = Score(10)
s.add_bonus(5)
print(s.total)
s.add_bonus(1)
```

## Q18 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
class Bot:
    def __init__(self, name):
        self.name = name
        self.steps = 0

    def walk(self):
        self.steps = self.steps + 1

a = Bot("A")
b = Bot("B")
c = a
a.walk()
c.walk()
b.walk()
print(a.steps, b.steps, c.steps)
c.name = "C"
print(a.name, b.name)
```

## Q19 (객관식 · 2점)

다음 코드를 실행한 뒤의 상태에 대한 설명으로 옳은 것은?

```python
class Timer:
    def __init__(self):
        self.sec = 0

    def tick(self):
        sec = self.sec + 1

    def tock(self):
        self.sec = self.sec + 1

    def show(self):
        print(sec)

t = Timer()
t.tick()
t.tock()
t.tick()
```

1. 이어서 `print(t.sec)` 을 실행하면 `3` 이 출력된다.
2. 이어서 `print(t.sec)` 을 실행하면 `1` 이 출력된다.
3. `tick()` 을 호출할 때마다 `t.sec` 이 1 씩 늘어난다.
4. 이어서 `t.show()` 를 실행하면 `1` 이 출력된다.
