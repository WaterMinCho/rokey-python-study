# p15. 이름 목록 다듬기 (빈칸 채우기 · 6점)

쉼표(`,`)로 구분된 이름들이 문자열 `text` 하나로 주어집니다. 이름 앞뒤에는 공백이 섞여 있을 수 있습니다. 각 이름의 **양 끝 공백**을 지운 뒤 이름 사이에 `/` 를 넣어 이어 붙인 문자열을 반환하는 `solution` 함수입니다. 빈칸(`____`) 3곳을 채워 완성하세요.

```python
def solution(text):
    names = text.split(____)
    clean = list(map(lambda s: ____, names))
    return ____.join(clean)
```

- 첫 번째 빈칸: 이름을 나누는 구분자
- 두 번째 빈칸: 문자열 `s` 의 양 끝 공백을 지운 값
- 세 번째 빈칸: 이름 사이에 넣을 문자열
- 이름 가운데에 있는 공백은 지우지 않습니다(`"doosan robotics"` 는 한 이름입니다).
- **빈칸만** 채웁니다. 다른 줄을 고치거나 줄을 추가하면 오답 처리됩니다.

## 제한 사항
- `text` 는 길이 1 이상 100 이하의 문자열이며, 영문 소문자·공백·쉼표로만 이루어져 있습니다.
- 쉼표로 나눈 조각마다 공백이 아닌 글자가 한 글자 이상 들어 있습니다.

## 입출력 예

| 호출 | 반환값 |
|---|---|
| `solution(" kim, lee ,park ")` | `"kim/lee/park"` |
| `solution("robot")` | `"robot"` |
| `solution("  doosan robotics ,rokey  ")` | `"doosan robotics/rokey"` |
