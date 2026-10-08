# 16차시 · 알고리즘(1)

데이터를 넣은 순서와 꺼내는 순서의 관계로 구분하는 자료구조인 스택·큐·덱과, 중복을 허용하지 않는 세트를 배우는 차시입니다.
스택과 큐는 리스트의 `append` / `pop` 과 9차시의 클래스 문법으로 만들고, 덱은 `collections` 모듈의 `deque` 를 불러와 씁니다.
출력 예측 문제는 코드를 한 줄씩 따라가며 리스트가 어떻게 바뀌는지 옆에 적어 보면 풀립니다.

| 강의 절 | 내용 |
|---|---|
| 16.1~16.2 스택 | 후입선출(LIFO), push/pop, 리스트 `append()`/`pop()`, `Stack` 클래스 |
| 16.3~16.4 큐 | 선입선출(FIFO), enqueue/dequeue, 리스트 `append()`/`pop(0)`, `Queue` 클래스 |
| 16.5~16.6 덱 | 양쪽 끝 삽입·삭제, `from collections import deque`, `append`/`appendleft`/`pop`/`popleft` |
| 연습 문제 | 괄호 짝 검사(스택), 회전 큐(덱·리스트) |
| 8. 세트 | 중복 없는 자료구조, `add`/`remove`, 교집합 `&` · 합집합 `\|` · 차집합 `-` |

## 1. 알고리즘과 자료구조

- **알고리즘**은 문제를 해결하기 위한 명확한 절차나 방법입니다. 알고리즘을 이해하면 코드를 효율적으로 쓰고 실행 속도를 높일 수 있습니다.
- **자료구조**는 데이터를 저장하고 관리하는 방법입니다. 상황에 맞는 자료구조를 고르면 속도와 효율이 좋아집니다. 강의는 주요 자료구조로 리스트·튜플·딕셔너리·세트를 들었습니다.

## 2. 스택(Stack): 나중에 넣은 것이 먼저 나온다

- 삽입과 삭제가 한쪽 끝(top)에서만 일어납니다. 감자칩 통처럼 마지막에 넣은 것을 먼저 꺼내며, 이 방식을 **후입선출(LIFO, Last In First Out)** 이라고 부릅니다.
- 넣는 연산이 **push**, 꺼내는 연산이 **pop** 입니다.
- 강의가 든 활용 사례는 함수 호출 스택, 웹 브라우저의 뒤로 가기, 괄호 검사 같은 문자열 처리입니다.

리스트로 만들면 `append()` 가 push, `pop()` 이 pop 입니다. `pop()` 은 마지막 요소를 제거하면서 그 값을 돌려줍니다.

```python
stack = []
stack.append(7)       # [7]
stack.append(9)       # [7, 9]
top = stack.pop()     # 9 를 꺼냄 → [7]
print(top, stack)     # 9 [7]
```

클래스로 만들 때는 리스트를 인스턴스 변수에 두고, 꺼내거나 보는 메서드는 비어 있는지 먼저 확인합니다.

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

- 강의 자료는 맨 위 값을 보는 메서드 이름을 `peak` 로 씁니다(다른 자료에서는 보통 `peek`). 시험에는 강의의 철자가 나올 수 있습니다.
- `return` 뒤에 아무것도 없으면 `None` 을 돌려줍니다. 그래서 빈 스택에서 `print(s.pop())`, `print(s.peak())` 를 하면 `None` 이 출력됩니다.
- `peak()` 는 요소를 지우지 않고 `pop()` 은 지웁니다. 눈으로 실행할 때 `peak()` 뒤에 리스트를 줄여 적지 않도록 주의합니다.

## 3. 큐(Queue): 먼저 넣은 것이 먼저 나온다

- 줄 서기처럼 뒤로 들어와서 앞에서부터 나갑니다. 이 방식을 **선입선출(FIFO, First In First Out)** 이라고 부릅니다.
- 넣는 연산이 **enqueue**, 꺼내는 연산이 **dequeue** 입니다.
- 강의가 든 활용 사례는 운영체제의 프로세스 관리(작업 대기열)와 BFS(너비 우선 탐색, 다음 차시)입니다.

