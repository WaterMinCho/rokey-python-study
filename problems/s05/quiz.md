# 5차시 퀴즈: 반복문

> 코드를 실행하지 말고 눈으로 풀어 보세요. 답은 `submissions/<내 ID>/s05/quiz.py` 에 적습니다.
> 출력 예측 문제의 답이 여러 줄이면 `"""` 로 감싸서 줄을 나눠 적습니다.

## Q1 (객관식 · 2점)

`range()` 가 만드는 수를 `list()` 로 바꿔 확인했습니다. 결과가 **잘못** 짝지어진 것은?

1. `list(range(4))` → `[0, 1, 2, 3]`
2. `list(range(2, 6))` → `[2, 3, 4, 5]`
3. `list(range(1, 10, 3))` → `[1, 4, 7, 10]`
4. `list(range(5, 0, -2))` → `[5, 3, 1]`

## Q2 (객관식 · 2점)

다음 코드의 빈칸(`____`)에 넣었을 때 **오류가 발생하는** 것은?

```python
for x in ____:
    print(x)
```

1. `"ROKEY"`
2. `[10, 20]`
3. `(1, 2)`
4. `2025`

## Q3 (객관식 · 2점)

다음 코드를 실행했더니 아래와 같이 출력되었습니다. 빈칸(`____`)에 들어갈 조건으로 알맞은 것은?

```python
count = 5
while ____:
    count -= 1
    print(count)
```

```
4
3
2
```

1. `count > 2`
2. `count >= 2`
3. `count > 3`
4. `count != 3`

## Q4 (객관식 · 2점)

다음 코드를 실행하면 어떻게 되나요?

```python
count = 0
while count < 3:
    if count == 1:
        continue
    print(count)
    count = count + 1
```

1. `0` 과 `2` 가 출력되고 끝난다
2. `0`, `1`, `2` 가 출력되고 끝난다
3. `0` 만 출력된 뒤 반복이 끝나지 않는다(무한 반복)
4. 아무것도 출력되지 않고 끝난다

## Q5 (객관식 · 2점)

다음 코드를 실행했을 때 출력되는 것은?

```python
for n in range(1, 5):
    total = 0
    total = total + n
print(total)
```

1. `10`
2. `4`
3. `0`
4. 오류가 발생한다

## Q6 (객관식 · 2점)

다음 코드를 실행했을 때의 출력을 바르게 설명한 것은?

```python
for i in range(2):
    for j in range(3):
        print("*", end="")
print()
```

1. `***` 이 두 줄로 출력된다
2. `******` 이 한 줄로 출력된다
3. `**` 이 세 줄로 출력된다
4. `*` 이 여섯 줄로 출력된다

## Q7 (객관식 · 2점)

반복문에 대한 설명으로 옳은 것을 **모두** 고르세요.

1. `for` 문은 리스트·문자열·튜플 같은 시퀀스의 값을 앞에서부터 하나씩 꺼내며 반복한다
2. `while` 문은 조건식이 거짓인 동안 코드블록을 반복한다
3. `break` 를 만나면 반복문을 끝내고, 반복문 바로 다음 코드부터 이어서 실행한다
4. `continue` 를 만나면 반복문을 끝내고, 반복문 바로 다음 코드부터 이어서 실행한다
5. `while True:` 는 조건이 항상 참이므로, 안에서 `break` 로 빠져나오지 않으면 스스로 끝나지 않는다

## Q8 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
scores = [70, 85]
for score in scores:
    print(score)
    print(scores)
print("done")
```

## Q9 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.
(`len()` 은 문자열의 글자 수를 알려 주는 내장 함수입니다.)

```python
animals = ["cat", "horse", "ox", "zebra"]
for animal in animals[1:3]:
    print(animal, len(animal))
```

## Q10 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
word = "A"
for ch in "BCD":
    word += ch
    print(word)
```

## Q11 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
for i in range(1, 10):
    if i == 7:
        break
    elif i % 3 == 0:
        continue
    print(i)
```

## Q12 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
n = 0
while True:
    n += 3
    if n > 10:
        break
    print(n)
print("끝", n)
```

## Q13 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.
(주간 요약본 예제처럼 f-string 을 썼습니다. `f"..."` 안의 `{i}` 자리에는 변수 `i` 의 값이 들어갑니다.)

```python
for i in range(2):
    for j in range(2):
        print(f"i={i}, j={j}")
```

## Q14 (단답 · 3점)

다음 코드를 실행했을 때 출력되는 숫자를 적으세요.

```python
count = 0
for n in range(2, 20, 3):
    count = count + 1
print(count)
```

## Q15 (단답 · 3점)

`total = total + price` 를 복합 대입 연산자를 사용해 `total ____ price` 로 줄여 쓰려고 합니다.
빈칸(`____`)에 들어갈 연산자를 적으세요.

## Q16 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
for n in range(0, 31, 5):
    if n % 3 == 0:
        print(n, end=" ")
print("끝")
```

## Q17 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요. (줄 끝에 남는 공백은 적지 않아도 됩니다.)

```python
for i in range(1, 4):
    for j in range(1, 4):
        if j > i:
            break
        print(i * j, end=" ")
    print()
```

## Q18 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
signals = [7, 15, 0, 4]
i = 0
value = 1
count = 0
while value != 0:
    value = signals[i]
    i += 1
    if value > 10:
        continue
    count += 1
print(i, count)
```

## Q19 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.
(리스트와 딕셔너리를 통째로 출력할 때의 모양은 4차시에서 배운 대로 적습니다.)

```python
stock = {"pen": 2, "note": 0}
orders = ["pen", "note", "pen", "pen"]
sold = []
for item in orders:
    if stock[item] == 0:
        continue
    stock[item] -= 1
    sold.append(item)
print(sold)
print(stock)
```
