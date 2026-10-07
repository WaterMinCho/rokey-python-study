# p02. 스택 클래스 완성 (빈칸 채우기 · 4점)

리스트를 이용해 스택을 구현한 `Stack` 클래스입니다. 빈칸(`____`) 3곳을 채워 클래스를 완성하세요.

| 메서드 | 하는 일 |
|---|---|
| `push(data)` | `data` 를 스택의 맨 위에 넣습니다 |
| `pop()` | 맨 위 데이터를 꺼내서 반환합니다. 비어 있으면 `None` 을 반환합니다 |
| `is_empty()` | 비어 있으면 `True`, 아니면 `False` |
| `peak()` | 맨 위 데이터를 꺼내지 않고 반환합니다. 비어 있으면 `None` |
| `status_stack()` | 스택 리스트 전체를 반환합니다 |

- 객체를 만들면 스택은 빈 리스트로 시작합니다.
- 빈칸만 채웁니다. 다른 줄을 고치거나 줄을 추가하면 오답 처리됩니다.

```python
class Stack:
    def __init__(self):
        self.stack = ____

    def push(self, data):
        self.stack.____(data)

    def pop(self):
        if not self.is_empty():
            return self.stack.pop()
        return

    def is_empty(self):
        if len(self.stack) == 0:
            return True
        return False

    def peak(self):
        if not self.is_empty():
            return self.stack[____]
        return

    def status_stack(self):
        return self.stack
```

## 테스트 코드와 출력 예

```python
s = Stack()
s.push(1)
s.push(2)
print(s.peak())
print(s.pop())
print(s.status_stack())
```

```
2
2
[1]
```

```python
s = Stack()
print(s.peak())
print(s.pop())
print(s.is_empty())
```

```
None
None
True
```
