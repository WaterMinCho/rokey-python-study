def withdraw(balance, amount):
    if amount > balance:
        raise ValueError("잔액 부족")
    return balance - amount

balance = 10000
# 여기에 코드를 작성하세요
