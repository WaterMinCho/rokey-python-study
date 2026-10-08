# 8차시 퀴즈: 자료구조와 알고리즘

> 코드를 실행하지 말고 눈으로 풀어 보세요. 답은 `submissions/<내 ID>/s08/quiz.py` 에 적습니다.

## Q1 (객관식 · 2점)

리스트의 첫 요소와 마지막 요소를 맞바꾸려고 아래처럼 작성했습니다. 출력되는 것은?

```python
a = [5, 6, 7, 8]
a[0] = a[3]
a[3] = a[0]
print(a)
```

1. `[8, 6, 7, 5]`
2. `[5, 6, 7, 5]`
3. `[5, 6, 7, 8]`
4. `[8, 6, 7, 8]`

## Q2 (객관식 · 2점)

다음 코드의 출력이 `[10, 20, 30, 40, 50]` 이 되도록 빈칸에 들어갈 코드는?

```python
lst = [50, 20, 30, 40, 10]
lst[0], lst[4] = ____
print(lst)
```

1. `lst[0], lst[4]`
2. `lst[1], lst[3]`
3. `lst[4], lst[0]`
4. `lst[4], lst[4]`

## Q3 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요. (여러 줄이면 `"""` 로 감싸서 줄을 나눠 적습니다)

```python
def swap_a(na, nb):
    temp = na
    na = nb
    nb = temp

def swap_b(cb):
    temp = cb[0]
    cb[0] = cb[1]
    cb[1] = temp

ca = [5, 9]
swap_a(ca[0], ca[1])
print(ca)
swap_b(ca)
print(ca)
```

## Q4 (객관식 · 2점)

다음 코드를 실행했을 때 출력되는 것은?

```python
a = [4, 5, 6]
b = a
b[1] = 50
b = [7, 8, 9]
b[0] = 70
print(a)
```

1. `[4, 5, 6]`
2. `[4, 50, 6]`
3. `[70, 50, 6]`
4. `[70, 8, 9]`

## Q5 (객관식 · 2점)

다음 코드를 실행했을 때 출력되는 것은?

```python
a = [10, 11, 12]
b = a
c = [10, 11, 12]
before = id(a)
a[1] = 21
print(before == id(a), id(a) == id(b), id(a) == id(c))
```

1. `True True False`
2. `True True True`
3. `False True False`
4. `True False False`

## Q6 (객관식 · 2점)

다음 코드를 실행했을 때 출력되는 것은? (강의·과제에서 쓰는 표준 파이썬 기준)

```python
x = 7
y = 7
p = [7, 7]
q = [7, 7]
print(id(x) == id(y), id(p) == id(q))
```

1. `True True`
2. `True False`
3. `False True`
4. `False False`

## Q7 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
def fk(cb):
    total = 0
    for sb in range(0, 3, 1):
        total = total + cb[sb]
    cb[0] = total
    return cb

ca = [4, 5, 6]
cd = fk(ca)
cd[2] = 0
print(ca)
print(cd)
```

## Q8 (객관식 · 2점)

리스트에서 가장 큰 값을 구하려고 아래처럼 작성했습니다. 출력되는 것은?

```python
ca = [14, 19, 16, 25]
max = ca[0]
if max < ca[1]:
    max = ca[1]
elif max < ca[2]:
    max = ca[2]
elif max < ca[3]:
    max = ca[3]
print(max)
```

1. `19`
2. `25`
3. `16`
4. `14`

## Q9 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
def fmax(a, b, c, d):
    fu = [a, b, c, d]
    max = fu[0]
    for i in range(1, 4, 1):
        if max < fu[i]:
            max = fu[i]
            print(i, max)
    return max

su = [12, 30, 25, 41, 8]
print("최댓값은", fmax(su[4], su[0], su[3], su[2]))
```

## Q10 (단답 · 3점)

다음 코드에서 반복문이 끝난 뒤 변수 `minix` 에 저장되어 있는 값을 적으세요.

```python
ca = [14, 9, 20, 6, 11]
mina = ca[0]
minix = 0
for sb in range(1, 5, 1):
    if mina > ca[sb]:
        mina = ca[sb]
        minix = sb
```

## Q11 (객관식 · 2점)

