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
