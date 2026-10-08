# p13. 대기 인원이 정해진 큐 (출력 · 8점)

강의의 `Queue` 클래스를 **상속**해, 대기 인원에 상한이 있는 `LimitedQueue` 클래스를 정의하세요.
시작 코드에 `Queue` 클래스가 들어 있습니다. `Queue` 는 고치지 않고 그 아래에 `LimitedQueue` 를 작성합니다.

| 구분 | 이름 | 내용 |
|---|---|---|
| 생성자 | `__init__(limit)` | 부모의 `__init__` 을 호출해 빈 큐를 만들고, 최대 대기 수 `limit` 를 인스턴스 변수 `limit` 에 저장합니다 |
| 메서드 | `enqueue(data)` | 큐에 이미 `limit` 개가 들어 있으면 넣지 않고 `가득 참: data` 를 출력합니다. 자리가 있으면 부모의 `enqueue` 로 넣고 `등록: data` 를 출력합니다 |
| 메서드 | `dequeue()` | 큐가 비어 있으면 `대기 없음` 을 출력하고 `None` 을 반환합니다. 비어 있지 않으면 부모의 `dequeue` 로 맨 앞 데이터를 꺼내 `호출: data` 를 출력하고, 꺼낸 데이터를 반환합니다 |

- `is_empty()` 와 `status_queue()` 는 부모에게서 물려받아 씁니다.
- `data` 로는 문자열과 정수가 모두 들어올 수 있습니다.
- 출력은 글자 하나까지 같아야 합니다(콜론 뒤 공백 한 칸).

```python
class Queue:
    def __init__(self):
        self.queue = []

    def enqueue(self, data):
        self.queue.append(data)

    def dequeue(self):
        if not self.is_empty():
            return self.queue.pop(0)
        return

    def is_empty(self):
        if len(self.queue) == 0:
            return True
        return False

    def status_queue(self):
        return self.queue


# 여기에 LimitedQueue 클래스를 작성하세요
```

## 테스트 코드와 출력 예

```python
q = LimitedQueue(2)
q.enqueue("A")
q.enqueue("B")
q.enqueue("C")
print(q.status_queue())
print(q.dequeue())
q.enqueue("C")
print(q.status_queue())
```

```
등록: A
등록: B
가득 참: C
['A', 'B']
호출: A
A
등록: C
['B', 'C']
```

```python
q = LimitedQueue(1)
print(q.dequeue())
print(q.is_empty(), q.limit)
q.enqueue(7)
print(q.is_empty())
```

```
대기 없음
None
True 1
등록: 7
False
```
