# 13차시 · 예외 처리·문자열·람다·map

네 가지 주제가 한 차시에 들어 있어 시험 범위가 넓은 단원입니다. 예외 처리는 코드 흐름을 손으로 따라가는 출력 문제,
문자열은 인덱스·슬라이싱·메서드의 결과를 정확히 적는 문제, 람다·map 은 한 줄 코드를 읽고 결과를 쓰는 문제로 나오기 좋습니다.

## 1. 에러와 예외

| | 문법 에러(SyntaxError) | 예외(Exception) |
|---|---|---|
| 원인 | 파이썬 문법에 맞지 않게 씀 (콜론 빠짐 등) | 문법은 맞지만 **실행 중에** 문제가 생김 |
| 언제 | 프로그램을 실행하기 전에 걸림 | 그 줄이 실행되는 순간 발생 |
| 대처 | 코드를 고쳐야 함 | `try ... except` 로 처리하면 프로그램을 계속 실행할 수 있음 |

자주 나오는 예외는 코드만 보고 이름을 고를 수 있어야 합니다.

| 예외 | 언제 나는가 | 예 |
|---|---|---|
| `ZeroDivisionError` | 0 으로 나눔 | `7 / 0`, `7 // 0`, `7 % 0` |
| `ValueError` | 자료형은 맞지만 값이 변환 불가 | `int("abc")`, `int("3.5")`, `float("")` |
| `TypeError` | 자료형이 맞지 않는 연산 | `"5" + 5`, `"abc"[0] = "A"` |
| `NameError` | 정의하지 않은 이름 사용 | `print(total)` (total 을 만든 적 없음) |
| `IndexError` | 리스트·문자열 범위를 벗어난 인덱스 | `[1, 2, 3][5]` |
| `KeyError` | 딕셔너리에 없는 키 | `{"a": 1}["b"]` |

## 2. try / except / finally 의 흐름

```python
try:
    n = int(input())        # ① 문제가 생길 수 있는 코드
    print("두 배:", n * 2)   # ②
except ValueError:          # ③ ① 에서 ValueError 가 나면 여기로
    print("정수가 아닙니다")
finally:                    # ④ 예외가 났든 안 났든 마지막에 반드시 실행
    print("끝")
```

- 예외가 **안 나면**: ① → ② → ④ (except 는 건너뜀)
- 예외가 **나면**: ① 에서 멈추고 ② 는 실행되지 않음 → ③ → ④
- 예외가 났는데 **이름이 맞는 except 가 없으면**: ④ 는 실행된 뒤 프로그램이 오류로 중단됨
- `finally` 는 선택 사항이지만, 적으면 예외 발생 여부와 상관없이 항상 실행됩니다.
- 함수 안에서 `return` 을 만나도 `finally` 가 **먼저** 실행된 뒤 값이 반환됩니다.
- `try` 문이 끝난 뒤의 코드는 예외가 났든 안 났든(잡혔다면) 그대로 이어서 실행됩니다. 예외가 난 쪽만 `except` 를 거쳐 갈 뿐입니다.

## 3. except 를 여러 개 쓰기

```python
try:
    print(21 // int(text))
except ValueError:                 # 변환 실패
    print("값 오류")
except ZeroDivisionError:          # 0 으로 나눔
    print("0 오류")
```

- except 절은 위에서부터 차례로 검사하고, 맞는 것 **하나만** 실행됩니다.
- 여러 예외를 같은 방법으로 처리하려면 **괄호로 묶은 튜플**로 적습니다: `except (ValueError, ZeroDivisionError):`
- `except Exception as e:` 처럼 `as 변수` 를 붙이면 예외 안에 담긴 메시지를 꺼낼 수 있습니다. `print(e)` 는 **메시지만** 출력합니다(예외 이름은 붙지 않음).

```python
try:
    int("abc")
except Exception as e:
    print(e)        # invalid literal for int() with base 10: 'abc'
```

## 4. 예외 클래스

- `BaseException`: 모든 예외의 공통 조상입니다.
- `Exception`: 프로그램 실행 중 생기는 보통의 예외들의 부모 클래스입니다. `except Exception:` 은 시스템 종료 같은 특수한 예외를 뺀 거의 모든 예외를 잡습니다.
- 그래도 강의는 **예외 이름을 구체적으로 적을 것**을 권장합니다. 범위가 넓은 `Exception` 은 맨 **아래** except 절에 둡니다.
- 사용자 정의 예외를 만들 때는 `Exception` 을 상속합니다: `class MyError(Exception): pass`

## 5. raise 로 예외를 일부러 일으키기

