# 4차시 퀴즈 — 리스트와 딕셔너리

> 코드를 실행하지 말고 눈으로 풀어 보세요. 답은 `submissions/<내 ID>/s04/quiz.py` 에 적습니다.

## Q1 (객관식 · 2점)

`nums = [10, 20, 30]` 을 실행한 다음 아래 코드 중 하나를 실행했습니다. 오류가 발생하지 **않는** 것은?

1. `print(nums[3])`
2. `nums[3] = 40`
3. `nums.append(40)`
4. `del nums[3]`

## Q2 (객관식 · 2점)

리스트·튜플·딕셔너리에 대한 설명으로 옳지 **않은** 것은?

1. 리스트는 대괄호 `[ ]`, 튜플은 소괄호 `( )`, 딕셔너리는 중괄호 `{ }` 로 만든다.
2. 리스트와 튜플은 둘 다 `이름[인덱스]` 로 요소를 꺼내며, 인덱스는 0부터 시작한다.
3. 튜플도 리스트처럼 `append()` 로 요소를 추가할 수 있다.
4. 딕셔너리의 값(value) 자리에는 리스트도 넣을 수 있다.

## Q3 (객관식 · 2점)

`a = [1, 2]` 를 실행한 다음 아래 코드 중 하나를 실행하고 `print(a)` 를 했습니다.
출력이 `[1, 2, 3, 4]` 가 되는 것은?

1. `a.append([3, 4])`
2. `a.extend([3, 4])`
3. `a.insert(2, [3, 4])`
4. `a.append(3, 4)`

## Q4 (객관식 · 2점)

다음 중 `print(type(v))` 의 출력이 `<class 'tuple'>` 이 **아닌** 것은?

1. `v = ()`
2. `v = ("a")`
3. `v = "a",`
4. `v = "a", "b"`

## Q5 (객관식 · 2점)

`t = ('a', 'b', 'c')` 를 실행한 다음 아래 코드 중 하나를 실행했습니다.
오류 없이 `('A', 'b', 'c')` 가 출력되는 것은?

1. ```python
   t[0] = 'A'
   print(t)
   ```
2. ```python
   t = list(t)
   t[0] = 'A'
   print(t)
   ```
3. ```python
   t = ('A', 'b', 'c')
   print(t)
   ```
4. ```python
   t.remove('a')
   t.insert(0, 'A')
   print(t)
   ```

## Q6 (객관식 · 2점)

`user` 딕셔너리에 없는 키 `'email'` 로 값을 꺼내려고 합니다. ①과 ②를 **각각 따로** 실행했을 때의 결과로 옳은 것은?

```python
user = {'id': 'rokey', 'level': 3}
print(user.get('email'))   # ①
print(user['email'])       # ②
```

1. ①은 `None` 이 출력되고, ②는 오류가 발생한다
2. ①은 오류가 발생하고, ②는 `None` 이 출력된다
3. ①과 ② 모두 `None` 이 출력된다
4. ①과 ② 모두 오류가 발생한다

## Q7 (객관식 · 2점)

다음 중 실행하면 오류가 발생하는 코드는?

1. `d = {1: 'a', 1: 'b'}`
2. `d = {(1, 2): 'a'}`
3. `d = {[1, 2]: 'a'}`
4. `d = {'k': [1, 2]}`

## Q8 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요. (여러 줄이면 `"""` 로 감싸서 줄을 나눠 적습니다)

```python
box = [7, "seven", 7.5]
print(box)
print(box[1])
print(box[0] + box[2])
```

## Q9 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
bag = []
bag.append("펜")
bag.append("공책")
print(bag)
bag[0] = "연필"
bag.insert(1, "지우개")
print(bag)
print(bag.pop())
```

## Q10 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
stops = ['서울', '수원', '대전', '대구', '부산']
part = stops[1:3]
del stops[1]
print(part)
print(stops)
print(stops[1])
```

## Q11 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
a = (4, 5, 6)
b = list(a)
b[0] = a[1] + a[2]
print(a)
print(b)
print(type(a), type(b))
```

## Q12 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
pet = {}
pet['name'] = '초코'
pet['age'] = 3
pet['age'] = pet['age'] + 1
print(pet)
print(pet.keys())
print(pet.values())
```

## Q13 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
menu = {'김밥': 3000, '라면': 4000, '우동': 5000}
del menu['라면']
menu['김밥'] = 3500
print(menu.items())
print(menu.get('우동'))
```

## Q14 (단답 · 3점)

다음 코드를 실행한 뒤 `type(point)` 로 확인되는 자료형의 이름을 영어 소문자로 적으세요. (답 형식 예: `int`, `str`)

```python
point = 3.5, 7
```

## Q15 (단답 · 3점)

다음 코드를 실행했을 때 화면에 출력되는 값을 적으세요.

```python
menu = ["김밥", "라면", "김밥", "떡볶이"]
menu.remove("김밥")
print(menu[1])
```

## Q16 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
scores = [70, 85, 70, 95]
print(len(scores))
print(sum(scores))
print(sum(scores) / len(scores))
```

## Q17 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
colors = ['빨강', '파랑', '노랑']
codes = {1: '빨강', 2: '파랑', 3: '노랑'}
print(colors[1])
print(codes[1])
print(codes.get(0))
```

## Q18 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
empty = ()
robot = 'ROKEY', 11, 2.5
print(empty)
print(robot)
print(robot[0])
```
