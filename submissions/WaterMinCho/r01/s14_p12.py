import re


def solution(text):
    answer = ""
    
    numbers = re.findall(r'\d+', text)
    
    
    if numbers:
        answer = max(numbers, key=len)
    
    return answer
