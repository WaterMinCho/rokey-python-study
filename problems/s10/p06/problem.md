# p06. 보너스 계좌 (출력 · 6점)

아래 `Account` 클래스가 이미 작성되어 있습니다(시작 코드에 포함).

```python
class Account:
    def __init__(self):
        self.balance = 0

    def deposit(self, amount):
        self.balance = self.balance + amount
        print("입금:", amount)
```

`Account` 를 **상속받는** `BonusAccount` 클래스를 정의하세요.

- `deposit(amount)` 을 **재정의**합니다. 먼저 **부모의 `deposit`** 과 똑같이 동작한 뒤(잔액 증가 + `입금: 금액` 출력), 보너스 `100` 을 잔액에 더하고 `보너스: 100` 을 출력합니다. (`super().deposit(amount)` 를 호출하면 부모의 동작을 그대로 가져올 수 있습니다)
- `__init__` 은 새로 만들지 않습니다. 부모의 것을 그대로 써서 잔액 `0` 으로 시작합니다.
- `Account` 클래스는 고치지 않습니다. 채점할 때는 아래와 같은 테스트 코드가 객체를 만들어 메서드를 호출합니다.

## 테스트 코드와 출력 예

```python
b = BonusAccount()
b.deposit(500)
print(b.balance)
```

```
입금: 500
보너스: 100
600
```

```python
a = Account()
a.deposit(500)
print(a.balance)
```

```
입금: 500
500
```

- 출력은 글자 하나까지 같아야 합니다(콜론 뒤 공백 한 칸).
