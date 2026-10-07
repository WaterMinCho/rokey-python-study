# 10차시 · 클래스(2)

9차시에서 만든 클래스를 파일 단위로 나눠 쓰는 법(모듈·import)과, 클래스끼리 성질을 물려주는 상속·오버라이딩을 배우는 차시입니다.
모듈 쪽은 여러 파일이 얽히므로 용어와 동작 순서를 묻는 객관식이, 상속 쪽은 코드를 눈으로 실행하는 출력 문제와 클래스를 직접 쓰는 문제가 나오기 좋습니다.

## 1. 모듈과 패키지

- **모듈(module)**: 클래스·함수·변수를 모아 둔 파이썬 파일(.py) 하나입니다. 같은 코드를 여러 프로그램에서 다시 쓰려고 만듭니다.
- **패키지(package)**: 여러 모듈을 묶어 놓은 디렉터리(폴더)입니다.
- 파일 `calc.py` 를 만들면 그 순간 `calc` 모듈이 생깁니다. 모듈 이름은 확장자를 뺀 파일 이름입니다.

```python
# calc.py
class Box:
    def __init__(self):
        self.items = []

    def put(self, x):
        self.items.append(x)

    def show(self):
        print(self.items)


def plus(a, b):
    return a + b


print("calc 모듈 로드")      # 모듈 최상위 코드
```

## 2. import 의 세 가지 형태

| 형태 | 쓰는 법 | 사용할 때 |
|---|---|---|
| `import 모듈` | `import calc` | `calc.plus(1, 2)`, `calc.Box()` 처럼 모듈 이름과 점(.)을 붙여 씁니다 |
| `from 모듈 import 이름` | `from calc import plus` | `plus(1, 2)` 처럼 모듈 이름 없이 씁니다. 가져온 이름(`plus`)만 쓸 수 있습니다 |
| `from 모듈 import *` | `from calc import *` | 모듈의 모든 이름을 그대로 씁니다. 가독성이 나빠지고 이름이 충돌할 수 있어 권장하지 않습니다 |

- 별칭: `import calc as c` 라고 하면 `c.plus(1, 2)` 처럼 짧은 이름으로 씁니다.
- `from calc import plus` 를 한 뒤 `calc.plus(1, 2)` 라고 쓰면 `NameError` 입니다. `calc` 라는 이름은 만들어지지 않았기 때문입니다.
- 반대로 `import calc` 만 한 뒤 `plus(1, 2)` 라고 써도 `NameError` 입니다. 모듈 이름을 붙여야 합니다.
- 파이썬이 미리 제공하는 내장 라이브러리(`random`, `math`, `turtle`, `tkinter` 등)도 같은 방법으로 불러옵니다. `from math import factorial` 뒤에 `factorial(5)` 를 부르면 120 입니다.

## 3. import 하면 모듈의 코드가 실행된다

`import calc` 또는 `from calc import plus` 를 만나는 순간 파이썬은 calc.py 를 처음부터 끝까지 한 번 실행합니다.
그래서 모듈 맨 바깥에 있는 `print("calc 모듈 로드")` 는 import 하는 쪽 프로그램이 아무 출력을 하기 전에 먼저 화면에 찍힙니다.

```python
# main.py
import calc                 # 여기서 "calc 모듈 로드" 출력
print(calc.plus(10, 20))    # 30
```

출력 순서는 `calc 모듈 로드` 다음에 `30` 입니다.

## 4. 메인 모듈 · 하위 모듈과 `__name__`

- 메인 모듈: 내가 직접 실행한 파일(`python main.py` 의 main.py)입니다.
- 하위 모듈: 메인 모듈이 `import` 로 불러온 파일입니다.
- 모든 모듈에는 내장 변수 **`__name__`** 이 있습니다(밑줄 두 개씩).
  - 메인 모듈로 실행되면 `__name__` 에 문자열 `"__main__"` 이 들어 있습니다.
  - 하위 모듈로 import 되면 모듈 이름(예: `"calc"`)이 들어 있습니다.

