# p05. 장바구니에 여러 개 담기 (반환값 · 6점)

장바구니를 나타내는 `Cart` 클래스의 메서드 두 개를 완성하세요. `__init__` 과 `solution` 함수는 이미 작성되어 있으며 고치지 않습니다.

| 메서드 | 하는 일 |
|---|---|
| `put(item)` | `item` 을 리스트 `self.items` 의 맨 뒤에 추가 |
| `put_many(item, count)` | `item` 을 `count` 번 담기. **`put` 메서드를 `count` 번 호출**해서 구현 |

`solution(names, counts)` 는 장바구니를 하나 만들고, `names[i]` 를 `counts[i]` 개씩 차례로 담은 뒤 장바구니의 `items` 리스트를 반환합니다.

- 시작 코드의 `pass` 는 아무 일도 하지 않는 자리 채움 문장이므로, 지우고 그 자리에 코드를 작성하세요.

## 제한 사항
- `names` 와 `counts` 의 길이는 같고, 0 이상 10 이하
- `counts` 의 원소는 0 이상 5 이하의 정수

## 입출력 예

| names | counts | 반환값 |
|---|---|---|
| `["apple", "milk"]` | `[2, 1]` | `['apple', 'apple', 'milk']` |
| `["tea"]` | `[3]` | `['tea', 'tea', 'tea']` |
| `["a", "b"]` | `[0, 2]` | `['b', 'b']` |
