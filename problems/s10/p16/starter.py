class Sensor:
    def __init__(self, name):
        self.name = name
        self.values = []

    def read(self, value):
        self.values.append(value)

    def report(self):
        print(self.name, self.values)


class RangeSensor(Sensor):
    def __init__(self, name, low, high):
        super().__init__(name)
        self.low = low
        self.high = high

    def read(self, value):
        if value >= self.low and value <= self.high:
            ____.read(value)


class AlarmSensor(____):
    def __init__(self, name, low, high):
        super().__init__(____)
        self.alarms = 0

    def read(self, value):
        if value < self.low or value > self.high:
            self.alarms = self.alarms + 1
        super().read(value)

    def report(self):
        super().report()
        print("경보", self.alarms)
