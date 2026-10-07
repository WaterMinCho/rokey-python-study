# p12. 카운터 변형 (출력 · 6점)

아래 `Counter` 클래스가 이미 작성되어 있습니다(시작 코드에 포함).

```python
class Counter:
    def __init__(self):
        self.value = 0

    def up(self):
        self.value = self.value + 1

    def show(self):
        print("현재 값:", self.value)
```

`Counter` 를 **상속받는** 두 클래스를 정의하세요.

| 클래스 | 설명 |
|---|---|
| `DoubleCounter(Counter)` | `up()` 을 **재정의**해 한 번 호출할 때 `value` 가 `2` 커지게 합니다. `__init__` 은 새로 만들지 않습니다. |
| `StepCounter(Counter)` | 생성자 `StepCounter(step)` 는 **부모의 `__init__`** 으로 `value` 를 `0` 으로 만든 뒤, `step` 을 인스턴스 변수 `step` 에 저장합니다. `up()` 을 **재정의**해 한 번 호출할 때 `value` 가 `step` 만큼 커지게 합니다. |

- `show()` 는 두 클래스 모두 재정의하지 않습니다.
- `Counter` 클래스는 고치지 않습니다. 채점할 때는 아래와 같은 테스트 코드가 객체를 만들어 메서드를 호출합니다.

## 테스트 코드와 출력 예

```python
d = DoubleCounter()
d.up()
d.up()
d.show()
```

```
현재 값: 4
```

```python
s = StepCounter(5)
s.up()
s.up()
s.up()
s.show()
```

```
현재 값: 15
```

```python
c = Counter()
d = DoubleCounter()
s = StepCounter(10)
c.up()
d.up()
s.up()
print(c.value, d.value, s.value)
```

```
1 2 10
```

## 제한 사항
- `step` 은 1 이상 100 이하의 정수
