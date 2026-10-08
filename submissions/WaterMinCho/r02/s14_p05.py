import re

text = input()
p = re.compile(r"\d+")
for m in p.____(text):            # 매치되는 부분을 match 객체로 하나씩 꺼내기
    print(m.____(), m.____())     # 매치된 문자열, (시작, 끝) 튜플
