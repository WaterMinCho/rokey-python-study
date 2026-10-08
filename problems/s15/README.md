# 15차시 · 고급 함수(이터레이터와 제너레이터)

값을 한꺼번에 다 만들어 두지 않고 필요할 때 하나씩 꺼내 쓰는 **이터레이터**(클래스로 만들기)와 **제너레이터**(함수로 만들기)를 배우는 차시입니다.
리스트·딕셔너리를 한 줄로 만드는 **컴프리헨션** 문법도 함께 다룹니다.
용어를 묻는 객관식과, `next()`·`yield` 를 눈으로 따라가는 출력 문제가 나오기 좋은 단원입니다.

## 1. 이터레이터란

- `next()` 를 부를 때마다 다음 값을 하나씩 돌려주는 객체입니다.
- 이터레이터가 되려면 아래 메서드가 모두 있어야 합니다.
  - `__iter__()`: 자기 자신(이터레이터)을 돌려줍니다. 이 메서드가 있어서 for 문과 `iter()` 에 넣을 수 있습니다.
  - `__next__()`: 다음 값을 돌려주고, 더 줄 값이 없으면 `StopIteration` 예외를 일으킵니다.

## 2. 이터러블 vs 이터레이터

| | 이터러블(iterable) | 이터레이터(iterator) |
|---|---|---|
| 뜻 | 반복 가능한 것(for 문에 넣을 수 있음) | 값을 하나씩 꺼낼 수 있는 것 |
| 필요한 메서드 | `__iter__()` → 이터레이터를 돌려줌 | `__next__()` + `__iter__()` 는 자기 자신 |
| 예 | 리스트, 튜플, 문자열, 딕셔너리 | `iter(리스트)`, 제너레이터 객체 |
| `next()` 가능? | 안 됨 → `TypeError` | 됨 |

```python
a = [1, 2, 3]
# next(a)          # TypeError: 'list' object is not an iterator
it = iter(a)        # 이터러블을 이터레이터로 변환
print(type(it))     # <class 'list_iterator'>
print(next(it))     # 1
print(next(it))     # 2
print(next(it))     # 3
# next(it)         # StopIteration
```

리스트는 for 문에 넣을 수 있지만(반복 가능) 이터레이터는 아닙니다. `iter()` 로 이터레이터를 만든 뒤에야 `next()` 를 쓸 수 있습니다.

`iter()` 를 이터러블에 부르면 처음부터 읽는 새 이터레이터가 만들어지고, 이터레이터에 부르면 그 이터레이터 자신이 돌아옵니다.

```python
word = "abc"
p = iter(word)
q = iter(word)      # p 와 별개인 새 이터레이터
r = iter(p)         # 이터레이터의 __iter__() 는 자기 자신을 돌려줌 (r 과 p 는 같은 객체)
print(next(p))      # a
print(next(r))      # b   p 가 a 를 꺼낸 다음 값
print(next(q))      # a   q 는 p 와 따로 위치를 기억
```

## 3. for 문과 이터레이터

- for 문은 속으로 `iter()` 를 한 번 부른 뒤 `next()` 를 반복하고, `StopIteration` 이 나면 오류 없이 멈춥니다. 그래서 for 문에서는 예외가 보이지 않습니다.
- 이터레이터는 **일회용**입니다. 한 번 끝까지 읽으면 처음으로 되돌릴 수 없습니다.

```python
it = iter([1, 2, 3])
print(next(it))     # 1
for x in it:
    print(x)        # 2, 3
for x in it:
    print(x)        # 아무것도 출력되지 않음
```

리스트는 for 문에 넣을 때마다 새 이터레이터가 만들어지므로 몇 번이든 처음부터 읽을 수 있습니다.

```python
nums = [1, 2, 3]
it = iter(nums)
print([x * 2 for x in it])      # [2, 4, 6]
print([x * 2 for x in it])      # []         it 는 이미 끝까지 읽음
print([x * 2 for x in nums])    # [2, 4, 6]  리스트는 다시 처음부터
```

13차시의 `map()` 이 돌려주는 객체도 이터레이터입니다. `list()` 로 한 번 값을 모두 꺼내고 나면 두 번째 `list()` 는 빈 리스트를 돌려줍니다.

## 4. 클래스로 이터레이터 만들기

```python
class Count:
    def __init__(self, stop):
        self.n = 0
        self.stop = stop

    def __iter__(self):
        return self

    def __next__(self):
        if self.n >= self.stop:
            raise StopIteration
        self.n += 1
        return self.n

for x in Count(3):
    print(x)                     # 1 2 3
```

