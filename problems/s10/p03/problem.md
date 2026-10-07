# p03. 청소 로봇 (출력 · 4점)

아래 `Robot` 클래스가 이미 작성되어 있습니다(시작 코드에 포함).

```python
class Robot:
    def greet(self):
        print("안녕하세요")

    def work(self):
        print("작업 중")
```

`Robot` 을 **상속받는** `CleanBot` 클래스를 정의하세요.

- `CleanBot` 은 `work()` 메서드를 **재정의(오버라이딩)** 하여 `청소 중` 을 출력합니다.
- `greet()` 는 재정의하지 않습니다(부모의 것을 그대로 씁니다).
- `Robot` 클래스는 고치지 않습니다. 채점할 때는 아래와 같은 테스트 코드가 객체를 만들어 메서드를 호출합니다.

## 테스트 코드와 출력 예

```python
c = CleanBot()
c.greet()
c.work()
```

```
안녕하세요
청소 중
```

```python
r = Robot()
r.work()
c = CleanBot()
c.work()
```

```
작업 중
청소 중
```

- 출력은 글자 하나까지 같아야 합니다.
