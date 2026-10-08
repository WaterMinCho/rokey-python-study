# p10. 거꾸로 꺼내는 이터레이터 클래스 (빈칸 채우기 · 6점)

전달받은 데이터(리스트나 문자열)의 원소를 **맨 뒤에서부터** 하나씩 돌려주는 이터레이터 클래스 `Rewinder` 입니다.
빈칸(`____`) 2곳을 채워 클래스를 완성하세요.

```python
class Rewinder:
    def __init__(self, data):
        self.data = data
        self.pos = ____

    def __iter__(self):
        return self

    def __next__(self):
        if ____:
            raise StopIteration
        item = self.data[self.pos]
        self.pos = self.pos - 1
        return item
```

- 첫 번째 빈칸에는 처음 꺼낼 원소(마지막 원소)의 인덱스를 구하는 식이 들어갑니다.
- 두 번째 빈칸에는 맨 앞 원소까지 돌려준 뒤에 참이 되는 조건이 들어갑니다. 맨 앞 원소(인덱스 0)는 빠지지 않고 나와야 합니다.
- `data` 가 비어 있으면 아무 값도 돌려주지 않습니다.
- **빈칸만** 채웁니다. 다른 줄을 고치거나 줄을 추가하면 오답 처리됩니다.

## 테스트 코드와 출력 예

```python
for x in Rewinder([1, 2, 3]):
    print(x)
```

```
3
2
1
```

```python
print(list(Rewinder("abc")))
print(list(Rewinder([])))
```

```
['c', 'b', 'a']
[]
```

```python
r = Rewinder([7])
print(next(r))
try:
    next(r)
except StopIteration:
    print("stop")
```

```
7
stop
```