```python
# calc.py 의 맨 아래
if __name__ == "__main__":      # 직접 실행했을 때만 참
    b = Box()
    b.put(1)
    b.show()                    # [1]
```

- `python calc.py` 로 직접 실행하면 `if` 안이 실행되어 `[1]` 이 출력됩니다.
- 다른 파일에서 `import calc` 하면 `__name__` 이 `"calc"` 이라 `if` 안은 실행되지 않습니다. 테스트용 코드를 직접 실행할 때만 돌리고 import 할 때는 조용히 두는 장치입니다.

## 5. random 모듈 (내장 라이브러리 예)

```python
import random
cards = ["A", "K", "Q", "J"]
random.choice(cards)        # 값 하나를 임의로 선택         예) 'K'
random.sample(cards, 2)     # 중복 없이 2개를 뽑아 리스트로   예) ['Q', 'A']
random.randint(1, 6)        # 1 이상 6 이하의 정수 하나(양 끝 포함)
```

- `choice` 는 값 하나, `sample` 은 리스트를 돌려줍니다. 뽑을 개수는 `sample` 의 두 번째 인수입니다.
- 결과가 매번 달라지므로 실행 결과를 맞히는 문제가 아니라 어떤 함수를 써야 하는지 묻는 문제로 나옵니다.

## 6. 상속(inheritance)

어떤 클래스(**자식, sub class**)가 다른 클래스(**부모, super class**)의 변수와 메서드를 물려받는 것입니다. 기존 클래스를 고치지 않고 멤버를 추가하거나 동작을 바꿀 때 씁니다.

```python
class Animal:                 # 부모 클래스
    legs = 4

    def eat(self):
        print("먹는다")


class Dog(Animal):            # 자식 클래스: 괄호 안에 부모 이름
    def bark(self):           # 자식만의 새 메서드
        print("멍멍")


d = Dog()
d.eat()        # 먹는다   (Animal 에서 물려받음)
d.bark()       # 멍멍
print(d.legs)  # 4        (클래스 변수도 물려받음)
```

- 문법은 `class 자식이름(부모이름):` 이고 괄호 안이 부모입니다. `class Animal(Dog)` 라고 쓰면 반대로 Animal 이 Dog 를 상속하게 됩니다.
- 자식 객체는 부모의 모든 멤버와 자기 멤버를 씁니다. 부모 객체는 자식의 멤버를 쓸 수 없습니다(`Animal().bark()` 는 오류).
- 자식이 `__init__` 을 따로 만들지 않으면 부모의 `__init__` 이 그대로 쓰입니다. 생성할 때 넘기는 인수도 부모 기준입니다.

## 7. 오버라이딩(overriding)

부모의 메서드를 자식 클래스에서 같은 이름으로 다시 정의하는 것입니다.

```python
class Printer:
    def start(self):
        print("전원 켜짐")

    def work(self):
        print("흑백 인쇄")


class ColorPrinter(Printer):
    def work(self):               # 부모의 work 를 재정의
        print("컬러 인쇄")


c = ColorPrinter()
c.start()      # 전원 켜짐   (재정의하지 않은 메서드는 부모 것)
c.work()       # 컬러 인쇄   (재정의한 메서드는 자식 것)
Printer().work()   # 흑백 인쇄 (부모 객체는 영향 없음)
```

- 재정의하지 않은 메서드는 부모 것이, 재정의한 메서드는 자식 것이 실행됩니다.
- 용어 구분: **오버라이딩**은 같은 이름으로 재정의하는 것입니다. 오버로딩·다형성은 다른 개념입니다. 객관식 보기에 섞여 나오면 "부모 메서드를 자식에서 재정의"가 오버라이딩입니다.

## 8. super() — 부모의 메서드 호출하기

`super()` 는 자식 클래스 안에서 부모 클래스를 가리키는 내장 함수입니다. 재정의한 메서드 안에서 부모 버전을 이어서 쓰고 싶을 때 `super().메서드()` 로 호출합니다.

