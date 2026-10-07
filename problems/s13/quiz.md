# 13차시 퀴즈 — 예외 처리·문자열·람다·map

> 코드를 실행하지 말고 눈으로 풀어 보세요. 답은 `submissions/<내 ID>/s13/quiz.py` 에 적습니다.

## Q1 (객관식 · 2점)

에러와 예외에 대한 설명으로 옳지 **않은** 것은?

1. 문법 에러(SyntaxError)는 코드 작성 방법이 잘못된 것으로, 프로그램이 실행되기 전에 걸린다.
2. 예외는 문법에 문제가 없어도 프로그램을 실행하는 도중에 발생할 수 있다.
3. 예외 처리를 하면 예외가 발생해도 프로그램의 실행 상태를 유지할 수 있다.
4. `10 / 0` 처럼 0 으로 나누는 코드는 문법 에러이므로 `try` 문으로 처리할 수 없다.

## Q2 (객관식 · 2점)

코드와 그 코드를 실행했을 때 발생하는 예외의 연결이 옳지 **않은** 것은?

1. `int("삼")` → `ValueError`
2. `"5" + 5` → `TypeError`
3. `print(total)` (`total` 을 만든 적이 없음) → `NameError`
4. `[1, 2, 3][5]` → `KeyError`

## Q3 (객관식 · 2점)

`ValueError` 와 `ZeroDivisionError` 를 **하나의** `except` 절에서 **둘 다** 잡으려고 합니다. 올바른 코드는?

1. `except ValueError and ZeroDivisionError:`
2. `except (ValueError, ZeroDivisionError):`
3. `except [ValueError, ZeroDivisionError]:`
4. `except ValueError or ZeroDivisionError:`

## Q4 (객관식 · 2점)

다음 코드를 실행했을 때 출력되는 것은?

```python
try:
    raise ValueError("나이는 0 이상이어야 합니다")
except Exception as e:
    print(e)
```

1. `ValueError`
2. `나이는 0 이상이어야 합니다`
3. `ValueError: 나이는 0 이상이어야 합니다`
4. 아무것도 출력되지 않고 오류와 함께 프로그램이 중단된다

## Q5 (객관식 · 2점)

다음 코드를 실행했을 때의 결과로 옳은 것은?

```python
s = "robot"
s[0] = "R"
print(s)
```

1. `Robot`
2. `robot`
3. `['R', 'o', 'b', 'o', 't']`
4. 오류가 발생한다

## Q6 (객관식 · 2점)

`s = "programming"` 일 때, 설명이 옳지 **않은** 것은?

1. `s[-1]` 의 값은 `'g'` 이다.
2. `s[:4]` 의 값은 `'prog'` 이다.
3. `s[3:7]` 의 값은 `'gramm'` 이다.
4. `s[7:]` 의 값은 `'ming'` 이다.

## Q7 (객관식 · 2점)

실행했을 때 `[2, 4, 6]` 이 출력되는 코드는?

1. `print(map(lambda x: x * 2, [1, 2, 3]))`
2. `print(list(map(lambda x: x * 2, [1, 2, 3])))`
3. `print(list(map(lambda x: x + 2, [1, 2, 3])))`
4. `print(lambda x: x * 2, [1, 2, 3])`

## Q8 (객관식 · 2점)

람다(lambda) 함수에 대한 설명으로 옳지 **않은** 것은?

1. `def` 키워드를 쓰지 않고 함수를 만들 수 있으며, 이름이 없는 익명 함수라고 부른다.
2. `lambda x: x + 1` 처럼 `lambda 매개변수: 표현식` 형태로 쓴다.
3. 값을 돌려주려면 `lambda x: return x + 1` 처럼 반드시 `return` 을 써야 한다.
4. `f = lambda x: x + 1` 처럼 변수에 저장한 뒤 `f(3)` 으로 호출할 수 있다.

## Q9 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요. (여러 줄이면 `"""` 로 감싸서 줄을 나눠 적습니다)

```python
try:
    n = int("20")
    print("변환 성공:", n)
except ValueError:
    print("변환 실패")
finally:
    print("끝")
```

## Q10 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
data = ["7", "x", "0"]
for d in data:
    try:
        print(21 // int(d))
    except ValueError:
        print("값 오류")
    except ZeroDivisionError:
        print("0 오류")
print("완료")
```

## Q11 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
def divide(a, b):
    try:
        print("계산 시작")
        result = a / b
        print("결과:", result)
    except ZeroDivisionError:
        print("0으로 나눌 수 없습니다")
    finally:
        print("계산 종료")

divide(10, 4)
divide(3, 0)
```

## Q12 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
text = "  rokey bootcamp python  "
words = text.strip().split()
print(words)
print(len(words))
print("-".join(words))
print(words[1][0], words[-1][-1])
print(text.strip()[0:5])
```

## Q13 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
add = lambda a, b: a + b
nums = [3, 5, 8]
doubled = list(map(lambda x: x * 2, nums))
print(doubled)
print(add(doubled[0], doubled[-1]))
print("%d개 중 첫 번째는 %d" % (len(doubled), doubled[0]))
print(f"{nums[1]} + {nums[2]} = {add(nums[1], nums[2])}")
```

## Q14 (단답 · 3점)

다음 빈칸에 들어갈 **클래스 이름**을 적으세요.

`except ____ as e:` 처럼 쓰면 시스템 종료와 관련된 특수한 예외를 제외한, 프로그램 실행 중에 발생하는 거의 모든 예외를 한 번에 잡을 수 있습니다. 사용자 정의 예외 클래스를 만들 때 상속받는 기본 클래스이기도 합니다.

## Q15 (단답 · 3점)

`ord("A")` 의 값이 `65` 일 때, 다음 식의 값(문자)을 적으세요.

```python
chr(ord("A") + 2)
```

## Q16 (객관식 · 2점)

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

## Q17 (객관식 · 2점)

다음 코드를 실행했을 때 일어나는 일로 옳은 것은?

```python
def check(n):
    if n % 2 == 1:
        raise TypeError("홀수")
    return n // 2

try:
    print(check(8))
    print(check(5))
    print(check(4))
except ValueError as e:
    print("오류:", e)
finally:
    print("검사 끝")
```

1. `4`, `오류: 홀수`, `검사 끝` 이 차례로 출력되고 프로그램이 정상 종료된다.
2. `4`, `검사 끝` 이 차례로 출력된 뒤 `TypeError` 로 프로그램이 중단된다.
3. `4`, `2` 가 출력되고 `검사 끝` 은 출력되지 않는다.
4. `4`, `검사 끝`, `2` 가 차례로 출력된다.

## Q18 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
def withdraw(balance, amount):
    if amount > balance:
        raise ValueError("잔액 부족")
    print("출금 완료")
    return balance - amount

try:
    left = withdraw(5000, 3000)
    print("남은 돈:", left)
    left = withdraw(left, 4000)
    print("남은 돈:", left)
except ValueError as e:
    print("실패:", e)
print("끝")
```

## Q19 (출력 예측 · 3점)

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

## Q20 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
items = ["7", "seven", "70"]

def pick(i):
    try:
        return int(items[i]) // 2
    except IndexError:
        return "범위 밖"
    except ValueError:
        return "정수 아님"

print(pick(0))
print(pick(1))
print(pick(3))
print(pick(-1))
```

## Q21 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
def parse(text):
    try:
        n = int(text)
        print("변환:", n)
        return n
    finally:
        print("parse 종료")

try:
    total = parse("8") + parse("x")
    print("합계:", total)
except ValueError:
    print("정수가 아닙니다")
```
