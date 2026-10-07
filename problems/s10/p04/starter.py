class Device:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def info(self):
        print("제품:", self.name)
        print("가격:", self.price)


class Laptop(____):
    def __init__(self, name, price, ram):
        ____.__init__(name, price)
        self.ram = ____
