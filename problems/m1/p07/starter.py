import re

text = input()
p = re.compile(____)        # 숫자 3자리-숫자 4자리-숫자 4자리 꼴
count = 0
for m in p.____(text):      # 매치 결과를 match 객체로 하나씩
    print(m.group(), m.start())
    count += 1
print(count)
