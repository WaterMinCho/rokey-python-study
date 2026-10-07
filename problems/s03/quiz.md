# 3차시 퀴즈 — 조건식과 제어문

> 코드를 실행하지 말고 눈으로 풀어 보세요. 답은 `submissions/<내 ID>/s03/quiz.py` 에 적습니다.

## Q1 (단답 · 3점)

비교 연산의 결과처럼 `True` 또는 `False` 값만 갖는 자료형이 있습니다.
다음 코드를 실행하면 `<class '____'>` 형태로 출력되는데, 빈칸에 들어갈 자료형 이름을 적으세요.

```python
print(type(3 > 1))
```

## Q2 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요. (여러 줄이면 `"""` 로 감싸서 줄을 나눠 적습니다)

```python
a = 30
b = 45
print(a == b)
print(a != b)
print(a >= 30)
print(b < 45)
print("Robot" == "robot")
```

## Q3 (객관식 · 2점)

다음 중 출력 결과가 나머지 셋과 **다른** 하나는?

1. `print(True and False)`
2. `print(False or False)`
3. `print(not True)`
4. `print(False or True)`

## Q4 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
x = 8
print(x > 5 and x < 8)
print(x > 5 or x < 8)
print(not x == 8)
print(not (x < 3 or x > 10))
```

## Q5 (객관식 · 2점)

한 식에 여러 종류의 연산자가 섞여 있을 때, **먼저 계산되는 것부터** 바르게 나열한 것은?

1. 괄호 → 산술 연산자 → 비교 연산자 → 논리 연산자
2. 괄호 → 비교 연산자 → 산술 연산자 → 논리 연산자
3. 논리 연산자 → 비교 연산자 → 산술 연산자 → 괄호
4. 괄호 → 논리 연산자 → 비교 연산자 → 산술 연산자

## Q6 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
n = 9
print(3 * (2 - 6))
print(3 * 2 - 6)
print(n + 1 > 5 * 2)
print(n % 3 == 0 and n // 2 == 4)
```

## Q7 (객관식 · 2점)

제어문과 조건문에 대한 설명으로 **옳지 않은** 것은?

1. 프로그램은 기본적으로 위에서 아래로 차례대로 실행되고, 제어문은 이 흐름을 바꾼다.
2. 제어문에는 조건문과 반복문이 있다.
3. `else` 뒤에도 `elif` 처럼 조건식을 적어야 한다.
4. `elif` 와 `else` 는 `if` 없이 단독으로 쓸 수 없다.

## Q8 (객관식 · 2점)

`score = 85` 가 먼저 실행되었다고 할 때, 아래 (가)~(라) 중 **오류 없이** 실행되어 `통과` 를 출력하는 코드는?

(가)

```python
if score >= 80
    print("통과")
```

(나)

```python
if score = 85:
    print("통과")
```

(다)

```python
if score >= 80:
    print("통과")
```

(라)

```python
if score >= 80:
print("통과")
```

1. (가)
2. (나)
3. (다)
4. (라)

## Q9 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
n = 18
if n % 4 == 0:
    print(n, "4의 배수")
else:
    print(n, "4의 배수 아님")
    print("나머지", n % 4)
print("검사 끝")
```

## Q10 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
battery = 20
if battery >= 60:
    print("여유")
elif battery < 60 and battery >= 20:
    print("주의")
else:
    print("충전 필요")
print("점검 완료")
```

## Q11 (단답 · 3점)

다음 프로그램이 `중` 을 출력하게 만드는 정수 입력값 중 **가장 큰 값**을 적으세요.

```python
x = int(input())
if x > 50:
    print("상")
elif x > 20:
    print("중")
else:
    print("하")
```

## Q12 (객관식 · 2점)

다음 코드를 실행했을 때의 결과로 알맞은 것은?

```python
n = 15
if n > 5:
    print("A")
if n > 10:
    print("B")
elif n > 12:
    print("C")
else:
    print("D")
```

1. `A` 만 출력된다
2. `A`, `B` 가 차례로 출력된다
3. `A`, `B`, `C` 가 차례로 출력된다
4. `A`, `C` 가 차례로 출력된다

## Q13 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
if 5 > 2:
    if 3 == 4:
        print("가")
        print("나")
    else:
        print("다")
    print("라")
else:
    print("마")
print("바")
```

## Q14 (객관식 · 2점)

다음 프로그램을 실행하고 키보드로 `20` 을 입력했습니다. 결과로 알맞은 것은?

```python
age = input()
if age >= 20:
    print("성인")
else:
    print("미성년")
```

1. `성인` 이 출력된다
2. `미성년` 이 출력된다
3. 아무것도 출력되지 않는다
4. 오류가 발생한다

## Q15 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
temp = 38
if temp >= 20:
    print("따뜻함")
elif temp >= 30:
    print("더움")
else:
    print("추움")
print("측정 끝")
```

## Q16 (객관식 · 2점)

다음 코드를 실행했을 때의 결과로 알맞은 것은?

```python
n = 7
if n > 10:
    print("크다")
elif n < 5:
    print("작다")
print("확인")
```

1. `크다` 가 출력된다
2. `작다` 가 출력된다
3. `확인` 만 출력된다
4. 아무것도 출력되지 않는다
