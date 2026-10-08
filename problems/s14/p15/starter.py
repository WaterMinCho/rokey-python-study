import re

text = input()
pattern = ____                    # 아이디@도메인 모양의 이메일 주소
mails = re.____(pattern, text)    # 매치되는 모든 문자열을 리스트로
print(mails)
print(len(mails))
