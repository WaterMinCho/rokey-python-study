import re

text = input()
tags = re.findall(____, text)   # '#' 뒤에 글자·숫자·밑줄이 1개 이상 이어진 덩어리
print(len(tags))
for t in tags:
    print(t)