리스트로 만들면 `append()` 가 enqueue, `pop(0)` 이 dequeue 입니다. 인덱스 `0` 을 넣어야 맨 앞 요소가 빠집니다.

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

`Queue` 클래스는 `Stack` 클래스와 구조가 같고, 꺼내는 줄에서 `pop()` 대신 `pop(0)` 을 씁니다. 메서드 이름은 `enqueue`/`dequeue`/`status_queue` 로 바뀌고 `peak` 메서드는 없습니다.

`status_stack()` 과 `status_queue()` 는 복사본이 아니라 객체 안의 리스트 자체를 돌려줍니다(8차시의 별명). 돌려받은 리스트를 변수에 담아 두면 그 뒤에 넣고 꺼낸 결과가 그 변수에도 보이고, 그 변수에 `append` 하면 큐에도 들어갑니다.

```python
q = Queue()
q.enqueue(1)
view = q.status_queue()   # view 와 q.queue 는 같은 리스트
q.enqueue(2)
print(view)               # [1, 2]
view.append(3)
print(q.dequeue(), view)  # 1 [2, 3]   (dequeue 가 먼저 실행된 뒤의 리스트)
```

### 상속으로 일부 동작만 바꾸기

10차시의 상속을 쓰면 `Stack`·`Queue` 를 고치지 않고 일부 메서드만 다시 정의한 클래스를 만들 수 있습니다.

```python
class CountStack(Stack):
    def __init__(self):
        super().__init__()          # 부모가 self.stack = [] 를 만든다
        self.count = 0

    def push(self, data):           # 오버라이딩
        super().push(data)          # 넣는 일은 부모의 push 에 맡긴다
        self.count += 1

s = CountStack()
s.push(4)
s.push(8)
print(s.pop(), s.count)             # 8 2   (pop 은 부모의 메서드)
print(s.status_stack())             # [4]
```

- 자식이 `__init__` 을 새로 쓰면 부모의 `__init__` 이 자동으로 실행되지 않으므로, `super().__init__()` 을 불러 `self.stack` 을 만들어야 합니다.
- 자식이 다시 정의하지 않은 메서드는 부모의 코드가 실행됩니다. 자식이 `pop` 만 `self.stack.pop(0)` 으로 재정의하면 맨 앞 요소가 나오지만, 재정의하지 않은 `peak()` 는 여전히 마지막 요소 `self.stack[-1]` 을 돌려줍니다.
- 재정의한 메서드 안에서 부모 버전을 부를 때는 `super().push(data)` 로 씁니다. `self.push(data)` 라고 쓰면 자식의 `push` 가 자기 자신을 다시 부릅니다.

## 4. 덱(Deque): 양쪽 끝을 모두 쓴다

- 덱(Deque)이라는 이름은 **D**ouble **E**nded **QUE**ue 를 줄여 만들었습니다. 양쪽 끝에서 삽입과 삭제가 모두 가능해 스택과 큐를 합친 형태입니다.
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

- 덱을 `print` 하면 리스트와 달리 `deque([...])` 로 감싸져 나옵니다. 비어 있으면 `deque([])` 이고, 문자열 요소는 `deque(['a', 'b'])` 처럼 작은따옴표가 붙습니다.
- 강의가 든 활용 사례는 회전 큐(고정 크기 윈도우를 옮겨 가며 푸는 슬라이딩 윈도우)와 회문 검사입니다. 회문은 `level`, `SOS`, `rotator` 처럼 거꾸로 읽어도 같은 문자열입니다.
- 빈 덱에서 `pop()` 이나 `popleft()` 를 하면 빈 리스트의 `pop()` 과 마찬가지로 `IndexError` 가 납니다.

### 연습 문제의 패턴

