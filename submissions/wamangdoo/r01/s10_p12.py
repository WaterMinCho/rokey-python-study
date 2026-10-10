class Counter:
    def __init__(self):
        self.value = 0

    def up(self):
        self.value = self.value + 1

    def show(self):
        print("현재 값:", self.value)


# 아래에 DoubleCounter, StepCounter 클래스를 작성하세요
class DoubleCounter(Counter):
    def up(self):
        self.value = self.value + 2

class StepCounter(Counter):
    def __init__(self, step):
        super().__init__()
        self.step = step
    def up(self):
        self.value = self.value + self.step
