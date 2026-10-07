# 16차시 · 알고리즘(1) — 스택 · 큐 · 덱

데이터를 넣는 순서와 꺼내는 순서가 어떻게 다른지로 구분되는 세 가지 자료구조(스택·큐·덱)를 배우는 차시입니다.
새 문법은 거의 없습니다. 리스트의 `append` / `pop` 과 9차시에서 배운 클래스 문법을 조합할 뿐이라서,
코드를 한 줄씩 따라가며 리스트가 어떻게 변하는지 적어 보는 힘이 그대로 점수가 됩니다.

| 강의 절 | 핵심 |
|---|---|
| 16.1~16.2 스택 | 후입선출(LIFO), push/pop, 리스트 `append()`/`pop()`, `Stack` 클래스 |
| 16.3~16.4 큐 | 선입선출(FIFO), enqueue/dequeue, 리스트 `append()`/`pop(0)`, `Queue` 클래스 |
| 16.5~16.6 덱 | 양쪽 끝 삽입·삭제, `from collections import deque`, `append`/`appendleft`/`pop`/`popleft` |
| 연습 문제 | 괄호 짝 검사(스택), 회전 큐(덱) |
| 8. 세트 | 중복 없는 자료구조, `add`/`remove`, 교집합 `&` · 합집합 `\|` · 차집합 `-` |

## 1. 알고리즘과 자료구조

- **알고리즘**: 문제를 해결하기 위한 명확한 절차나 방법. 잘 이해하면 코드를 효율적으로 쓰고 속도를 높일 수 있습니다.
- **자료구조**: 데이터를 저장하고 관리하는 방법. 상황에 맞는 자료구조를 고르면 속도와 효율이 좋아집니다. 지금까지 배운 리스트·튜플·딕셔너리·세트도 자료구조입니다.

## 2. 스택(Stack) — 나중에 넣은 것이 먼저 나온다

- 삽입과 삭제가 한쪽 끝(top)에서만 일어납니다. 감자칩 통처럼 마지막에 넣은 것을 먼저 꺼냅니다. 이것을 **후입선출(LIFO, Last In First Out)** 이라고 부릅니다.
- 연산 이름: 넣기 = **push**, 꺼내기 = **pop**
- 활용 사례: 함수 호출 스택, 웹 브라우저 뒤로 가기, 괄호 짝 검사 같은 문자열 처리

리스트로 만들면 `append()` 가 push, `pop()` 이 pop 입니다. `pop()` 은 마지막 요소를 제거하면서 그 값을 돌려줍니다.

```python
stack = []
stack.append(7)       # [7]
stack.append(9)       # [7, 9]
top = stack.pop()     # 9 를 꺼냄 → [7]
print(top, stack)     # 9 [7]
```

클래스로 만들 때는 리스트를 인스턴스 변수에 두고, 메서드마다 비어 있는 경우를 먼저 확인합니다.

```python
class Stack:
    def __init__(self):
        self.stack = []

    def push(self, data):
        self.stack.append(data)

    def pop(self):
        if not self.is_empty():
            return self.stack.pop()
        return                      # 비어 있으면 None

    def is_empty(self):
        if len(self.stack) == 0:
            return True
        return False

    def peak(self):                 # 꺼내지 않고 맨 위 값만 본다
        if not self.is_empty():
            return self.stack[-1]
        return

    def status_stack(self):
        return self.stack
```

- 강의 자료는 맨 위 값을 보는 메서드 이름을 `peak` 로 씁니다(일반적으로는 `peek`). 시험에 강의 철자가 나올 수 있으니 그대로 기억해 두세요.
- `return` 뒤에 아무것도 없으면 `None` 을 돌려줍니다. 그래서 빈 스택에서 `print(s.pop())`, `print(s.peak())` 를 하면 `None` 이 찍힙니다.
- `peak()` 는 요소를 지우지 않고 `pop()` 은 지웁니다. 눈으로 실행할 때 가장 많이 틀리는 부분입니다.

## 3. 큐(Queue) — 먼저 넣은 것이 먼저 나온다

- 줄 서기와 같습니다. 뒤로 들어와서 앞에서부터 나갑니다. 이것을 **선입선출(FIFO, First In First Out)** 이라고 부릅니다.
- 연산 이름: 넣기 = **enqueue**, 꺼내기 = **dequeue**
- 활용 사례: 운영체제의 프로세스 관리(작업 대기열), BFS 너비 우선 탐색(다음 차시)

리스트로 만들면 `append()` 가 enqueue, `pop(0)` 이 dequeue 입니다. 인덱스 `0` 을 써야 맨 앞이 빠집니다.

```python
queue = []
queue.append("a")     # ['a']
queue.append("b")     # ['a', 'b']
first = queue.pop(0)  # 'a' 를 꺼냄 → ['b']
print(first, queue)   # a ['b']
```

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
```

스택 클래스와 다른 곳은 `pop()` 이 `pop(0)` 으로 바뀐 것 하나뿐입니다. 큐에는 `peak` 메서드가 없습니다.

## 4. 덱(Deque) — 양쪽 끝을 모두 쓴다

- **D**ouble **E**nded **QUE**ue 의 줄임말. 양쪽 끝에서 삽입과 삭제가 모두 가능해 스택과 큐를 합친 형태입니다.
- 파이썬 내장 모듈 `collections` 의 `deque` 클래스를 씁니다. 먼저 `from collections import deque` 로 불러와야 합니다.

| 메서드 | 하는 일 |
|---|---|
| `append(x)` | 마지막(오른쪽)에 넣기 |
| `appendleft(x)` | 처음(왼쪽)에 넣기 |
| `pop()` | 마지막 요소를 꺼내서 돌려주기 |
| `popleft()` | 처음 요소를 꺼내서 돌려주기 |

```python
from collections import deque