괄호 짝 검사(스택)에서는 여는 괄호를 push 하고, 닫는 괄호를 만나면 pop 합니다. 닫을 때 스택이 비어 있거나, 다 보고도 스택에 남아 있으면 짝이 맞지 않습니다.

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

괄호 종류가 여럿(`()`, `{}`, `[]`)이면 pop 한 여는 괄호가 지금 닫는 괄호와 같은 종류인지도 비교합니다. `"([)]"` 는 `)` 를 만났을 때 pop 한 값이 `[` 라서 짝이 맞지 않습니다. 닫는 괄호마다 짝이 되는 여는 괄호를 4차시의 딕셔너리에 적어 두면 비교를 한 줄로 쓸 수 있습니다.

왼쪽으로 k 회전(덱)은 맨 앞 요소를 꺼내 맨 뒤에 붙이는 일을 k 번 반복합니다.

```python
dq = deque()
for x in [1, 2, 3, 4, 5]:
    dq.append(x)
for i in range(2):
    dq.append(dq.popleft())
print(dq)                           # deque([3, 4, 5, 1, 2])
```

- 오른쪽 회전은 반대로 맨 뒤 요소를 꺼내 맨 앞에 붙이는 `dq.appendleft(dq.pop())` 입니다. 길이가 n 인 덱을 왼쪽으로 k 번 돌린 결과는 오른쪽으로 n - k 번 돌린 결과와 같습니다.
- 리스트로는 왼쪽 회전을 `data.append(data.pop(0))`, 오른쪽 회전을 `data.insert(0, data.pop())` 으로 씁니다. 슬라이싱 `data[k:] + data[:k]` 는 왼쪽으로 k 회전한 새 리스트를 만듭니다.

회문 검사(덱)는 양 끝에서 하나씩 꺼내 비교합니다. 요소가 2개 이상 남아 있는 동안만 반복합니다.

```python
while len(dq) > 1:
    if dq.popleft() != dq.pop():
        return False
return True
```

## 5. 세트(set)

- 중복을 허용하지 않는 자료구조입니다. `{1, 2, 2, 3}` 은 요소가 3개입니다.
- `add(x)` 로 추가하고 `remove(x)` 로 제거합니다. 이미 있는 값을 `add` 해도 개수는 늘지 않습니다.
- 집합 연산은 교집합 `a & b`, 합집합 `a | b`, 차집합 `a - b`(a 에만 있는 것)입니다. 연산 결과는 새 세트이고 `a` 와 `b` 는 바뀌지 않습니다.
- 요소 개수는 `len()` 으로 셉니다. 연산을 이어 쓰면 한쪽에만 있는 요소를 `(a | b) - (a & b)` 로 구할 수 있습니다.

```python
a = {1, 2, 3}
b = {3, 4, 5}
a & b                 # {3}
a | b                 # {1, 2, 3, 4, 5}
a - b                 # {1, 2}
b - a                 # {4, 5}
(a | b) - (a & b)     # {1, 2, 4, 5}
len(a | b)            # 5
```

## 시험에서 헷갈리기 쉬운 포인트

