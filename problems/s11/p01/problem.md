# p01. 버튼 클릭 연결 흉내 (빈칸 채우기 · 4점)

PyQt6 의 `btn.clicked.connect(order)` 가 하는 일을 GUI 없이 흉내 낸 프로그램입니다. 빈칸(`____`) 2곳을 채워 완성하세요.

- `Button` 클래스의 `connect(func)` 는 전달받은 함수를 `self.slot` 에 저장만 합니다.
- `click()` 은 저장해 둔 함수를 호출합니다. 버튼이 클릭된 상황에 해당합니다.
- 프로그램은 클릭 횟수를 한 줄 입력받아, 그 횟수만큼 `click()` 을 호출합니다. 클릭할 때마다 `order` 함수가 실행되어 `주문하세요` 가 한 줄씩 출력되어야 합니다.
- 빈칸만 채웁니다. 다른 줄을 고치거나 줄을 추가하면 오답 처리됩니다.

```python
def order():
    print("주문하세요")


class Button:
    def connect(self, func):
        self.slot = func

    def click(self):
        self.____()


btn = Button()
btn.connect(____)
clicks = int(input())
for i in range(clicks):
    btn.click()
```

## 입출력 예

| 입력 | 출력 |
|---|---|
| `3` | `주문하세요`<br>`주문하세요`<br>`주문하세요` |
| `1` | `주문하세요` |
| `0` | (아무것도 출력하지 않음) |