- `__iter__` 를 만들면 `__next__` 도 반드시 만들어야 합니다. 이 메서드들은 `__init__` 처럼 파이썬이 특별하게 취급하므로 for 문과 `next()` 가 알아서 호출합니다.
- 리스트나 문자열을 받아 앞에서부터 돌려줄 때는 위치를 0 에서 시작해 `+= 1` 하고, 위치가 `len(data)` 이상이면 `StopIteration` 을 일으킵니다.
- 역순으로 돌려주려면 위치를 `len(data) - 1` 에서 시작해 `-= 1` 하고, `< 0` 이면 `StopIteration` 을 일으킵니다. 끝 조건을 `<= 0` 으로 쓰면 인덱스 0 의 원소가 빠집니다.
- `__next__` 안에서 **값을 바꾸는 줄과 `return` 하는 줄의 순서**가 출력을 결정합니다. 위 예는 먼저 1 을 더하고 돌려주므로 1 부터 시작하지만, 순서를 바꾸면 0 부터 시작합니다.

이터레이터 클래스도 상속할 수 있습니다(10차시). 자식 클래스는 부모의 `__iter__` 를 물려받으므로 `__next__` 만 재정의하면 되고, 부모의 `__next__` 는 `super().__next__()` 로 부릅니다.

```python
class Doubled(Count):
    def __next__(self):
        return super().__next__() * 2

print(list(Doubled(3)))          # [2, 4, 6]
```

부모의 `__next__` 가 일으킨 `StopIteration` 은 자식의 `__next__` 를 빠져나가 for 문이나 `list()` 까지 전달됩니다. 자식 클래스에 `raise StopIteration` 을 따로 적지 않아도 반복이 끝납니다.

## 5. 제너레이터

- 이터레이터를 만들어 주는 함수입니다. 값을 돌려줄 때 `return` 대신 `yield` 를 씁니다.
- 제너레이터 함수를 호출해도 본문은 실행되지 않고 제너레이터 객체만 생깁니다. `type(g)` 는 `<class 'generator'>` 로 출력됩니다.
- `next()` 를 부를 때마다 다음 `yield` 까지 실행하고 → 값을 돌려주고 → 그 자리에서 일시 정지(상태 기억)합니다. 다음 `next()` 에서 멈춘 곳부터 이어서 실행합니다.
- 실행을 이어 가다 `yield` 를 더 만나지 못하고 함수 본문이 끝나면 그 `next()` 호출에서 `StopIteration` 예외가 발생합니다.

```python
def gen():
    print("A")
    yield 1
    print("B")
    yield 2

g = gen()          # 아직 아무것도 출력되지 않음
print(next(g))     # A 출력 후 1
print(next(g))     # B 출력 후 2
# next(g)          # StopIteration
```

반복문 안에 `yield` 를 두면 값을 원하는 만큼 만들어 낼 수 있습니다.

```python
def squares(n):
    for i in range(1, n + 1):
        yield i * i

print(list(squares(3)))   # [1, 4, 9]
```

제너레이터 함수 안에서도 `try ... except` 를 쓸 수 있습니다(13차시). 문제가 생긴 항목만 건너뛰고 계속 내보내려면 `try` 를 for 문 안에 둡니다. `try` 로 for 문 전체를 감싸면 처음 예외가 난 곳에서 반복이 끝납니다.

```python
def shares(nums):
    for n in nums:
        try:
            yield 10 // n
        except ZeroDivisionError:
            pass                  # 0 은 건너뛰고 다음 수로

print(list(shares([5, 0, 2])))    # [2, 5]
```

파일을 한 줄씩 내보내는 제너레이터(강의 연습 문제)도 같은 구조입니다. `with open(...)` 블록 안에서 줄을 하나씩 돌며 `yield` 하고, 줄 끝의 `\n` 은 `strip()` 으로 뗍니다(12차시).

## 6. 제너레이터 표현식과 컴프리헨션

괄호 모양이 결과의 자료형을 결정합니다.

| 괄호 | 이름 | 결과 |
|---|---|---|
| `[ ]` | 리스트 컴프리헨션 | 리스트. 값이 그 줄에서 전부 만들어짐 |
| `{ 키: 값 }` | 딕셔너리 컴프리헨션 | 딕셔너리 |
| `( )` | 제너레이터 표현식 | 제너레이터. 값은 `next()` 때 하나씩 만들어짐 |

문법은 `[표현식 for 변수 in 이터러블 if 조건]` 이고, `if 조건` 은 생략할 수 있습니다(조건이 참인 것만 포함).

```python
nums = [1, 2, 3, 4]
print([x * x for x in nums])              # [1, 4, 9, 16]
print([x for x in nums if x % 2 == 0])    # [2, 4]
print({x: x * x for x in nums if x > 2})  # {3: 9, 4: 16}
g = (x * x for x in nums)                 # 제너레이터 객체
print(type(g))                            # <class 'generator'>
print(next(g))                            # 1
```

`yield` 함수로 만든 제너레이터와 `( )` 표현식으로 만든 제너레이터는 `type` 이 똑같이 `<class 'generator'>` 로 출력되고, `next()` 와 for 문에서도 같은 방식으로 값을 내놓습니다.

제너레이터 표현식 한 줄을 이터레이터 클래스로 옮겨 적을 수도 있습니다. 아래 클래스는 `(i * i for i in range(1, 4))` 와 같은 값을 냅니다. `range(1, 4)` 가 4 를 포함하지 않으므로 클래스의 끝 조건은 `>= 4` 입니다.

