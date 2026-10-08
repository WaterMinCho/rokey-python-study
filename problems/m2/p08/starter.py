import re

p = re.compile(r"#[0-9a-f]{6}$", ____)    # 대문자 A~F 도 허용
codes = input().split()
count = 0
for code in codes:
    m = p.____(code)
    if m:
        print(m.group()[____])              # '#' 을 뺀 여섯 글자
        count += 1
print(count)