리스트 `data = [35, 12, 27, 8, 19]` 를 선택 정렬로 오름차순 정렬하려고 합니다.
첫 번째 단계(전체에서 가장 작은 값을 찾아 맨 앞 요소와 교환)만 수행한 직후의 리스트는?

1. `[8, 35, 12, 27, 19]`
2. `[12, 35, 27, 8, 19]`
3. `[8, 12, 27, 35, 19]`
4. `[8, 12, 19, 27, 35]`

## Q12 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
ca = [7, 3, 9, 1]
for sa in range(0, 3, 1):
    mina = ca[sa]
    minix = sa
    for sb in range(sa + 1, 4, 1):
        if mina > ca[sb]:
            mina = ca[sb]
            minix = sb
    temp = ca[sa]
    ca[sa] = ca[minix]
    ca[minix] = temp
    print(ca)
```

## Q13 (객관식 · 2점)

다음은 최솟값의 위치만 변수 `pos` 에 기억하는 방식으로 쓴 선택 정렬입니다.
`[10, 15, 20, 30, 40]` 이 출력되도록(오름차순 정렬) 빈칸에 들어갈 조건식은?

```python
def sel_sort(nums):
    for i in range(len(nums)):
        pos = i
        for j in range(i + 1, len(nums)):
            if ____:
                pos = j
        nums[i], nums[pos] = nums[pos], nums[i]
    return nums

print(sel_sort([30, 10, 40, 20, 15]))
```

1. `nums[j] < nums[i]`
2. `nums[j] > nums[pos]`
3. `nums[i] < nums[j]`
4. `nums[j] < nums[pos]`

## Q14 (단답 · 3점)

선택 정렬은 한 단계마다 남은 구간에서 가장 작은 값을 찾아 그 구간의 맨 앞 요소와 맞바꿉니다.
요소가 4개인 리스트는 이 단계를 3번 수행하면 어떤 값이 들어 있어도 정렬이 끝납니다.
같은 방식으로 요소가 6개인 리스트를 정렬할 때, 어떤 값이 들어 있어도 정렬이 끝나려면 단계를 최소 몇 번 수행해야 하는지 숫자만 적으세요.

## Q15 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
def fch(x):
    x["kim"] = 95
    x["park"] = 70

score = {"kim": 80, "lee": 90}
backup = score
fch(backup)
print(score)
print(len(score))
```

## Q16 (단답 · 3점)

두 변수가 같은 리스트를 가리키는지 확인하려고 메모리 주소 값을 비교했습니다.
빈칸 두 곳에 똑같이 들어가는, 객체의 메모리 주소 값을 돌려주는 내장 함수의 이름을 적으세요.

```python
a = [10, 11, 12]
b = a
print(____(a) == ____(b))
```

## Q17 (객관식 · 2점)

리스트에서 가장 큰 값을 반환하는 함수입니다. `-2` 가 출력되도록 빈칸에 들어갈 조건식은?

```python
def list_max(nums):
    big = nums[0]
    for num in nums:
        if ____:
            big = num
    return big

print(list_max([-6, -2, -9]))
```

1. `big > num`
2. `big < num`
3. `big < nums[num]`
4. `num < nums[0]`

## Q18 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
def fa(cb):
    cb = [cb[1], cb[0]]
    return cb

def fb(cb):
    temp = cb[0]
    cb[0] = cb[1]
    cb[1] = temp
    return cb

ca = [2, 7]
cd = fa(ca)
print(ca, cd)
ce = fb(ca)
ce[0] = 0
print(ca, ce)
```

## Q19 (객관식 · 2점)

다음 코드를 실행했을 때 출력되는 것은?

```python
count = 0

def push_max(cb):
    count = 0
    for i in range(1, len(cb), 1):
        if cb[0] < cb[i]:
            temp = cb[0]
            cb[0] = cb[i]
            cb[i] = temp
            count = count + 1
    return count

ca = [4, 9, 2, 11]
push_max(ca)
print(ca, count)
```

1. `[11, 4, 2, 9] 2`
2. `[11, 4, 2, 9] 0`
3. `[4, 9, 2, 11] 0`
4. `[11, 9, 2, 4] 0`
