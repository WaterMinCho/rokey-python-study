from collections import deque


def is_palindrome(word):
    dq = deque()
    for i in range(len(word)):
        dq.append(word[i])
    while len(dq) > ____:
        if dq.____() != dq.____():
            return False
    return True


word = input()
print(is_palindrome(word))
