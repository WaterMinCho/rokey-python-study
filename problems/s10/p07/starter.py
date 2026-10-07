class Vehicle:
    def __init__(self, name, speed):
        self.name = name
        self.speed = speed

    def info(self):
        print(self.name, self.speed)


class Bicycle(Vehicle):
    def __init__(self, name, speed, gears):
        super().__init__(____, speed)
        self.gears = gears

    def info(self):
        ____.info()
        print("기어:", self.gears)


if __name__ == "____":
    b = Bicycle("자전거", 25, 7)
    b.info()
