# p16. 형식을 검사하는 클래스 (출력 · 8점)

아래 `FormatError` 와 `Field` 클래스가 이미 작성되어 있습니다(시작 코드에 포함).

```python
import re


class FormatError(Exception):
    pass


class Field:
    label = "값"
    pattern = r".+"

    def __init__(self, text):
        if not re.match(self.pattern, text):
            raise FormatError(self.label + " 형식 오류: " + text)
        self.text = text

    def show(self):
        print(self.label, self.text)
```

`Field` 는 객체를 만들 때 `text` 가 클래스 변수 `pattern` 의 정규식과 맞는지 `re.match` 로 조사하고, 맞지 않으면 `FormatError` 를 일으킵니다.
`Field` 를 **상속받는** 클래스 `Phone` 과 `Date` 를 정의하세요.

| 클래스 | `label` | 허용하는 모양 |
|---|---|---|
| `Phone` | `"전화"` | `숫자 3자리-숫자 4자리-숫자 4자리` (예: `010-1234-5678`) |
| `Date` | `"날짜"` | `숫자 4자리-숫자 2자리-숫자 2자리` (예: `2025-10-16`) |

- 두 클래스 모두 클래스 변수 `label` 과 `pattern` 을 다시 선언합니다. `__init__` 과 `show` 는 새로 만들지 않고 부모의 것을 씁니다.
- 문자열 전체가 표의 모양이어야 합니다. 자릿수가 다르거나 앞뒤에 글자가 더 붙은 문자열(`010-1234-56789`, `x010-1234-5678`)로 객체를 만들면 `FormatError` 가 발생해야 합니다.
- `Date` 에는 월(가운데 두 자리)을 **정수**로 반환하는 메서드 `month()` 를 추가합니다. `Date("2025-10-16").month()` 는 `10`, `Date("2024-03-09").month()` 는 `3` 을 반환합니다.
- `FormatError` 와 `Field` 는 고치지 않습니다. 채점할 때는 아래와 같은 테스트 코드가 객체를 만들어 메서드를 호출합니다.

## 테스트 코드와 출력 예

```python
p = Phone("010-1234-5678")
p.show()
d = Date("2025-10-16")
d.show()
print(d.month())
```

```
전화 010-1234-5678
날짜 2025-10-16
10
```

```python
try:
    Phone("010-1234-56789")
except FormatError as e:
    print(e)
try:
    Date("2025-1-5")
except FormatError as e:
    print(e)
```

```
전화 형식 오류: 010-1234-56789
날짜 형식 오류: 2025-1-5
```

- 출력은 글자 하나까지 같아야 합니다.
