# p10. 입력창과 라벨 연결 흉내 (출력 · 8점)

PyQt6 의 `entry.textChanged.connect(label.setText)` 가 동작하는 과정을 GUI 없이 흉내 냅니다. 시작 코드에는 아래 세 클래스가 들어 있습니다. 이 클래스들은 고치지 말고, 그 아래에 `TextWidget` 을 상속받는 `LineEdit` 클래스를 정의하세요.

```python
class Signal:
    def __init__(self):
        self.slots = []

    def connect(self, func):
        self.slots.append(func)

    def emit(self, value):
        for func in self.slots:
            func(value)


class TextWidget:
    def __init__(self):
        self.content = ""

    def setText(self, s):
        self.content = s

    def text(self):
        return self.content


class Label(TextWidget):
    pass
```

- `Signal` 은 시그널을 흉내 냅니다. `connect(func)` 는 함수를 목록에 넣어 두기만 하고, `emit(value)` 는 넣어 둔 함수를 연결한 순서대로 `func(value)` 로 호출합니다.
- `TextWidget` 은 글자를 저장하는 위젯의 공통 부분이고, `Label` 은 그것을 그대로 물려받은 라벨입니다.

`LineEdit` 이 지켜야 할 규칙입니다.

- `LineEdit()` 으로 만든 객체의 글자는 빈 문자열 `""` 입니다. `text()` 는 새로 정의하지 않고 `TextWidget` 의 것을 물려받아 씁니다.
- 객체마다 자기만의 `Signal` 객체를 `textChanged` 라는 인스턴스 변수로 가집니다. 입력창이 여러 개이면 `textChanged` 도 입력창마다 따로 있어야 합니다.
- `setText(s)` 는 `s` 가 지금 저장된 글자와 다를 때만 동작합니다. 저장된 글자를 `s` 로 바꾸고, 바꾼 다음에 `textChanged.emit(s)` 를 호출합니다.
- `s` 가 지금 저장된 글자와 같으면 `setText(s)` 는 글자를 다시 저장하지도, 시그널을 보내지도 않습니다.

채점할 때는 시작 코드의 세 클래스와 직접 정의한 `LineEdit` 을 불러온 뒤, 아래와 같은 테스트 코드가 객체를 만들어 메서드를 호출합니다.

## 테스트 코드와 출력 예

```python
entry = LineEdit()
label = Label()
entry.textChanged.connect(label.setText)
print(entry.text() == "", label.text() == "")
entry.setText("RO")
print(entry.text(), label.text())
entry.setText("ROKEY")
print(entry.text(), label.text())
```

```
True True
RO RO
ROKEY ROKEY
```

```python
def report(s):
    print("받은 글자:", s, "/ 입력창:", entry.text())

entry = LineEdit()
entry.textChanged.connect(report)
entry.setText("3")
entry.setText("3")
entry.setText("30")
```

```
받은 글자: 3 / 입력창: 3
받은 글자: 30 / 입력창: 30
```

- 두 번째 예에서 `entry.setText("3")` 을 두 번 호출했지만 두 번째는 글자가 바뀌지 않아 `report` 가 실행되지 않습니다.
- `report` 가 실행되는 시점에 `entry.text()` 는 이미 새 글자입니다.
