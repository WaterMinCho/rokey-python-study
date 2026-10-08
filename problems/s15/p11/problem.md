# p11. 배수만 돌려주는 자식 이터레이터 (출력 · 8점)

`Steps(stop)` 은 1, 2, …, `stop` 을 차례로 돌려주는 이터레이터 클래스이고, 시작 코드에 완성되어 있습니다.
`Steps` 를 상속한 `Multiples(stop, k)` 클래스를 완성하세요. `Multiples` 객체는 1 부터 `stop` 까지의 수 가운데 **`k` 의 배수만** 작은 것부터 돌려줍니다.

```python
class Steps:
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


class Multiples(Steps):
    # 여기에 __init__ 과 __next__ 를 작성하세요
    pass
```

- `Steps` 클래스는 고치지 않습니다.
- `Multiples` 의 `__init__(self, stop, k)` 는 `stop` 을 부모의 `__init__` 에 넘겨 저장하고, `k` 를 `self.k` 에 저장합니다.
- `__next__` 를 재정의해 `k` 의 배수가 아닌 값은 건너뜁니다. 부모의 `__next__` 는 `super().__next__()` 로 부를 수 있습니다.
- `stop` 이 `k` 의 배수이면 `stop` 도 돌려줍니다. 돌려줄 배수가 더 없으면 `next()` 에서 `StopIteration` 예외가 나야 합니다.
- `k` 는 1 이상의 정수, `stop` 은 0 이상의 정수입니다.

## 테스트 코드와 출력 예

```python
for x in Multiples(10, 3):
    print(x)
```

```
3
6
9
```

```python
m = Multiples(5, 5)
print(next(m))
try:
    next(m)
except StopIteration:
    print("stop")
```

```
5
stop
```

```python
print(list(Multiples(7, 2)))
print(list(Multiples(2, 3)))
```

```
[2, 4, 6]
[]
```
