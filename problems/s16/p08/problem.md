# p08. 덱으로 회문 검사 (빈칸 채우기 · 6점)

단어를 입력받아 회문(거꾸로 읽어도 같은 문자열, 예: `level`, `SOS`)인지 덱으로 검사하는 프로그램입니다.
빈칸(`____`) 3곳을 채워 프로그램을 완성하세요.

- 글자를 모두 덱에 넣은 뒤, 양쪽 끝에서 하나씩 꺼내 비교합니다. 다르면 바로 `False` 입니다.
- 비교는 덱에 글자가 2개 이상 남아 있는 동안만 합니다.
- 대소문자는 구분합니다.
- 빈칸만 채웁니다. 다른 줄을 고치거나 줄을 추가하면 오답 처리됩니다.

```python
from collections import deque


def is_palindrome(word):
    dq = deque()
    for i in range(len(word)):
        dq.append(word[i])
    while len(dq) > ____:
        if dq.____() != dq.____():
            return False
    return True


word = input()
print(is_palindrome(word))
```

## 입출력 예

| 입력 | 출력 |
|---|---|
| `level` | `True` |
| `robot` | `False` |
| `SOS` | `True` |
| `ab` | `False` |
