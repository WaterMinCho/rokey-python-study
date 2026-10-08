# 7차시 퀴즈: 함수(2)

> 코드를 실행하지 말고 눈으로 풀어 보세요. 답은 `submissions/<내 ID>/s07/quiz.py` 에 적습니다.

## Q1 (객관식 · 2점)

전역 변수와 지역 변수에 대한 설명으로 **옳지 않은** 것은?

1. 전역 변수는 함수 바깥에서 만든 변수이며, 프로그램이 끝날 때까지 유지된다.
2. 함수마다 자신만의 이름공간(namespace)이 있어서, `global` 선언이 없다면 함수 안에서 만든 변수와 함수 밖의 변수는 이름이 같아도 서로 다른 변수이다.
3. 전역 변수의 값은 `global` 선언 없이도 함수 안에서 읽을(참조할) 수 있다.
4. 지역 변수는 그 함수를 한 번 호출하고 나면 함수 밖에서도 사용할 수 있다.

## Q2 (객관식 · 2점)

다음 코드는 마지막 줄에서 오류가 발생합니다. 그 이유로 알맞은 것은?

```python
def make_total(a, b):
    total = a + b

make_total(3, 4)
print(total)
```

1. `total` 은 함수 안에서만 존재하는 지역 변수라서, 함수 밖에서는 사용할 수 없기 때문이다.
2. 함수에 `return` 이 없어서 `total` 에 `None` 이 들어 있기 때문이다.
3. 함수를 정의하기 전에 호출했기 때문이다.
4. 인수의 개수와 매개변수의 개수가 다르기 때문이다.

## Q3 (객관식 · 2점)

다음과 같이 전역 변수 `x` 와 함수 세 개를 정의했습니다. 각 함수를 따로 호출했을 때 **오류가 발생하는** 호출은?

```python
x = 10

def fa(num):
    b = x + num
    print(b)

def fb(num):
    x = x + num
    print(x)

def fc(num):
    global x
    x = x + num
    print(x)
```

1. `fa(5)`
2. `fb(5)`
3. `fc(5)`
4. 셋 다 오류 없이 `15` 를 출력한다

## Q4 (객관식 · 2점)

어떤 함수 안에서 `global a` 를 선언했습니다. 이에 대한 설명으로 **옳은** 것은?

1. 그 함수 안에 `a` 라는 지역 변수가 새로 만들어진다.
2. 그 함수 안에서 `a` 에 값을 대입하면 전역 변수 `a` 의 값이 바뀐다.
3. 함수 실행이 끝나면 전역 변수 `a` 도 함께 사라진다.
4. `global a` 는 함수 바깥(전역 영역)에 적어야만 효과가 있다.

## Q5 (객관식 · 2점)

함수를 다음과 같이 정의했습니다. 이어서 실행했을 때 **오류가 발생하는** 호출은?

```python
def order(menu, count=1):
    print(menu, count)
```

1. `order("라떼")`
2. `order("라떼", 3)`
3. `order()`
4. `order(2)`

## Q6 (객관식 · 2점)

다음 코드를 실행했을 때의 결과로 알맞은 것은?

```python
def show(width, height):
    print("A", width, height)

def show():
    print("B")

show(3, 4)
```

1. `A 3 4` 가 출력된다
2. `B` 가 출력된다
3. `A 3 4` 와 `B` 가 차례로 출력된다
4. 오류가 발생한다

## Q7 (객관식 · 2점)

다음 코드를 실행했을 때의 결과로 알맞은 것은?

```python
def area(w: int, h: int) -> int:
    return w * h

print(area(1.5, 2))
```

1. `2`
2. `3`
3. `3.0`
4. 오류가 발생한다

## Q8 (출력 예측 · 3점)

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

## Q9 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
x = 1
y = 1

def change():
    global y
    x = 50
    y = 50
    print(x, y)

change()
print(x, y)
```

## Q10 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요. (띄어쓰기까지 정확히)

```python
def room(width=6, height=2):
    print("width=", width, "height=", height)

room()
room(9)
room(9, 5)
```

## Q11 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
total = 0
print("A")

def add(num):
    global total
    total = total + num
    print("B", total)

print("C")
add(5)
add(5)
print("D", total)
```

## Q12 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
def count_down(n):
    if n <= 0:
        print("발사!")
        return
    print(n)
    count_down(n - 2)

count_down(5)
```

## Q13 (단답 · 3점)

다음 코드는 실행하면 `7` 을 출력합니다. 빈칸(`____`)에 들어갈 **키워드 하나**를 적으세요.

```python
score = 2

def bonus():
    ____ score
    score = score + 5

bonus()
print(score)
```

## Q14 (단답 · 3점)

다음 코드를 실행했을 때 출력되는 **숫자**를 적으세요.

```python
def plus3(num):
    return num + 3

def twice(num):
    return plus3(num) * 2

a = plus3(4)
b = twice(a)
print(b)
```

## Q15 (객관식 · 2점)

네임스페이스(namespace, 이름공간)에 대한 설명으로 **옳은** 것은?

1. 프로그램 전체가 네임스페이스 하나를 함께 쓰므로, 함수 안과 밖에서 같은 이름을 쓰면 언제나 같은 변수를 가리킨다.
2. 변수 이름을 정의하는 공간이며, 프로그램 전체에서 쓰는 전역 네임스페이스와 함수마다 생기는 지역 네임스페이스로 구별한다.
3. 인수를 생략했을 때 대신 쓰이도록 매개변수에 미리 적어 두는 값을 말한다.
4. 매개변수와 반환값에 기대하는 자료형을 적어 두는 표시를 말한다.

## Q16 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
a = 3
b = 8
a = b
b = a
print(a, b)

c = 3
d = 8
temp = c
c = d
d = temp
print(c, d)
```

## Q17 (객관식 · 2점)

다음 재귀 함수에서 **기저 조건**과 **재귀 단계**에 해당하는 줄을 바르게 짝지은 것은?

```python
def count_up(n):
    if n > 3:           # (가)
        return
    print(n)            # (나)
    count_up(n + 1)     # (다)

count_up(1)
```

1. 기저 조건 (가), 재귀 단계 (다)
2. 기저 조건 (나), 재귀 단계 (다)
3. 기저 조건 (다), 재귀 단계 (가)
4. 기저 조건 (가), 재귀 단계 (나)

## Q18 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
a = 10

def use_local():
    a = 0
    a = a + 3
    print("local", a)

def use_global():
    global a
    a = a + 3
    print("global", a)

use_local()
use_global()
use_local()
print(a)
```

## Q19 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
def walk(n):
    if n == 0:
        print("도착")
        return
    print("가는 길", n)
    walk(n - 1)
    print("오는 길", n)

walk(2)
```

## Q20 (객관식 · 2점)

다음 네 프로그램을 각각 따로 실행했을 때 **오류가 발생하는** 것을 **모두 고르세요**.

**1번**

```python
count = 0

def show():
    print(count)

show()
```

**2번**

```python
count = 0

def show():
    print(count)
    count = 1

show()
```

**3번**

```python
def setup():
    global count
    count = 5

setup()
print(count)
```

**4번**

```python
def setup():
    count = 5

setup()
print(count)
```