```python
def check_age(age):
    if age < 0:
        raise ValueError("나이는 0 이상이어야 합니다")
    return age

try:
    check_age(-3)
except ValueError as e:
    print("오류:", e)      # 오류: 나이는 0 이상이어야 합니다
```

- `raise 예외클래스("메시지")` 형태입니다. `raise` 가 실행되면 그 아래 줄은 실행되지 않고 가장 가까운 `try` 의 except 로 건너뜁니다.
- 잡아 주는 except 가 없으면 Traceback 과 함께 프로그램이 중단됩니다.
- 함수 안에서 발생한 예외(`raise` 든 `int()` 실패든)는 그 함수에 `except` 가 없으면 **호출한 쪽**으로 전파됩니다. 호출한 쪽의 `try` 가 잡을 수 있습니다. 중간에 `finally` 만 있는 함수라면 `finally` 를 실행한 뒤 계속 전파됩니다.
- 이름이 맞지 않는 `except` 는 잡지 못합니다. `except ValueError:` 는 `TypeError` 를 지나쳐 보냅니다.

## 6. 문자열의 성질

```python
s = "robot"
print(s[0], s[-1])     # r t
print(len(s))          # 5
print(type(s))         # <class 'str'>
s[0] = "R"             # TypeError: 문자열은 바꿀 수 없음(불변)
```

- 문자열은 **인덱스와 길이**를 가지지만 일부 글자를 **바꿀 수는 없습니다**. 바꾸려면 새 문자열을 만들어야 합니다.
- `["python"]` 은 요소가 **하나**인 리스트이고, `["p", "y", "t"]` 는 글자 리스트입니다. `len("python")` 은 6, `len(["python"])` 은 1 이며 `["python"][0]` 은 문자열 전체 `"python"` 입니다. 리스트는 `lst[0] = "k"` 처럼 바꿀 수 있습니다.
- `for ch in s:` 로 글자를 하나씩 꺼낼 수 있고, `for i in range(len(s)): s[i]` 처럼 인덱스로 돌 수도 있습니다.
- 문자 ↔ 숫자: `ord("a")` → `97`, `chr(97)` → `"a"`. 컴퓨터는 글자를 숫자(아스키 코드·유니코드)로 저장합니다. `chr(ord("A") + 1)` 은 `"B"` 입니다.
- 알파벳의 코드는 순서대로 1씩 커집니다(`A` 65 ~ `Z` 90, `a` 97 ~ `z` 122). `ord(ch) - ord("a")` 는 소문자 `ch` 가 알파벳에서 몇 번째인지(a 는 0, z 는 25)를 알려 줍니다.

일부 글자만 바꾼 문자열이 필요하면 조각을 꺼내 `+` 로 이어 새 문자열을 만듭니다.

```python
s = "python"
masked = s[0] + "*" * (len(s) - 2) + s[-1]    # p****n  (첫 글자 + 별 4개 + 마지막 글자)

shifted = ""
for ch in "xyz":                               # 글자를 하나씩 바꿔 가며 뒤에 붙이기
    order = (ord(ch) - ord("a") + 3) % 26      # z 를 넘으면 a 로 돌아가도록 26 으로 나눈 나머지
    shifted = shifted + chr(ord("a") + order)
print(masked, shifted)                         # p****n abc
```

## 7. 문자열 출력 세 가지

```python
na = 20
nb = 5
print("na 값", na, "더하기", nb, "은", na + nb)          # 쉼표: 사이에 공백 한 칸
print("na 값 %d 더하기 %d 은 %d" % (na, nb, na + nb))    # 형식지정자: %d 정수 %s 문자열 %f 실수
print(f"na 값 {na} 더하기 {nb} 은 {na + nb}")           # f-string: 중괄호 안에 변수나 식
```

- 쉼표 방식은 값 사이에 **자동으로 공백 한 칸**이 들어갑니다. `+` 로 이으면 공백이 들어가지 않고, 숫자는 `str()` 로 바꿔야 합니다.
- `%` 방식은 값이 여러 개면 `% (a, b)` 처럼 **튜플**로 넘깁니다. `%s` 자리에는 문자열, `%d` 자리에는 정수, `%f` 자리에는 실수가 순서대로 들어갑니다.
- `%f` 는 소수점 아래 6자리까지 채워서 보여 줍니다: `"%s %d %f" % ("a", 3, 1.5)` → `a 3 1.500000`
- f-string 은 따옴표 앞에 `f` 를 붙이고 `{}` 안에 변수뿐 아니라 `{a + b}`, `{len(s)}` 같은 식도 쓸 수 있습니다.

## 8. 인덱싱과 슬라이싱

