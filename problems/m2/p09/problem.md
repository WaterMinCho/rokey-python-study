# p09. 정원이 있는 엘리베이터 (출력 · 6점)

아래 `Elevator` 클래스가 이미 작성되어 있습니다(시작 코드에 포함).

```python
class Elevator:
    def __init__(self, name):
        self.name = name
        self.people = 0

    def board(self):
        self.people += 1
        print(self.name, "탑승", self.people)

    def board_group(self, size):
        for i in range(size):
            self.board()
        print(self.name, "출발", self.people)
```

`Elevator` 를 **상속받는** `SmallElevator` 클래스를 정의하세요.

1. 생성자는 이름 `name` 과 정원 `capacity` 를 받습니다. `name` 과 `people` 은 부모의 `__init__` 이 저장하게 하고, `capacity` 는 같은 이름의 인스턴스 변수에 저장합니다.
2. `board()` 를 재정의합니다. `people` 이 `capacity` 보다 작으면 부모의 `board()` 를 실행합니다. 그렇지 않으면 `people` 을 바꾸지 않고 `A 정원 초과` 처럼 이름과 `정원 초과` 를 출력합니다.
3. `board_group()` 은 새로 정의하지 않고 부모의 것을 씁니다.

## 제한 사항

- `capacity` 는 0 이상 100 이하의 정수입니다.
- `Elevator` 클래스는 고치지 않습니다. 채점할 때는 아래와 같은 테스트 코드가 객체를 만들어 메서드를 호출합니다.
- 제출하면 `Elevator` 의 `__init__`, `board()`, `board_group()` 을 다른 함수로 바꿔 놓은 테스트도 함께 돌립니다. `SmallElevator` 가 부모의 메서드를 호출하지 않고 부모의 코드를 옮겨 적은 답은 이 테스트에서 오답 처리됩니다.
- 출력은 글자 하나까지 같아야 합니다. 이름과 `정원 초과` 사이에는 공백 한 칸이 있습니다.

## 테스트 코드와 출력 예

```python
e = SmallElevator("A", 2)
e.board_group(3)
```

```
A 탑승 1
A 탑승 2
A 정원 초과
A 출발 2
```

```python
e = SmallElevator("D", 1)
e.board()
e.board()
print(e.name, e.people, e.capacity)
```

```
D 탑승 1
D 정원 초과
D 1 1
```