dq = deque()          # 빈 덱
dq.append(1)          # deque([1])
dq.appendleft(2)      # deque([2, 1])
dq.append(3)          # deque([2, 1, 3])
print(dq.popleft())   # 2  → deque([1, 3])
print(dq.pop())       # 3  → deque([1])
print(dq)             # deque([1])
```

- 덱을 `print` 하면 리스트와 달리 `deque([...])` 로 감싸져 나옵니다. 비어 있으면 `deque([])` 입니다.
- 활용 사례: 회전 큐(고정 크기 윈도우를 옮겨 가며 푸는 슬라이딩 윈도우), 회문 검사(거꾸로 읽어도 같은 문자열 — `level`, `SOS`, `rotator`).

### 연습 문제의 두 가지 패턴

괄호 짝 검사(스택) — 여는 괄호는 push, 닫는 괄호를 만나면 pop. 닫을 때 스택이 비어 있거나, 다 보고도 스택에 남아 있으면 짝이 맞지 않는 것입니다.

```python
def check(s):
    stack = []
    for i in range(len(s)):
        if s[i] == "(":
            stack.append(s[i])
        elif s[i] == ")":
            if len(stack) == 0:     # 닫을 괄호가 없다
                return False
            stack.pop()
    return len(stack) == 0          # 남은 여는 괄호가 없어야 True
```

왼쪽으로 k 회전(덱) — 맨 앞 요소를 꺼내 맨 뒤에 붙이는 일을 k 번 반복합니다.

```python
dq = deque()
for x in [1, 2, 3, 4, 5]:
    dq.append(x)
for i in range(2):
    dq.append(dq.popleft())
print(dq)                           # deque([3, 4, 5, 1, 2])
```

회문 검사(덱) — 양 끝에서 하나씩 꺼내 비교합니다. 요소가 2개 이상 남아 있는 동안만 반복해야 합니다.

```python
while len(dq) > 1:
    if dq.popleft() != dq.pop():
        return False
return True
```

## 5. 세트(set)

- 중복을 허용하지 않는 자료구조입니다. `{1, 2, 2, 3}` 은 요소가 3개입니다.
- `add(x)` 로 추가, `remove(x)` 로 제거. 이미 있는 값을 `add` 해도 개수는 늘지 않습니다.
- 집합 연산: 교집합 `a & b`, 합집합 `a | b`, 차집합 `a - b`(a 에만 있는 것).

```python
a = {1, 2, 3}
b = {3, 4, 5}
a & b   # {3}
a | b   # {1, 2, 3, 4, 5}
a - b   # {1, 2}
b - a   # {4, 5}
```

## 시험에서 헷갈리기 쉬운 포인트

- 스택 = LIFO = `pop()`, 큐 = FIFO = `pop(0)`. 설명문에서 "먼저 들어온 것이 먼저 나간다"는 큐, "나중에 넣은 것이 먼저"는 스택입니다.
- `pop()` 은 값을 돌려주면서 지웁니다. `print(stack.pop(), stack.pop())` 처럼 한 줄에 두 번 있으면 왼쪽부터 차례로 두 개가 빠집니다.
- 빈 리스트에 `pop()` / `pop(0)` 을 하면 `IndexError` 가 납니다. 강의의 클래스는 `is_empty()` 로 먼저 확인해서 `None` 을 돌려주므로 오류가 나지 않습니다. 어느 쪽 코드인지 확인하세요.
- `return` 만 있는 줄은 `None` 을 반환합니다. 빈 스택의 `print(s.pop())`, `print(s.peak())` 는 `None` 을 출력합니다.
- `peak()` 는 지우지 않습니다. `peak()` 뒤에도 요소 수는 그대로입니다.
- `queue.pop()`(마지막 제거)과 `queue.pop(0)`(처음 제거)을 섞어 쓰면 큐가 아닙니다. `remove(0)` 은 인덱스가 아니라 값 0 을 지우는 것이라 전혀 다릅니다.
- 덱 메서드 네 개의 방향: `append`/`pop` 은 오른쪽(마지막), `appendleft`/`popleft` 는 왼쪽(처음). `appendleft` 를 여러 번 하면 나중 것이 더 앞에 옵니다.
- 덱 출력 형식은 `deque([1, 2])` 입니다. 리스트처럼 `[1, 2]` 라고 쓰면 틀립니다. 빈 덱은 `deque([])`.
- `from collections import deque` 를 빼면 `deque` 를 쓸 수 없습니다(`NameError`). 모듈 이름은 `collections`(끝에 s).
- 회문 검사의 반복 조건은 `len(dq) > 1`. `> 0` 으로 쓰면 홀수 길이에서 가운데 글자 하나를 꺼낸 뒤 빈 덱에 `pop()` 을 해서 오류가 납니다.
- 회전 큐에서 왼쪽으로 회전 = 앞에서 꺼내(`popleft`) 뒤에 붙이기(`append`). 회전 수가 길이보다 커도 그 횟수만큼 반복하면 됩니다.
- 세트는 중복을 세지 않습니다. `{5, 1, 5, 3, 1}` 의 요소는 3개. `a - b` 는 a 에만 있는 것이라 순서가 바뀌면 결과도 바뀝니다.
- 강의 코드의 `print("stack = ", stack)` 처럼 쉼표로 이으면 사이에 공백 한 칸이 들어갑니다. 리스트 안의 문자열은 작은따옴표로 찍힙니다: `['a', 'b']`.