```python
s = "programming"     # p r o g r a m m i n g
#     인덱스           0 1 2 3 4 5 6 7 8 9 10
#     음수 인덱스     -11 ... -3 -2 -1
print(s[0], s[-1])    # p g
print(s[3:7])         # gram   (3 부터 7 '앞'까지 → 3, 4, 5, 6)
print(s[:4])          # prog   (처음부터 4 앞까지)
print(s[7:])          # ming   (7 부터 끝까지)
print(s[2:-1])        # ogrammin (2 부터 마지막 글자 '앞'까지)
print(s[:])           # programming (전체 복사)
```

- 슬라이싱 `[시작:끝]` 은 **시작 포함, 끝 미포함**입니다. 글자 수는 `끝 - 시작` 입니다.
- 끝 인덱스가 음수이면 "그 위치의 글자 바로 앞까지"입니다. `s[2:-1]` 은 인덱스 2 부터 마지막 글자 앞까지 잘라 냅니다.
- 문자열·리스트·튜플 모두 같은 규칙입니다.

## 9. 문자열 메서드 split · strip · join

```python
text = "  rokey bootcamp python  "
words = text.strip().split()       # strip: 양끝 공백 제거 → split: 공백 기준으로 나눔
print(words)                       # ['rokey', 'bootcamp', 'python']
print("-".join(words))             # rokey-bootcamp-python
print("".join(words))              # rokeybootcamppython
print("2026-10-16".split("-"))     # ['2026', '10', '16']
```

| 메서드 | 하는 일 | 결과 자료형 |
|---|---|---|
| `s.split()` | 공백 기준으로 나눔. `s.split(",")` 처럼 구분자 지정 가능 | 리스트 |
| `s.strip()` | **양 끝**의 공백(띄어쓰기·탭·줄바꿈) 제거. 가운데 공백은 남음 | 문자열 |
| `"구분자".join(리스트)` | 리스트의 문자열들을 구분자로 이어 붙임. 구분자가 `""` 이면 그냥 붙임 | 문자열 |

- `split` 과 `strip` 은 **새 값을 반환**할 뿐 원래 문자열은 바뀌지 않습니다. 결과를 변수에 받아야 합니다.
- `join` 은 **구분자 문자열이 호출**합니다. `리스트.join("-")` 은 오류입니다. 리스트 안에 숫자가 있어도 오류입니다(문자열만 가능).
- `split()` 은 연속된 공백을 하나로 보고 빈 문자열을 만들지 않습니다. `"  a   b ".split()` → `['a', 'b']`
- `split(",")` 처럼 구분자를 주면 그 문자만 사라지고 조각 양옆의 공백은 남습니다. `" kim, lee ".split(",")` → `[' kim', ' lee ']`. 조각마다 `strip()` 을 적용하려면 `list(map(lambda s: s.strip(), 조각들))` 로 씁니다.
- 숫자 리스트를 이어 붙일 때는 문자열로 먼저 바꿉니다: `"-".join(map(str, [98, 97, 100]))` → `'98-97-100'`

## 10. 람다(lambda) 함수

```python
def square(x):          # 보통 함수
    return x ** 2

square = lambda x: x ** 2        # 같은 일을 하는 람다
add = lambda a, b: a + b         # 매개변수 여러 개는 쉼표로
print(square(3), add(2, 5))      # 9 7
```

- `lambda 매개변수: 표현식` 은 이름이 없는 **익명 함수**를 한 줄로 만듭니다. `def`, `return` 을 쓰지 않습니다.
- 콜론 뒤에는 **식 하나**만 올 수 있습니다. `return`, `if` 문, 여러 줄은 쓸 수 없습니다. 식의 값이 곧 반환값입니다.
- 변수에 넣어 `square(3)` 처럼 부르거나, `map()` 의 인수로 바로 넘깁니다.

## 11. map() 함수

```python
nums = [1, 2, 3, 4]
result = map(lambda x: x * 10, nums)   # 각 요소에 함수를 적용한 '이터레이터'
print(list(result))                    # [10, 20, 30, 40]   ← list() 로 바꿔야 값이 보임
print(nums)                            # [1, 2, 3, 4]       ← 원본은 그대로
```

