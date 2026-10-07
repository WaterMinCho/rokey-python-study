# p05. 큐 클래스 완성 (빈칸 채우기 · 6점)

리스트를 이용해 큐를 구현한 `Queue` 클래스입니다. 빈칸(`____`) 3곳을 채워 클래스를 완성하세요.

| 메서드 | 하는 일 |
|---|---|
| `enqueue(data)` | `data` 를 큐의 맨 뒤에 넣습니다 |
| `dequeue()` | 가장 먼저 넣은 데이터를 꺼내서 반환합니다. 비어 있으면 `None` 을 반환합니다 |
| `is_empty()` | 비어 있으면 `True`, 아니면 `False` |
| `status_queue()` | 큐 리스트 전체를 반환합니다 |

- `dequeue()` 는 비어 있는지 확인하는 메서드를 먼저 호출해야 합니다.
- 빈칸만 채웁니다. 다른 줄을 고치거나 줄을 추가하면 오답 처리됩니다.

```python
class Queue:
    def __init__(self):
        self.queue = []

    def enqueue(self, data):
        self.queue.append(data)

    def dequeue(self):
        if not self.____():
            return self.queue.pop(____)
        return

    def is_empty(self):
        if ____ == 0:
            return True
        return False

    def status_queue(self):
        return self.queue
```

## 테스트 코드와 출력 예

```python
q = Queue()
q.enqueue(1)
q.enqueue(2)
q.enqueue(3)
print(q.dequeue())
print(q.status_queue())
```

```
1
[2, 3]
```

```python
q = Queue()
print(q.dequeue())
print(q.is_empty())
q.enqueue("x")
print(q.is_empty())
```

```
None
True
False
```