```python
class SquareIter:
    def __init__(self):
        self.i = 1

    def __iter__(self):
        return self

    def __next__(self):
        if self.i >= 4:
            raise StopIteration
        value = self.i * self.i
        self.i += 1
        return value

print(list(SquareIter()))                    # [1, 4, 9]
print(list(i * i for i in range(1, 4)))      # [1, 4, 9]
```

## 7. 느긋한 계산(lazy evaluation)

```python
def job(n):
    print("job", n)
    return n

a = [job(i) for i in range(3)]   # job 0, job 1, job 2 출력
b = (job(i) for i in range(3))   # 아무것도 출력되지 않음
print(next(b))                   # job 0 출력 후 0
for v in b:
    print(v)                     # job 1, 1, job 2, 2 순서로 출력
```

- 리스트 컴프리헨션은 만드는 순간 전부 실행하고, 제너레이터는 값이 필요할 때 하나씩 실행합니다.
- 제너레이터를 for 문으로 돌면 값 하나를 꺼낼 때마다 그 값을 만드는 계산만 실행됩니다. 계산 안의 `print` 와 for 문 안의 `print` 가 번갈아 출력됩니다.
- 오래 걸리는 작업이나 큰 데이터는 제너레이터가 유리합니다.
- 간단한 이터레이터는 제너레이터로, 복잡한 동작이 필요하면 클래스로 만듭니다.

## 시험에서 헷갈리기 쉬운 포인트

- `next(리스트)` 는 `TypeError` 입니다. 리스트는 이터러블이지 이터레이터가 아니므로, `it = iter(리스트)` 로 바꾼 뒤에야 `next(it)` 가 됩니다.
- `iter(리스트)` 는 부를 때마다 새 이터레이터를 만들고, `iter(이터레이터)` 는 같은 객체를 돌려줍니다. `a = iter(nums)` 뒤의 `c = iter(a)` 는 복사본이 아니어서 `next(c)` 가 `a` 의 위치를 함께 옮깁니다.
- `StopIteration` 은 값이 다 떨어졌다는 신호입니다. for 문은 이 신호를 받아 오류 없이 멈추지만, 직접 `next()` 를 부르면 예외로 나타납니다.
- `try` 블록 안에서 부른 `next()` 가 `StopIteration` 을 일으키면 블록의 남은 줄은 실행되지 않고 `except StopIteration` 으로 넘어갑니다. `finally` 가 있으면 그 뒤에 실행됩니다.
- 이터레이터는 처음으로 되돌릴 수 없습니다. `next()` 로 하나 꺼낸 뒤 for 문을 돌리면 그 다음 값부터 나오고, 끝까지 읽은 이터레이터로 다시 for 문을 돌리면 아무것도 출력되지 않습니다.
- 제너레이터 함수 호출은 실행이 아니라 객체 생성입니다. 본문 첫 줄의 `print` 는 첫 `next()` 때 비로소 실행됩니다.
- `yield` 뒤의 코드는 다음 `next()` 때 실행됩니다. 마지막 `yield` 뒤의 코드는 `StopIteration` 이 나는 `next()` 에서 실행되므로, `next()` 를 `yield` 개수만큼만 부르면 그 부분은 실행되지 않습니다.
- 괄호가 자료형을 정합니다. `[...]` 는 리스트, `{키: 값 ...}` 는 딕셔너리, `(...)` 는 제너레이터이며, `( )` 라고 튜플이 되지 않습니다.
- `type(iter([1]))` 은 `<class 'list_iterator'>`, `type(gen())` 은 `<class 'generator'>` 입니다. 둘 다 이터레이터지만, 제너레이터는 `yield` 함수나 `( )` 표현식으로 만든 것만을 가리킵니다.
- `__iter__` 가 `self` 를 돌려주는데 `__next__` 가 없으면 for 문에서 `TypeError` 가 납니다. 두 메서드는 함께 구현하고, 이름은 밑줄 두 개씩 앞뒤로 붙입니다.
- `__next__` 에서 `raise StopIteration` 을 빼먹으면 끝나지 않거나(무한 반복) 다른 오류(IndexError 등)로 멈춥니다. 끝 조건 → `raise` → 값 계산 → `return` 순서로 씁니다.
- 클래스의 끝 조건과 `range` 의 끝값을 맞춰 볼 때는 등호를 확인합니다. `if self.n > 5: raise StopIteration` 은 5 까지 돌려주므로 `range(..., 6)` 과 짝이 됩니다.
- 컴프리헨션의 `range` 경계를 확인하세요. `range(1, 4)` 는 1, 2, 3 이고 `range(7)` 은 0 부터 시작하므로 `[x for x in range(7) if x % 2 == 0]` 에는 0 이 들어갑니다.
- 딕셔너리 컴프리헨션의 출력은 넣은 순서대로, `{3: 0, 8: 2}` 처럼 키 뒤에 콜론과 공백 한 칸입니다. 리스트 출력에서 문자열 원소는 작은따옴표로 나옵니다.