- `map(함수, 반복가능객체)`: 요소 **하나하나**에 함수를 적용합니다. 함수 이름만 넘기고 괄호는 붙이지 않습니다(`map(square, nums)`, `map(square(), nums)` 아님).
- `map()` 의 결과를 그대로 `print` 하면 `<map object at 0x...>` 처럼 나옵니다. 값을 보려면 `list()` 로 감쌉니다.
- 입력 한 줄을 정수 리스트로 바꿀 때 자주 쓰는 코드: `nums = list(map(int, input().split()))`
- 첫 인수에는 `def` 로 만든 함수, 람다, `int`·`str`·`len`·`ord` 같은 내장 함수 이름을 모두 쓸 수 있습니다. 문자열도 반복 가능한 객체라 `list(map(ord, "bad"))` 는 글자마다 `ord` 를 적용한 `[98, 97, 100]` 입니다.

## 시험에서 헷갈리기 쉬운 포인트

- try 안에서 예외가 난 줄 아래는 실행되지 않습니다. `print("A")` → 오류 → `print("B")` 순서면 B 는 안 나오고 except 로 갑니다.
- finally 는 항상 실행됩니다. 예외가 안 나도, except 가 실행돼도, 심지어 잡히지 않는 예외가 나도 실행됩니다.
- `print(e)` 는 메시지만 찍습니다. `ValueError: ...` 처럼 이름이 앞에 붙지 않습니다.
- 여러 예외를 한 except 로 묶을 때는 괄호 튜플 `except (A, B):` 를 씁니다. 대괄호 `[A, B]` 는 오류이고, `A and B` / `A or B` 는 문법은 통과하지만 한 쪽만 잡는 엉뚱한 코드입니다.
- `int("3.5")` 는 ValueError 입니다. 소수점이 있는 문자열은 `float()` 로만 바꿀 수 있습니다.
- `[1, 2, 3][5]` 는 IndexError, `{"a": 1}["b"]` 는 KeyError 입니다. 리스트는 Index, 딕셔너리는 Key 로 구분합니다.
- 문자열은 불변이라 `s[0] = "R"` 은 TypeError 입니다. 리스트는 `lst[0] = "R"` 로 요소를 바꿀 수 있습니다.
- 슬라이싱 끝은 미포함입니다. `s[3:7]` 은 인덱스 3, 4, 5, 6 네 글자입니다.
- `a / b` 는 나누어떨어져도 실수입니다: `9 / 3` → `3.0`. 정수 몫은 `//` 로 구합니다.
- `"-".join(words)` 에서 join 을 부르는 쪽은 구분자입니다. `words.join("-")` 은 오류가 납니다.
- `strip()` 은 양 끝만 지웁니다. `"a b".strip()` 은 가운데 공백이 남아 `"a b"` 를 돌려줍니다.
- `map()` 결과는 `list()` 로 바꾸기 전까지 값이 보이지 않습니다. `print(map(...))` 은 `<map object ...>` 를 출력합니다.
- `lambda x: return x + 1` 은 문법 오류입니다. 람다에는 `return` 을 쓰지 않습니다.
- `list(map(int, ["1", "2"]))` 는 `[1, 2]` (정수), `list(map(str, [1, 2]))` 는 `['1', '2']` (문자열). 리스트를 출력하면 문자열은 작은따옴표로 표시됩니다.
- `raise` 뒤에 적은 메시지는 `except ... as e:` 의 `e` 에 들어갑니다. `raise` 가 실행되면 함수의 나머지 줄도, try 블록의 나머지 줄도 실행되지 않습니다.
- 음수 인덱스는 IndexError 가 아닙니다. 길이 3 인 리스트에서 `[3]` 은 IndexError 지만 `[-1]` 은 마지막 요소입니다. `[-4]` 부터 IndexError 가 납니다.
- `except` 블록 안의 `continue` 나 `return` 은 그 아래 줄을 건너뜁니다. 반복문 안의 try 에서 실패한 요소만 건너뛸 때 자주 쓰는 구조입니다.
- `"python"[0]` 은 `'p'`, `["python"][0]` 은 `'python'` 입니다. 따옴표만 있으면 문자열, 대괄호로 감싸면 요소 하나짜리 리스트입니다.
- `s[2:-1]` 은 인덱스 2 부터 마지막 글자 **앞**까지입니다. 마지막 글자는 들어가지 않습니다.
- `+` 로 문자열을 이으면 공백이 자동으로 들어가지 않습니다. `"3" + "대"` 는 `3대` 가 되고, `print(3, "대")` 는 `3 대` 를 출력합니다.
- `chr(ord("z") + 1)` 은 `a` 가 아니라 기호 `{` 입니다. `z` 다음을 `a` 로 돌리려면 `(순서 + k) % 26` 으로 직접 계산해야 합니다.
- 같은 `ValueError` 라도 원인이 둘(변환 실패·`raise`)이면 한 `except` 로는 구분할 수 없습니다. `try` 를 나누거나 순서를 조정해야 메시지가 갈립니다.
