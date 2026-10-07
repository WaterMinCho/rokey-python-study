# p10. 긴급 안내 방송 (출력 · 6점)

아래 `Announcer` 클래스가 이미 작성되어 있습니다(시작 코드에 포함).

```python
class Announcer:
    def __init__(self, place):
        self.place = place

    def prefix(self):
        return "[안내]"

    def say(self, text):
        print(self.prefix() + " " + self.place + ": " + text)
```

`Announcer` 를 **상속받는** `EmergencyAnnouncer` 클래스를 정의하세요.

- `prefix()` 메서드만 **재정의(오버라이딩)** 하여 문자열 `[긴급]` 을 **반환**합니다.
- `__init__` 과 `say()` 는 새로 만들지 않습니다. 부모의 것을 그대로 씁니다.
- `Announcer` 클래스는 고치지 않습니다. 채점할 때는 아래와 같은 테스트 코드가 객체를 만들어 메서드를 호출합니다.

## 테스트 코드와 출력 예

```python
e = EmergencyAnnouncer("3층")
e.say("대피하세요")
```

```
[긴급] 3층: 대피하세요
```

```python
a = Announcer("로비")
a.say("환영합니다")
e = EmergencyAnnouncer("로비")
e.say("환영합니다")
```

```
[안내] 로비: 환영합니다
[긴급] 로비: 환영합니다
```

- 출력은 글자 하나까지 같아야 합니다. 대괄호 뒤 공백 한 칸, 장소 뒤 콜론과 공백 한 칸입니다.
