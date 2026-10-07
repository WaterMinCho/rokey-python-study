# p02. 체크박스 흉내 (빈칸 채우기 · 4점)

PyQt6 의 `QCheckBox` 가 하는 일을 GUI 없이 흉내 낸 `CheckBox` 클래스입니다. 빈칸(`____`) 3곳을 채워 완성하세요.

- 객체를 만들면 글자(`text`)를 저장하고, 선택되지 않은 상태로 시작합니다.
- `setChecked(value)` 는 선택 상태를 전달받은 값(`True`/`False`)으로 바꿉니다.
- `isChecked()` 는 현재 선택 상태를 `True` 또는 `False` 로 반환합니다.
- 빈칸만 채웁니다. 다른 줄을 고치거나 줄을 추가하면 오답 처리됩니다.

```python
class CheckBox:
    def __init__(self, text):
        self.text = text
        self.checked = ____

    def setChecked(self, value):
        self.checked = ____

    def isChecked(self):
        return ____
```

## 테스트 코드와 출력 예

```python
c = CheckBox("라떼")
print(c.isChecked())
c.setChecked(True)
print(c.isChecked())
print(c.text)
```

```
False
True
라떼
```

```python
a = CheckBox("A")
b = CheckBox("B")
a.setChecked(True)
print(a.isChecked(), b.isChecked())
```

```
True False
```

- 출력은 글자 하나까지 같아야 합니다. `False`/`True` 는 불(bool) 값이어야 하며 `0`/`1` 이 출력되면 오답입니다.