```python
class Bell:
    def ring(self):
        print("딸랑")


class DoorBell(Bell):
    def ring(self):
        print("딩동 ", end="")   # 줄을 바꾸지 않음
        super().ring()           # 부모의 ring()


DoorBell().ring()    # 딩동 딸랑
```

가장 많이 쓰는 곳은 `__init__` 입니다. 자식이 `__init__` 을 새로 만들면 부모의 `__init__` 은 자동으로 호출되지 않으므로, 부모가 저장하던 변수를 그대로 쓰려면 직접 불러 줘야 합니다.

```python
class Device:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def info(self):
        print("제품:", self.name)
        print("가격:", self.price)


class Laptop(Device):
    def __init__(self, name, price, ram):
        super().__init__(name, price)   # 부모가 name, price 를 저장
        self.ram = ram

    def info(self):
        super().info()                  # 부모의 두 줄 출력
        print("램:", self.ram)


Laptop("그램", 1500000, 16).info()
# 제품: 그램
# 가격: 1500000
# 램: 16
```

- `super().__init__(...)` 의 괄호 안에는 `self` 를 빼고 부모 `__init__` 의 매개변수 순서대로 넘깁니다.
- `super()` 뒤에 괄호가 있다는 점에 주의하세요. `super.ring()` 처럼 괄호를 빼면 오류입니다.

## 9. 메서드를 찾는 순서와 self

객체로 `obj.메서드()` 를 부르면 파이썬은 **그 객체의 클래스 → 부모 → 부모의 부모** 순서로 이름을 찾고, 처음 만난 것을 실행합니다. 상속이 여러 단계여도 같습니다.

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
print(c.f(), c.g())    # B.f C.g+A.g
```

- `c.f()` 는 `C` 에 없으므로 `B` 의 `f` 가 실행됩니다. `C` 안의 `super().g()` 는 `B` 부터 찾기 시작하는데 `B` 에 `g` 가 없으므로 그 위 `A` 의 `g` 가 실행됩니다. 바로 위 부모에 없다고 오류가 나지는 않습니다.
- 같은 부모를 둔 형제 클래스끼리는 아무것도 물려받지 않습니다. `Bike(Vehicle)`, `Truck(Vehicle)` 이 있을 때 `Truck` 에만 있는 메서드를 `Bike` 객체로 부르면 `AttributeError` 입니다.

부모 메서드 안의 `self.메서드()` 는 **호출한 객체의 클래스** 기준으로 찾습니다. 그래서 자식이 재정의한 버전이 실행됩니다.

```python
class Report:
    def title(self):
        return "보고서"

    def show(self):
        print("[" + self.title() + "]")


class SalesReport(Report):
    def title(self):
        return "매출 보고서"


SalesReport().show()    # [매출 보고서]
```

`show()` 는 부모에만 있지만, 그 안의 `self` 가 `SalesReport` 객체이므로 `self.title()` 은 자식의 `title()` 입니다. 부모 메서드를 고치지 않고 일부 동작만 바꾸는 상속의 대표적인 쓰임입니다.

같은 원리로, 서로 다른 자식 객체를 한 리스트에 담고 같은 이름의 메서드를 부르면 객체마다 자기 클래스의 버전이 실행됩니다. 재정의하지 않은 자식은 부모 버전을 씁니다.

```python
team = [Driver("Kim"), Intern("Lee"), Staff("Park")]   # Driver 만 pay() 를 재정의
for member in team:
    print(member.pay())        # 150, 100, 100
