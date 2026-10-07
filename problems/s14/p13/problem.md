# p13. 오류 줄 골라내기 (빈칸 채우기 · 8점)

첫 줄에 정수 `N` 이, 이어서 `N` 줄의 로그가 입력됩니다. 프로그램은 로그를 줄바꿈으로 이어 붙인
문자열 `log` 하나로 만든 뒤, `ERROR` 로 **시작하는** 줄만 골라 그 줄 전체를 한 줄씩 출력하고
마지막에 그 개수를 출력합니다. 빈칸(`____`) 2곳을 채워 프로그램을 완성하세요.

```python
import re

n = int(input())
lines = []
for i in range(n):
    lines.append(input())
log = "\n".join(lines)

p = re.compile(____, ____)   # 'ERROR' 로 시작하는 줄 전체를 찾는 패턴, ^ 를 각 줄의 처음으로 보게 하는 옵션
errors = p.findall(log)
for line in errors:
    print(line)
print(len(errors))
```

- 첫 번째 빈칸은 정규식 패턴 문자열, 두 번째 빈칸은 컴파일 옵션입니다.
- 줄 중간에 `ERROR` 가 들어 있는 줄(`WARN no ERROR here`)은 고르지 않습니다. 소문자 `error` 도 고르지 않습니다.
- `ERROR` 만 있는 줄도 `ERROR` 로 시작하는 줄입니다.
- 해당하는 줄이 없으면 `0` 만 출력합니다.
- **빈칸만** 채웁니다. 다른 줄을 고치거나 줄을 추가하면 오답 처리됩니다.

## 입출력 예

입력
```
4
INFO start
ERROR disk full
WARN no ERROR here
ERROR timeout 30s
```
출력
```
ERROR disk full
ERROR timeout 30s
2
```

입력
```
3
INFO ok
ERROR
error lower
```
출력
```
ERROR
1
```
