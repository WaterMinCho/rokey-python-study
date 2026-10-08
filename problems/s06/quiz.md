# 6차시 퀴즈: 함수(1)

> 코드를 실행하지 말고 눈으로 풀어 보세요. 답은 `submissions/<내 ID>/s06/quiz.py` 에 적습니다.

## Q1 (객관식 · 2점)

다음 중 함수를 정의하는 코드의 **첫 줄**로 문법이 올바른 것은?

1. `def greet:`
2. `def greet()`
3. `function greet():`
4. `def greet():`

## Q2 (객관식 · 2점)

함수의 종류에 대한 설명으로 옳은 것은?

1. `print()` 는 `def` 로 직접 정의해야만 쓸 수 있는 사용자 정의 함수이다.
2. 내장 함수는 파이썬에 처음부터 포함되어 있어, 따로 정의하지 않고 바로 호출할 수 있다.
3. 모듈은 여러 값을 한 변수에 모아 두는 자료형이다.
4. 사용자 정의 함수는 매개변수를 가질 수 없다.

## Q3 (객관식 · 2점)

함수를 사용하는 목적(장점)에 대한 설명으로 옳지 **않은** 것은?

1. 한 번 정의해 두면 프로그램의 여러 위치에서 호출해 다시 쓸 수 있다.
2. 기능을 고칠 때 함수 정의만 수정하면, 그 함수를 호출하는 모든 곳이 똑같이 바뀐 동작을 한다.
3. 함수 내부의 복잡한 처리 과정을 다 알지 못해도 이름만 불러 원하는 작업을 할 수 있다.
4. 함수를 정의해 두면 호출하지 않아도 프로그램이 시작될 때 자동으로 한 번 실행된다.

## Q4 (객관식 · 2점)

함수 호출에 대한 설명으로 옳은 것은?

1. 매개변수가 없는 함수는 `greet` 처럼 괄호 없이 이름만 적어도 호출된다.
2. 매개변수가 2개인 함수에 인수를 1개만 넘기면, 남은 매개변수에는 자동으로 0 이 들어간다.
3. 인수는 왼쪽부터 순서대로 매개변수에 하나씩 대입된다.
4. 인수로 변수를 넘길 때는 그 변수의 이름이 매개변수의 이름과 같아야 한다.

## Q5 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
def show(pa, pb, pc):
    print(pc, pa, pb)

a = 7
b = 2.5
c = "py"
r = show(b, c, a)
print(r)
```

## Q6 (객관식 · 2점)

다음 코드를 실행한 결과로 옳은 것은?

```python
def area(w, h):
    size = w * h

area(3, 4)
print(size)
```

1. `12` 가 출력된다
2. `None` 이 출력된다
3. `size` 가 출력된다
4. 오류가 발생한다

## Q7 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
def check(n):
    print("검사", n)
    return n * 2
    print("끝")

r = check(5)
print(r + 1)
```

## Q8 (객관식 · 2점)

`return` 에 대한 설명으로 옳은 것을 **모두** 고르세요.

1. `return` 문이 실행되면 함수가 그 자리에서 끝나고, 아래에 남은 함수 코드는 실행되지 않는다.
2. `return` 문이 없는 함수를 호출해 그 결과를 변수에 담으면 `None` 이 저장된다.
3. 함수 안에는 `return` 문이 반드시 하나 있어야 한다.
4. `return 값` 은 그 값을 화면에 출력한 뒤 함수를 끝낸다.

## Q9 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
def grade(score):
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"

print(grade(95))
print(grade(85))
print(grade(70))
```

## Q10 (객관식 · 2점)

다음 코드를 실행한 결과로 옳은 것은?

```python
print("시작")
greet()

def greet():
    print("안녕")
```

1. `시작` 과 `안녕` 이 차례로 출력된다.
2. `시작` 만 출력된 뒤 오류가 발생한다.
3. 아무것도 출력되지 않고 오류가 발생한다.
4. `안녕` 이 먼저, `시작` 이 나중에 출력된다.

## Q11 (단답 · 3점)

아래 코드는 함수 이름을 잘못 적어 호출했기 때문에 마지막 줄에서 오류가 발생합니다.
이때 발생하는 오류의 이름을 적으세요. (`○○○Error` 형태, 대소문자까지 정확히)

```python
def start():
    print("go")

strat()
```

## Q12 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
def first():
    print("A")

def second():
    first()
    print("B")

def third():
    print("C")
    second()
    print("D")

third()
```

## Q13 (객관식 · 2점)

다음 코드를 실행했을 때 출력되는 것은?

```python
def total(price, count=2):
    return price * count

print(total(500))
```

1. `500`
2. `1000`
3. `2`
4. 오류가 발생한다

## Q14 (단답 · 3점)

다음 코드를 실행한 뒤 변수 `x` 에 저장되어 있는 값을 적으세요.

```python
def step(n):
    if n % 2 == 0:
        return n // 2
    return n * 3 + 1

x = step(step(6))
```

## Q15 (객관식 · 2점)

다음 코드에 대한 설명으로 옳은 것을 **모두** 고르세요.

```python
def scale(value, ratio):
    result = value * ratio
    return result

base = 4
out = scale(base, 2.5)
```

1. `value` 와 `ratio` 는 매개변수이고, `base` 와 `2.5` 는 인수이다.
2. `scale(base, 2.5)` 를 호출하면 `ratio` 에 `4` 가 대입된다.
3. 코드를 끝까지 실행하면 `out` 에 `10.0` 이 저장된다.
4. 마지막 줄 아래에 `print(result)` 를 추가하면 `10.0` 이 출력된다.

## Q16 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
def first_over(nums, limit):
    for n in nums:
        if n > limit:
            return n
        print("skip", n)
    return -1

print(first_over([3, 8, 12, 5], 7))
print(first_over([6, 7], 7))
```

## Q17 (객관식 · 2점)

다음 코드를 실행한 결과로 옳은 것은?

```python
def report():
    print("보고 시작")
    line()
    print("보고 끝")

def line():
    print("-----")

report()
```

1. 아무것도 출력되지 않고 오류가 발생한다.
2. `보고 시작` 만 출력된 뒤 오류가 발생한다.
3. `보고 시작`, `-----`, `보고 끝` 이 차례로 출력된다.
4. `-----`, `보고 시작`, `보고 끝` 이 차례로 출력된다.

## Q18 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
def order(a, b):
    if a < b:
        return a, b
    return b, a

r = order(9, 4)
print(r)
print(r[0] + r[1] * 2)
print(order(5, 5))
```

## Q19 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
def twice(n):
    print(n * 2)

def triple(n):
    return n * 3

a = twice(4)
b = triple(4)
print(a, b)
print(twice(triple(1)))
```
