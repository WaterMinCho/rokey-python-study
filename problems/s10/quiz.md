# 10차시 퀴즈: 클래스(2)

> 코드를 실행하지 말고 눈으로 풀어 보세요. 답은 `submissions/<내 ID>/s10/quiz.py` 에 적습니다.

## Q1 (객관식 · 2점)

모듈과 패키지에 대한 설명으로 옳지 **않은** 것은?

1. 모듈은 클래스, 함수, 변수 등을 모아 둔 파이썬 파일(`.py`)이다.
2. 패키지는 여러 모듈을 묶어 놓은 디렉터리이다.
3. `mycalc.py` 라는 파일을 만들면 같은 폴더의 다른 파일에서 `import mycalc` 로 불러올 수 있다.
4. 모듈을 불러올 때는 확장자까지 적어 `import mycalc.py` 라고 써야 한다.

## Q2 (객관식 · 2점)

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

## Q3 (객관식 · 2점)

모듈을 불러오는 방법에 대한 설명으로 옳지 **않은** 것은?

1. `import random` 을 실행하면 `random.choice(...)` 처럼 모듈 이름 뒤에 점(`.`)을 붙여 사용한다.
2. `from random import choice` 를 실행한 뒤에는 `random.randint(1, 6)` 도 바로 사용할 수 있다.
3. `from random import choice` 를 실행하면 `random.choice(...)` 가 아니라 `choice(...)` 로 호출한다.
4. `from random import *` 는 모듈의 모든 내용을 모듈 이름 없이 쓰게 해 주지만, 이름이 충돌할 수 있어 권장하지 않는다.

## Q4 (객관식 · 2점)

같은 폴더에 다음 두 파일이 있습니다.

```python
# helper.py
print("helper 로드")

def hello():
    print("안녕")

if __name__ == "__main__":
    print("helper 직접 실행")
```

```python
# main.py
import helper
helper.hello()
```

`python main.py` 로 **main.py 를 실행**했을 때 화면에 출력되는 것은?

1. `안녕`
2. `helper 로드` → `안녕`
3. `helper 로드` → `helper 직접 실행` → `안녕`
4. `helper 직접 실행` → `안녕`

## Q5 (객관식 · 2점)

리스트 `colors` 에서 **중복 없이** 3개를 임의로 뽑아 리스트로 얻으려고 합니다. 올바른 코드는?

```python
import random
colors = ["빨강", "주황", "노랑", "초록", "파랑"]
```

1. `random.choice(colors, 3)`
2. `random.sample(colors, 3)`
3. `random.randint(colors, 3)`
4. `random.sample(3, colors)`

## Q6 (객관식 · 2점)

`Animal` 클래스를 **상속받는** `Dog` 클래스를 정의하려고 합니다. 첫 줄로 옳은 것은?

1. `class Dog(Animal):`
2. `class Animal(Dog):`
3. `class Dog extends Animal:`
4. `class Dog(Animal)`

## Q7 (객관식 · 2점)

다음 코드에 대한 설명으로 옳지 **않은** 것은?

```python
class Printer:
    def start(self):
        print("전원 켜짐")

    def info(self):
        print("일반 프린터")


class ColorPrinter(Printer):
    def info(self):
        print("컬러 프린터")

    def scan(self):
        print("스캔 중")
```

1. `ColorPrinter` 객체는 `start()` 를 직접 정의하지 않았지만 부모에게서 물려받았으므로 호출할 수 있다.
2. `ColorPrinter` 에서 `info()` 를 같은 이름으로 다시 정의한 것을 오버라이딩이라고 한다.
3. `ColorPrinter()` 객체의 `info()` 를 호출하면 `컬러 프린터` 가 출력된다.
4. `Printer()` 객체도 `scan()` 을 호출할 수 있다.

## Q8 (객관식 · 2점)

다음 코드를 실행했을 때의 결과로 옳은 것은?

```python
class Watch:
    def __init__(self, brand):
        self.brand = brand


class SmartWatch(Watch):
    def __init__(self, brand, os):
        self.os = os


s = SmartWatch("가민", "웨어OS")
print(s.os)
print(s.brand)
```

