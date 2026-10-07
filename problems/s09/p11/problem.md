# p11. 게임 캐릭터 체력 (빈칸 채우기 · 6점)

체력(`hp`)을 관리하는 `Hero` 클래스입니다. 빈칸(`____`) 3곳을 채워 클래스를 완성하세요.

- `hit(damage)` 는 체력을 `damage` 만큼 줄입니다. 체력이 0 보다 작아지면 **0 으로** 맞춥니다.
- `alive()` 는 체력이 0 보다 크면 `True`, 아니면 `False` 를 **반환**합니다.
- `heal(amount)` 는 **살아 있을 때만**(`alive()` 가 `True` 일 때만) 체력을 `amount` 만큼 늘립니다. 체력이 0 인 캐릭터는 회복되지 않습니다.
- **빈칸만** 채웁니다. 다른 줄을 고치거나 줄을 추가하면 오답 처리됩니다.

## 테스트 코드와 출력 예

```python
h = Hero("기사", 10)
h.hit(4)
print(h.hp)
h.heal(3)
print(h.hp)
h.hit(20)
print(h.hp, h.alive())
h.heal(5)
print(h.hp)
```

```
6
9
0 False
0
```

```python
h = Hero("궁수", 5)
print(h.alive())
h.hit(5)
print(h.hp, h.alive())
```

```
True
0 False
```

## 시작 코드

```python
class Hero:
    def __init__(self, name, hp):
        self.name = name
        self.hp = hp

    def hit(self, damage):
        self.hp = self.hp - damage
        if self.hp < 0:
            ____ = 0

    def alive(self):
        return ____ > 0

    def heal(self, amount):
        if self.____():
            self.hp = self.hp + amount
```
