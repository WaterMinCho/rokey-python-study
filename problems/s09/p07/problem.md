# p07. 물탱크 채우기 (빈칸 채우기 · 6점)

물의 양(`level`)을 관리하는 `Tank` 클래스입니다. 빈칸(`____`) 3곳을 채워 클래스를 완성하세요.

- 객체를 만들면 `level` 은 0 입니다.
- `fill(amount)` 은 `level` 을 `amount` 만큼 늘립니다. **인수 없이** `fill()` 로 호출하면 `10` 만큼 늘립니다.
- `fill_twice(amount)` 는 같은 객체의 `fill` 메서드를 **두 번** 호출해서 `amount` 만큼씩 두 번 채웁니다.
- **빈칸만** 채웁니다. 다른 줄을 고치거나 줄을 추가하면 오답 처리됩니다.

## 테스트 코드와 출력 예

```python
t = Tank()
t.fill()
print(t.level)
t.fill(5)
print(t.level)
t.fill_twice(20)
print(t.level)
```

```
10
15
55
```

## 시작 코드

```python
class Tank:
    def __init__(self):
        self.level = 0

    def fill(self, amount=____):
        self.level = self.level + amount

    def fill_twice(self, amount):
        ____.fill(amount)
        self.____(amount)
```