- 스택은 LIFO 라 `pop()`, 큐는 FIFO 라 `pop(0)` 으로 꺼냅니다. 설명문에서 "먼저 들어온 것이 먼저 나간다"는 큐, "나중에 넣은 것이 먼저 나온다"는 스택입니다.
- 활용 사례를 묻는 객관식은 자료구조별로 구분합니다. 함수 호출 스택·뒤로 가기·괄호 검사는 스택, 작업 대기열(프로세스 관리)·BFS 는 큐, 회전 큐(슬라이딩 윈도우)·회문 검사는 덱의 사례로 강의에 나옵니다.
- 연산 이름과 리스트 메서드 이름을 구분합니다. 스택의 push 와 큐의 enqueue 는 둘 다 리스트의 `append` 로 구현하고, 스택의 pop 은 `pop()`, 큐의 dequeue 는 `pop(0)` 으로 구현합니다.
- `pop()` 은 값을 돌려주면서 지웁니다. `print(stack.pop(), stack.pop())` 처럼 한 줄에 두 번 있으면 왼쪽부터 차례로 두 개가 빠집니다.
- 빈 리스트에 `pop()` / `pop(0)` 을 하면 `IndexError` 가 납니다. 강의의 클래스는 `is_empty()` 로 먼저 확인해서 `None` 을 돌려주므로 오류가 나지 않습니다. 문제의 코드가 리스트를 직접 쓰는지 클래스를 쓰는지 먼저 확인합니다.
- `try` 안에서 빈 리스트를 `pop()` 하면 그 줄의 남은 동작(예: `out.append(data.pop())` 의 `append`)은 실행되지 않고 `except IndexError` 로 넘어갑니다. `finally` 는 예외가 났든 안 났든 실행됩니다(13차시).
- `return` 만 있는 줄은 `None` 을 반환합니다. 빈 스택의 `print(s.pop())`, `print(s.peak())` 는 `None` 을 출력합니다.
- `peak()` 는 지우지 않습니다. `peak()` 를 여러 번 불러도 요소 수가 줄지 않습니다.
- `queue.pop()`(마지막 제거)과 `queue.pop(0)`(처음 제거)을 섞어 쓰면 큐로 동작하지 않습니다. `remove(0)` 은 인덱스 0 이 아니라 값이 0 인 요소를 지웁니다. `stack.remove(stack[-1])` 도 맨 위 요소가 아니라 같은 값을 가진 첫 번째 요소를 지우므로 `pop()` 을 대신하지 못합니다.
- 덱 메서드의 방향을 구분합니다. `append`/`pop` 은 오른쪽(마지막), `appendleft`/`popleft` 는 왼쪽(처음)에서 동작합니다. `appendleft` 를 여러 번 하면 나중에 넣은 것이 더 앞에 옵니다.
- 덱 출력 형식은 `deque([1, 2])` 입니다. 리스트처럼 `[1, 2]` 라고 쓰면 틀립니다. 빈 덱은 `deque([])` 로 출력됩니다.
- `from collections import deque` 를 빼면 `deque` 를 쓸 수 없습니다(`NameError`). 모듈 이름은 끝에 s 가 붙은 `collections` 입니다.
- 회문 검사의 반복 조건은 `len(dq) > 1` 입니다. `> 0` 으로 쓰면 홀수 길이에서 가운데 글자 하나를 꺼낸 뒤 빈 덱에 `pop()` 을 해서 오류가 납니다.
- 회전 큐에서 왼쪽 회전은 앞에서 꺼내(`popleft`) 뒤에 붙이기(`append`)입니다. 회전 수가 길이보다 커도 그 횟수만큼 반복하면 됩니다. `dq.append(dq.pop())` 은 꺼낸 자리에 다시 넣으므로 덱이 바뀌지 않습니다.
- 상속한 클래스가 나오면 어떤 메서드를 재정의했는지부터 확인합니다. 재정의하지 않은 메서드는 부모의 코드가 실행됩니다.
- 세트는 중복을 세지 않습니다. `{5, 1, 5, 3, 1}` 의 요소는 3개입니다. `a - b` 와 `b - a` 는 결과가 다르므로 어느 세트에서 빼는지 확인합니다.
- 합집합의 크기는 `len(a) + len(b)` 가 아니라 `len(a | b)` 입니다. 겹치는 요소는 한 번만 들어갑니다.
- 강의 코드의 `print("stack = ", stack)` 는 문자열 끝의 공백에 쉼표가 넣는 공백이 더해져 `stack =  [1, 2, 3]` 처럼 `=` 뒤에 공백이 두 칸 출력됩니다(슬라이드의 주석에는 한 칸으로 적혀 있습니다). 리스트 안의 문자열은 `['a', 'b']` 처럼 작은따옴표로 출력됩니다.