```

## 시험에서 헷갈리기 쉬운 포인트

- `import calc` 를 하면 `calc.plus()` 로, `from calc import plus` 를 하면 `plus()` 로 씁니다. 두 가지를 섞어 `from calc import plus` 뒤에 `calc.plus()` 를 쓰거나, `import calc` 뒤에 `plus()` 만 쓰면 `NameError` 입니다.
- import 하는 순간 모듈 파일 전체가 실행됩니다. 모듈 맨 바깥의 `print` 는 import 한 쪽의 첫 출력보다 먼저 나옵니다. `from calc import plus` 처럼 일부만 가져와도 모듈 전체가 실행되는 것은 같습니다.
- `__name__` 은 직접 실행한 파일에서 `"__main__"`, import 된 파일에서는 모듈 이름입니다. `if __name__ == "__main__":` 안의 코드는 import 할 때 실행되지 않습니다. 밑줄은 앞뒤 두 개씩입니다.
- 모듈 이름에 확장자는 붙이지 않습니다. `import calc.py` 는 오류입니다.
- 상속 괄호의 방향은 `class 자식(부모):` 입니다. 괄호 안이 부모입니다.
- 자식이 `__init__` 을 새로 정의하면 부모 `__init__` 은 자동으로 실행되지 않습니다. `super().__init__(...)` 을 빼먹으면 부모가 만들던 변수(`self.name` 등)가 없어서 `AttributeError` 가 납니다.
- 반대로 자식에 `__init__` 이 없으면 부모 `__init__` 이 그대로 쓰입니다. `Dog("초코")` 처럼 부모가 받는 인수를 그대로 넘깁니다.
- 재정의하지 않은 메서드는 부모 것이 실행되고, 재정의한 메서드는 자식 것이 실행됩니다. 자식 클래스를 만들어도 부모 객체의 동작은 바뀌지 않습니다.
- 부모 객체로 자식에만 있는 메서드를 부르면 오류입니다. 상속은 부모에서 자식으로 한 방향으로만 물려줍니다.
- 클래스 변수도 상속됩니다. 자식이 같은 이름의 클래스 변수를 다시 선언하면 자식 객체는 자식 값을, 부모 클래스는 원래 값을 씁니다.
- `super().메서드()` 는 괄호가 두 번 나옵니다. `super()` 가 부모를 뜻하고, 그 뒤에 `.메서드()` 를 붙입니다.
- `super().__init__(...)` 을 자식 `__init__` 의 **뒤쪽**에서 부르면, 그 앞에서 자식이 넣어 둔 같은 이름의 변수를 부모가 덮어씁니다. 보통 첫 줄에서 부릅니다.
- 자식에 `__init__` 이 없으면 인수 개수도 부모 기준입니다. 부모가 `name` 하나를 받는데 `Dog("초코", "갈색")` 처럼 두 개를 넘기면 `TypeError` 입니다.
- 메서드는 자기 클래스 → 부모 → 그 위 순서로 찾습니다. `super()` 도 같은 순서로 이어서 찾으므로 바로 위 부모에 그 메서드가 없어도 오류가 아닙니다. 형제 클래스끼리는 물려받지 않습니다.
- 부모 메서드 안의 `self.다른메서드()` 는 자식이 재정의했으면 자식 버전이 실행됩니다. 부모 메서드 안이라고 부모 버전으로 고정되지 않습니다.
- 리스트에 서로 다른 자식 객체를 담고 같은 메서드를 부르면 객체마다 자기 클래스의 버전이 실행됩니다. 재정의하지 않은 자식은 부모 버전입니다.
- `print("딩동 ", end="")` 는 줄을 바꾸지 않으므로 다음 `print` 의 내용이 같은 줄에 이어서 나옵니다. 출력 예측 문제에서 줄 수를 셀 때 주의하세요.
- `random.sample(리스트, 개수)` 는 중복 없이 뽑아 리스트로, `random.choice(리스트)` 는 값 하나를 돌려줍니다. `random.randint(a, b)` 는 `a` 와 `b` 둘 다 포함한 정수 하나입니다.
- "부모 메서드를 자식에서 같은 이름으로 재정의"는 오버라이딩입니다. 오버로딩·다형성·상속 같은 보기와 구분하세요.
- `from 모듈 import *` 는 모든 것을 가져오지만 가독성이 나빠지고 이름이 충돌할 수 있어 권장하지 않는 방식입니다. "쓸 수 없다"가 아니라 "권장하지 않는다"입니다.
