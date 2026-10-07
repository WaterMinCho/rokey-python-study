# 15차시 퀴즈 — 고급 함수

> 코드를 실행하지 말고 눈으로 풀어 보세요. 답은 `submissions/<내 ID>/s15/quiz.py` 에 적습니다.

## Q1 (객관식 · 2점)

이터러블(iterable)과 이터레이터(iterator)에 대한 설명으로 옳지 **않은** 것은?

1. 이터러블은 `__iter__()` 메서드를 가지며, `iter()` 함수로 이터레이터를 얻을 수 있다.
2. 이터레이터는 `__next__()` 메서드를 가지며, `__iter__()` 는 자기 자신을 반환한다.
3. 리스트는 이터러블이지만 이터레이터는 아니다.
4. 이터레이터는 값을 끝까지 읽은 뒤에도 for 문을 다시 돌리면 처음부터 값을 다시 읽을 수 있다.

## Q2 (객관식 · 2점)

다음 코드를 실행했을 때의 결과로 옳은 것은?

```python
a = [10, 20, 30]
print(next(a))
```

1. `10`
2. `[10, 20, 30]`
3. 오류(`TypeError`)가 발생한다
4. 오류(`StopIteration`)가 발생한다

## Q3 (객관식 · 2점)

클래스로 이터레이터를 만드는 방법에 대한 설명으로 옳지 **않은** 것은?

1. `__iter__` 메서드는 보통 자기 자신(`self`)을 반환한다.
2. `__next__` 메서드는 for 문이 반복될 때나 `next()` 함수를 호출할 때 실행된다.
3. `__iter__` 만 구현하고 `__next__` 는 생략해도 for 문에서 정상적으로 값을 꺼낼 수 있다.
4. `__iter__` 와 `__next__` 는 `__init__` 처럼 파이썬에서 특별한 의미를 갖는 메서드이다.

## Q4 (객관식 · 2점)

제너레이터(generator)에 대한 설명으로 옳지 **않은** 것은?

1. 제너레이터는 이터레이터를 만들어 주는 함수로, 값을 돌려줄 때 `return` 대신 `yield` 를 쓴다.
2. 제너레이터 함수를 호출하면 함수 본문이 끝까지 실행되어 모든 값이 담긴 리스트가 반환된다.
3. `yield` 를 만나면 값을 돌려주고 현재 상태를 기억한 채 멈추었다가, 다음 `next()` 호출 때 그 지점부터 이어서 실행한다.
4. 간단한 이터레이터는 제너레이터로 만들고, 복잡한 동작이 필요하면 클래스로 이터레이터를 만드는 것이 일반적이다.

## Q5 (객관식 · 2점)

다음 중 실행 결과가 `[2, 4, 6]` 이 되는 것을 **모두 고르세요**.

1. `[x * 2 for x in range(1, 4)]`
2. `[x for x in range(1, 7) if x % 2 == 0]`
3. `[x for x in range(7) if x % 2 == 0]`
4. `[x * 2 for x in range(4)]`

## Q6 (객관식 · 2점)

다음 중 변수 `g` 에 **제너레이터 객체**가 저장되는 문장은?

1. `g = [i * i for i in range(5)]`
2. `g = (i * i for i in range(5))`
3. `g = {i: i * i for i in range(5)}`
4. `g = iter([i * i for i in range(5)])`

## Q7 (객관식 · 2점)

다음 코드를 실행했을 때 `job` 으로 시작하는 줄은 모두 몇 번 출력될까요?

```python
def job(n):
    print("job", n)
    return n

a = [job(i) for i in range(3)]
b = (job(i) for i in range(3))
print("ready")
```

1. 0번
2. 3번
3. 6번
4. 1번

## Q8 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
nums = [1, 2, 3]
it = iter(nums)
print(type(nums))
print(type(it))
```

## Q9 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
colors = ["red", "green", "blue"]
it = iter(colors)
print(next(it))
for c in it:
    print(c)
for c in it:
    print("again", c)
print("end")
```

## Q10 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
class Timer:
    def __init__(self, start):
        self.n = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.n <= 0:
            raise StopIteration
        self.n -= 1
        return self.n

for x in Timer(3):
    print(x)
print("done")
```

## Q11 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
def steps():
    print("start")
    yield 1
    print("middle")
    yield 2
    print("finish")

g = steps()
print("made")
print(next(g))
print(next(g))
```

## Q12 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
nums = [3, 8, 5, 12]
a = [n * 2 for n in nums if n > 4]
b = {n: n % 3 for n in nums}
print(a)
print(b)
print(len(a), len(b))
```

## Q13 (단답 · 3점)

제너레이터 함수에서 값을 하나씩 돌려주기 위해 `return` 대신 쓰는 키워드를 적으세요.

## Q14 (단답 · 3점)

이터레이터에 더 이상 돌려줄 값이 없을 때 `next()` 가 발생시키는 예외의 이름을 적으세요. (대소문자 구분)
