# p11. 합격 부품 세기 (빈칸 채우기 · 8점)

부품 여섯 개의 무게가 리스트 `weights` 에 들어 있습니다.
허용 범위의 아래쪽 값 `low` 와 위쪽 값 `high` 를 한 줄에 하나씩 입력받아, 무게가 `low` 이상 `high` 이하인 부품의 수를 출력하는 프로그램입니다.

- `in_range` 함수는 `value` 가 `low` 이상 `high` 이하이면 `True`, 아니면 `False` 를 반환합니다.
- `count_ok` 함수는 리스트 `values` 의 값마다 `in_range` 를 호출해, `True` 가 나온 횟수를 반환합니다.

빈칸(`____`)을 채워 프로그램을 완성하세요.

- **빈칸만** 채웁니다. 다른 줄을 고치거나 줄을 추가하면 오답 처리됩니다.

## 주어진 코드

```python
def in_range(value, low, high):
    return ____

def count_ok(values, low, high):
    count = 0
    for v in values:
        if in_range(v, low, high):
            count += 1
    ____ count

weights = [98, 105, 110, 95, 94, 100]
low = int(input())
high = int(input())
print("합격:", ____, "개")
```

## 제한 사항
- 0 ≤ low ≤ high ≤ 200

## 입출력 예

입력

```
95
105
```

출력

```
합격: 4 개
```

98, 105, 95, 100 이 범위 안에 있습니다. 범위의 양 끝 값과 같은 95 와 105 도 셉니다.

입력

```
100
100
```

출력

```
합격: 1 개
```
