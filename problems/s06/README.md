# 6차시 · 함수(1)

함수를 정의하고 호출하는 법, 매개변수와 인수, `return`, 함수가 실행되는 순서를 다룹니다.
"이 코드의 출력은?", "이 함수의 반환값은?" 같은 문제가 이 차시의 문법으로 만들어지므로, 호출이 일어날 때마다 어느 줄이 실행되는지 눈으로 따라가며 읽습니다.

## 1. 함수란 무엇이고 왜 쓰나

함수는 자주 쓰는 코드를 한데 묶어 이름을 붙인 것입니다. 이름을 부르면(호출하면) 묶어 둔 코드가 실행됩니다.

| 함수를 쓰는 목적 | 뜻 |
|---|---|
| 모듈성(재사용성) | 한 번 정의하면 프로그램 여러 곳에서 불러 다시 쓸 수 있다 |
| 가독성 | 기능 단위로 나뉘어 있어, 코드가 무슨 일을 하는지 읽기 쉽다 |
| 유지보수성 | 고칠 일이 생기면 함수 정의 한 곳만 고치면 호출하는 모든 곳에 반영된다 |
| 추상성 | 안에서 어떻게 처리하는지 다 몰라도 이름만 불러 쓸 수 있다 |

| 함수의 종류 | 설명 |
|---|---|
| 내장 함수 | 파이썬에 처음부터 들어 있어 정의 없이 바로 호출한다. `print()`, `input()`, `len()`, `range()` |
| 모듈의 함수 | 비슷한 함수끼리 모아 둔 파일(모듈)에 들어 있는 함수 |
| 사용자 정의 함수 | `def` 로 직접 만들어 쓰는 함수 |

## 2. 정의와 호출

```python
def say_hi():          # 정의: def 함수이름(매개변수):
    print("안녕!")     # 함수의 코드블록(들여쓰기)

say_hi()               # 호출
say_hi()               # 다시 호출
```

- `def` 줄은 함수를 등록만 합니다. 코드블록은 호출할 때마다 실행되고, 한 번도 호출하지 않으면 한 번도 실행되지 않습니다.
- 매개변수는 선택이지만 괄호와 콜론은 생략할 수 없습니다. `def say_hi:` 와 `def say_hi()` 는 문법 오류입니다.
- 호출에도 괄호가 필요합니다. `say_hi` 처럼 이름만 적은 줄은 오류 없이 지나가고 함수는 실행되지 않습니다.

## 3. 매개변수와 인수

```python
def show_sum(left, right):         # left, right 는 매개변수(parameter)
    result = left + right
    print(left, "+", right, "=", result)

x = 7
show_sum(x, 5)                     # x, 5 는 인수(argument)
# 출력: 7 + 5 = 12
```

- 정의의 괄호 안에 적은 이름이 매개변수이고, 호출의 괄호 안에 넣어 보내는 값이 인수입니다.
- 호출하면 인수가 왼쪽부터 순서대로 매개변수에 대입됩니다(`left = x`, `right = 5`). 인수 하나가 매개변수 하나에 대응합니다.
- 인수가 3개면 매개변수도 3개가 필요하고 쉼표로 구분합니다. 개수가 맞지 않으면 오류(TypeError)가 납니다.
- 인수로 넘기는 변수 이름(`x`)과 매개변수 이름(`left`)은 달라도 됩니다. 값만 전달됩니다.
- 매개변수가 없는 함수를 호출할 때는 인수를 넣을 수 없습니다. 그래도 괄호는 써야 합니다.

## 4. return: 결과를 돌려주고 함수를 끝낸다

```python
def area(w, h):
    return w * h           # 결과를 호출한 자리로 돌려준다

size = area(4, 6)          # 반환값 24 가 size 에 저장된다
print(size)                # 24
print(area(2, 3) + 1)      # 7
```

- `return` 은 값을 호출한 쪽으로 돌려줍니다. 호출한 쪽에서는 그 값을 변수에 담거나 식에 씁니다.
  `size = area(4, 6)` 에서 반환값은 `=` 오른쪽 값(r_value)이 되어, 왼쪽 변수(l_value) `size` 에 저장됩니다.
- `return` 이 실행되면 함수가 끝납니다. `return` 아래에 남은 함수 코드는 실행되지 않습니다.

```python
def size_of(n):
    if n >= 100:
        return "large"
    elif n >= 10:
        return "medium"
    # n < 10 이면 return 없이 함수가 끝난다

print(size_of(250))    # large
print(size_of(3))      # None
```

- `return` 을 만나지 못하고 끝난 호출의 결과는 `None` 입니다. `return` 문이 아예 없는 함수(출력만 하는 함수)도 호출 결과가 `None` 입니다.

### 반복문 안의 return

```python
def first_even(nums):
    for n in nums:
        if n % 2 == 0:
            return n       # 여기서 함수가 끝난다. 뒤의 값은 꺼내지 않는다
    return -1              # 끝까지 돌아도 짝수가 없을 때만 실행된다

print(first_even([7, 4, 10]))   # 4
print(first_even([7, 9]))       # -1
```

- `break` 는 반복문만 끝내고 그 아래 코드로 넘어가지만, `return` 은 반복문 안에 있어도 함수 전체를 끝냅니다.
- "없으면 -1" 을 돌려주는 `return` 은 `for` 와 같은 들여쓰기 깊이에 둡니다. `if` 에 `else: return -1` 로 붙이면 첫 번째 값만 보고 함수가 끝납니다.

### 조건식을 반환하는 함수와 함수 안에서의 호출