1. `웨어OS` 와 `가민` 이 차례로 출력된다.
2. `가민` 과 `웨어OS` 가 차례로 출력된다.
3. `웨어OS` 가 출력된 뒤, `print(s.brand)` 에서 오류가 발생한다.
4. `SmartWatch("가민", "웨어OS")` 에서 인수 개수가 맞지 않아 오류가 발생한다.

## Q9 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
class Animal:
    legs = 4

    def eat(self):
        print("먹이를 먹는다")


class Bird(Animal):
    legs = 2

    def fly(self):
        print("날아간다")


b = Bird()
b.eat()
b.fly()
print(b.legs, Animal.legs)
```

## Q10 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
class Printer:
    def start(self):
        print("전원 켜짐")

    def work(self):
        print("흑백 인쇄")


class ColorPrinter(Printer):
    def work(self):
        print("컬러 인쇄")


p = Printer()
c = ColorPrinter()
c.start()
c.work()
p.work()
```

## Q11 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
class Bell:
    def ring(self):
        print("딸랑")


class DoorBell(Bell):
    def ring(self):
        print("딩동 ", end="")
        super().ring()
        print("문이 열립니다")


d = DoorBell()
d.ring()
Bell().ring()
```

## Q12 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
class Member:
    def __init__(self, name, point):
        self.name = name
        self.point = point

    def show(self):
        print("이름:", self.name)
        print("포인트:", self.point)


class Vip(Member):
    def __init__(self, name, point, grade):
        super().__init__(name, point * 2)
        self.grade = grade

    def show(self):
        super().show()
        print("등급:", self.grade)


v = Vip("Mina", 100, "골드")
v.show()
```

## Q13 (출력 예측 · 3점)

다음 코드를 파일로 저장한 뒤 **직접 실행**했을 때의 출력 결과를 그대로 적으세요.

```python
def plus(a, b):
    return a + b


print("모듈 시작")

if __name__ == "__main__":
    print(plus(2, 3))

print(__name__)
```

## Q14 (단답 · 3점)

자식 클래스 안에서 **부모 클래스의 메서드**를 호출할 때 사용하는 내장 함수의 이름을 적으세요. (괄호는 빼고 이름만)

## Q15 (단답 · 3점)

모듈이 직접 실행된 메인 모듈인지, 다른 파일에서 import 된 하위 모듈인지 알 수 있게 해 주는 **내장 변수**의 이름을 적으세요. (밑줄까지 정확히)

## Q16 (단답 · 3점)

1 이상 6 이하의 정수 하나를 임의로 뽑으려고 합니다. 빈칸에 들어갈 `random` 모듈의 함수 이름을 적으세요.

```python
import random
dice = random.____(1, 6)
```

## Q17 (객관식 · 2점)

다음 코드가 있습니다. (`pass` 는 아무 일도 하지 않는 자리 채움 문장입니다)

```python
class Pet:
    def __init__(self, name):
        self.name = name


class Cat(Pet):
    def __init__(self, name, color):
        super().__init__(name)
        self.color = color


class Dog(Pet):
    pass
```

아래 중 **오류가 발생하는** 것은?

1. `print(Pet("나비").name)`
2. `print(Cat("나비", "흰색").color)`
3. `print(Dog("초코").name)`
4. `print(Dog("초코", "갈색").name)`

## Q18 (객관식 · 2점)

다음 코드에 대한 설명으로 옳은 것은?

```python
class Vehicle:
    wheels = 4

    def move(self):
        print("이동")


class Bike(Vehicle):
    wheels = 2


class Truck(Vehicle):
    def load(self):
        print("적재")
```

1. `Bike` 와 `Truck` 은 같은 부모를 두었으므로 `Bike()` 객체도 `load()` 를 호출할 수 있다.
2. `Truck().wheels` 의 값은 `4` 이다.
3. `Bike` 가 `wheels` 를 `2` 로 다시 선언했으므로 `Vehicle.wheels` 도 `2` 가 된다.
4. `Bike` 에는 `move` 가 정의되어 있지 않으므로 `Bike().move()` 는 오류가 난다.

## Q19 (객관식 · 2점)

