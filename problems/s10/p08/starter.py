class Ticket:
    def __init__(self, price):
        self.price = price

    def cost(self):
        return self.price


class StudentTicket(Ticket):
    pass


class SeniorTicket(Ticket):
    pass


def solution(orders):
    answer = 0
    return answer
