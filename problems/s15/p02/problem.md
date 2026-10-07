# p02. 순서대로 꺼내는 이터레이터 클래스 (빈칸 채우기 · 4점)

전달받은 데이터(리스트나 문자열)의 원소를 앞에서부터 하나씩 돌려주는 이터레이터 클래스 `Looper` 입니다.
빈칸(`____`) 3곳을 채워 클래스를 완성하세요.

```python
class Looper:
    def __init__(self, data):
        self.data = data
        self.pos = 0

    def ____(self):
        return self

    def __next__(self):
        if self.pos >= len(self.data):
            raise ____
        item = self.data[self.pos]
        self.pos = ____
        return item
```

- 첫 번째 빈칸: 이 객체를 for 문에 넣을 수 있게 해 주는, 자기 자신을 돌려주는 특별한 메서드의 이름
- 두 번째 빈칸: 더 돌려줄 값이 없을 때 일으켜야 하는 예외
- 세 번째 빈칸: 다음 호출 때 그 다음 원소를 가리키도록 위치를 옮기는 식
- **빈칸만** 채웁니다. 다른 줄을 고치거나 줄을 추가하면 오답 처리됩니다.

## 테스트 코드와 출력 예

```python
for x in Looper([1, 2, 3]):
    print(x)
```

```
1
2
3
```

```python
it = Looper([5])
print(next(it))
try:
    next(it)
except StopIteration:
    print("stop")
```

```
5
stop
```
