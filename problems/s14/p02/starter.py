import re

phone = input()
p = re.compile(____)   # 숫자 3자리, 하이픈(-), 숫자 4자리로 된 문자열 전체
if p.match(phone):
    print("OK")
else:
    print("NO")
