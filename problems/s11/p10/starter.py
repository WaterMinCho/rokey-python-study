class Signal:
    def __init__(self):
        self.slots = []

    def connect(self, func):
        self.slots.append(func)

    def emit(self, value):
        for func in self.slots:
            func(value)


class TextWidget:
    def __init__(self):
        self.content = ""

    def setText(self, s):
        self.content = s

    def text(self):
        return self.content


class Label(TextWidget):
    pass


# 여기에 LineEdit 클래스를 정의하세요