다음 코드를 실행했을 때의 결과로 옳은 것은?

```python
class A:
    def f(self):
        return "A.f"

    def g(self):
        return "A.g"


class B(A):
    def f(self):
        return "B.f"


class C(B):
    def g(self):
        return "C.g+" + super().g()


c = C()
print(c.f(), c.g())
```

1. `B.f C.g+A.g`
2. `A.f C.g+A.g`
3. `B.f C.g+B.g`
4. `B` 클래스에 `g` 가 없으므로 `super().g()` 에서 오류가 발생한다

## Q20 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
class Battery:
    def __init__(self, name, level):
        self.name = name
        self.level = level

    def info(self):
        print(self.name, self.level)


class SolarBattery(Battery):
    def charge(self):
        self.level = self.level + self.level // 4
        print("충전 완료")


s = SolarBattery("태양광", 40)
s.charge()
s.info()
b = Battery("일반", 40)
b.info()
```

## Q21 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요. (`pass` 는 아무 일도 하지 않는 자리 채움 문장입니다)

```python
class Staff:
    def __init__(self, name):
        self.name = name

    def pay(self):
        return 100


class Driver(Staff):
    def pay(self):
        return 150


class Intern(Staff):
    pass


team = [Driver("Kim"), Intern("Lee"), Staff("Park")]
total = 0
for member in team:
    print(member.name, member.pay())
    total = total + member.pay()
print(total)
```

## Q22 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
class Lamp:
    def __init__(self, color):
        self.color = color
        self.power = 10


class DeskLamp(Lamp):
    def __init__(self, color):
        self.power = 5
        super().__init__(color)
        self.angle = 45


d = DeskLamp("흰색")
print(d.color, d.power, d.angle)
```

## Q23 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
class Report:
    def title(self):
        return "보고서"

    def show(self):
        print("[" + self.title() + "]")
        print("끝")


class SalesReport(Report):
    def title(self):
        return "매출 " + super().title()


Report().show()
SalesReport().show()
```

## Q24 (객관식 · 2점)

다음 코드를 설명한 문장 중 옳지 **않은** 것은?

```python
class Tool:
    def use(self):
        print("도구 사용")


class Drill(Tool):
    def use(self):
        print("구멍 뚫기")
```

1. `Tool` 은 부모 클래스(super class), `Drill` 은 자식 클래스(sub class)이다.
2. `Drill` 이 `Tool` 의 멤버를 물려받는 것을 상속(inheritance)이라고 한다.
3. `Drill` 이 `use` 를 같은 이름으로 다시 정의한 것을 오버로딩(overloading)이라고 한다.
4. `Drill()` 객체로 `use()` 를 호출하면 `구멍 뚫기` 가 출력된다.

## Q25 (객관식 · 2점)

같은 폴더에 다음 두 파일이 있습니다.

```python
# unit.py
print("unit:", __name__)


def double(x):
    return x * 2
```

```python
# main.py
from unit import double

print("main:", __name__)
print(double(4))
```

`python main.py` 로 **main.py 를 실행**했을 때 화면에 출력되는 것은?

1. `unit: unit` → `main: __main__` → `8`
2. `unit: __main__` → `main: __main__` → `8`
3. `main: __main__` → `8`
4. `unit: unit` → `main: main` → `8`

## Q26 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
class Part:
    def __init__(self):
        print("Part 준비")
        self.tags = ["부품"]


class Motor(Part):
    def __init__(self, watt):
        super().__init__()
        self.watt = watt
        self.tags.append("모터")
        print("Motor 준비")


class Servo(Motor):
    def __init__(self, watt, angle):
        print("Servo 시작")
        super().__init__(watt * 2)
        self.angle = angle
        self.tags.append("서보")


s = Servo(50, 90)
print(s.watt, s.angle)
print(s.tags)
```

## Q27 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
class Delivery:
    def fee(self):
        return 3000

    def total(self, price):
        return price + self.fee()


class Express(Delivery):
    def fee(self):
        return super().fee() + 2000

    def total(self, price):
        print("기본 배송비", super().fee())
        return super().total(price)


e = Express()
print(e.total(10000))
print(Delivery().total(10000))
```
