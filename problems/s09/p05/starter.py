class Cart:
    def __init__(self):
        self.items = []

    def put(self, item):
        pass

    def put_many(self, item, count):
        pass


def solution(names, counts):
    cart = Cart()
    for i in range(len(names)):
        cart.put_many(names[i], counts[i])
    return cart.items
