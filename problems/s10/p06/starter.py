class Account:
    def __init__(self):
        self.balance = 0

    def deposit(self, amount):
        self.balance = self.balance + amount
        print("입금:", amount)


# 아래에 BonusAccount 클래스를 작성하세요