```python
def is_adult(age):
    return age >= 19             # 조건식의 결과 True / False 를 돌려준다

def count_adults(ages):
    count = 0
    for a in ages:
        if is_adult(a):          # 돌려받은 True / False 를 if 의 조건으로 쓴다
            count += 1
    return count

print(count_adults([15, 19, 30]))   # 2
```

함수 안에서 다른 함수를 호출하고 그 반환값을 바로 쓸 수 있습니다. `count_adults` 는 값마다 `is_adult` 를 호출해 `True` 가 나온 횟수를 셉니다.

## 5. 함수 안에서 만든 변수는 함수가 끝나면 사라진다

```python
def double(n):
    twice = n * 2      # 함수 안에서만 존재하는 변수

double(8)
print(twice)           # NameError: name 'twice' is not defined
```

함수가 끝나면 그 안의 변수(매개변수 포함)는 사라집니다. 결과를 밖에서 쓰려면 사라지기 전에 `return` 으로 돌려주고,
호출한 쪽에서 변수로 받아야 합니다.

```python
def double(n):
    twice = n * 2
    return twice

answer = double(8)     # 돌려받은 값을 answer 에 저장
print(answer)          # 16
```

## 6. 호출 순서

파이썬은 위에서 아래로 실행합니다. 함수는 호출하는 줄이 실행되기 전에 정의되어 있어야 합니다.

```python
ring()                 # NameError: name 'ring' is not defined
def ring():
    print("따르릉")
```

함수 안에서 다른 함수를 호출하면, 호출된 함수가 끝난 뒤 호출한 자리의 다음 줄로 돌아옵니다.

```python
def inner():
    print("inner")

def outer():
    print("outer 시작")
    inner()            # inner 를 실행하고 이 자리로 돌아온다
    print("outer 끝")

outer()
# outer 시작
# inner
# outer 끝
```

위 코드에서 `def outer` 를 `def inner` 보다 먼저 적어도 결과가 같습니다. `outer` 안의 `inner()` 줄은 `outer()` 가 호출될 때 실행되고,
그 시점에는 두 함수가 모두 정의되어 있기 때문입니다. `outer()` 호출 줄을 `def inner` 보다 위로 옮기면 `outer 시작` 을 출력한 뒤 `NameError` 가 납니다.

## 7. 과제에 나온 형태

값 여러 개를 돌려줄 때는 `return a, b` 처럼 쉼표로 나열합니다. 나열한 값은 튜플 하나로 묶여 반환되고, 받은 쪽에서 인덱스로 꺼냅니다.

```python
def calc(a, b):
    return a + b, a - b

result = calc(7, 3)
print(result)          # (10, 4)
print(result[0])       # 10
```

정의에서 `count=1` 처럼 매개변수에 값을 정해 두면, 호출할 때 그 인수를 생략할 수 있습니다(기본값이 있는 매개변수, 7차시에서 자세히 다룹니다).

```python
def pay(price, count=1):
    return price * count

print(pay(300))        # 300  (count 는 기본값 1)
print(pay(300, 4))     # 1200
```

## 시험에서 헷갈리기 쉬운 포인트

- `print` 는 화면에 보여 주기만 하고 값을 돌려주지 않습니다. 출력만 하는 함수를 `x = f()` 로 받으면 `x` 는 `None` 이고,
  `print(f())` 는 함수 안의 출력 뒤에 `None` 을 한 줄 더 출력합니다.
- `return` 을 만나면 즉시 끝납니다. `return` 아래에 `print` 가 있어도 실행되지 않습니다.
- `if`/`elif` 안에만 `return` 이 있고 `else` 가 없으면, 어느 조건에도 맞지 않는 인수에서 `None` 이 반환됩니다.
- 반복문 안의 `return` 은 반복이 남아 있어도 함수를 끝냅니다. `return` 이 `if` 안에 있는지, `for` 안에 있는지, `for` 밖에 있는지 들여쓰기로 확인하세요.
- 정의 전에 호출하면 `NameError` 입니다. 다만 그 줄에 도달하기 전에 실행된 `print` 는 이미 출력된 상태입니다.
- 정의된 순서가 아니라 호출 줄이 실행되는 시점을 봅니다. 함수 안에서 부르는 다른 함수는 그 호출이 실행되기 전에만 정의되어 있으면 됩니다.
- 함수 안의 변수를 밖에서 쓰면 `None` 이 출력되는 것이 아니라 `NameError` 가 납니다.
- 정의에도 호출에도 괄호가 필요합니다. `say_hi` 처럼 이름만 적으면 호출되지 않고, 오류도 나지 않아 알아채기 어렵습니다.
- 인수는 순서대로 대입됩니다. `f(b, c, a)` 로 호출하면 첫째 매개변수에 `b` 의 값이 들어갑니다. 변수 이름이 아니라 위치를 보세요.
- `print(a, b)` 의 쉼표는 공백 한 칸을 넣습니다. `print(name, "님")` 은 `민수 님` 이고, `print(name + "님")` 은 `민수님` 입니다.
- 함수 안에서 함수를 호출하면 호출 줄 위의 출력, 호출된 함수의 출력, 호출 줄 아래의 출력 순서로 나옵니다.
- `return a, b` 는 튜플이라 출력하면 괄호가 붙습니다: `(10, 4)`.
- `/` 의 결과는 항상 실수입니다. 나눗셈 함수가 `20 / 5` 를 반환하면 `4` 가 아니라 `4.0` 입니다.
- 나누는 수가 0 이면 `ZeroDivisionError` 가 납니다. 평균이나 나눗셈을 반환하는 함수는 나누기 전에 `if` 로 0 인지 확인하고, 0 일 때 돌려줄 값을 먼저 `return` 합니다.
