# p05. 산책 가능 여부 (반환값 · 6점)

기온 `temp`(정수)와 비가 오는지 여부 `is_raining`(`True` 또는 `False`)이 주어집니다.
아래 두 조건을 모두 만족하면 `True` 를, 하나라도 만족하지 않으면 `False` 를 **반환(return)** 하는 `solution` 함수를 완성하세요.

- 기온이 10도 이상 25도 이하이다.
- 비가 오지 않는다(`is_raining` 이 `False`).

주의할 점

- 반환값은 문자열 `"True"` 가 아니라 **bool 값** `True` / `False` 여야 합니다(자료형까지 채점합니다).
- 함수 이름과 매개변수는 바꾸지 않습니다. `print` 가 아니라 `return` 으로 돌려줍니다.

## 제한 사항
- -30 ≤ temp ≤ 45

## 입출력 예

| temp | is_raining | 반환값 |
|---|---|---|
| 18 | False | True |
| 25 | False | True |
| 9 | False | False |
| 18 | True | False |
