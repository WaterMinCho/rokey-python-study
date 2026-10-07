# p06. 라디오 버튼 묶음 흉내 (출력 · 8점)

같은 창에 놓인 `QRadioButton` 들은 자동으로 묶여서 하나를 선택하면 나머지는 해제됩니다. 이 동작을 GUI 없이 흉내 내는 `RadioGroup` 클래스를 정의하세요.

- 생성자 `RadioGroup(names)`: 항목 이름 리스트를 저장합니다. 처음에는 아무것도 선택되지 않은 상태입니다.
- `setChecked(name)`: `name` 이 항목 목록에 있으면 그 항목만 선택하고 나머지는 모두 해제합니다. 목록에 없는 이름이면 `이름: 없는 항목` 을 출력하고 선택 상태는 바꾸지 않습니다.
- `isChecked(name)`: `name` 이 현재 선택된 항목이면 `True`, 아니면 `False` 를 반환합니다. 목록에 없는 이름이면 `False` 를 반환합니다.
- `order()`: 선택된 항목이 있으면 `이름 주문` 을, 없으면 `선택된 항목이 없습니다.` 를 출력합니다.

클래스만 정의하면 됩니다. 채점할 때는 아래와 같은 테스트 코드가 객체를 만들어 메서드를 호출합니다.

## 테스트 코드와 출력 예

```python
g = RadioGroup(["A런치", "B런치", "C런치"])
g.order()
g.setChecked("B런치")
g.order()
print(g.isChecked("B런치"), g.isChecked("A런치"))
```

```
선택된 항목이 없습니다.
B런치 주문
True False
```

```python
g = RadioGroup(["S", "M", "L"])
g.setChecked("S")
g.setChecked("L")
print(g.isChecked("S"))
g.setChecked("XL")
g.order()
```

```
False
XL: 없는 항목
L 주문
```

- 출력은 글자 하나까지 같아야 합니다. `XL:` 은 이름 바로 뒤에 콜론이 붙고, `L 주문` 은 이름과 `주문` 사이에 공백이 하나 있습니다.

## 제한 사항
- `names` 의 길이는 1 이상 10 이하, 이름은 서로 다른 문자열
