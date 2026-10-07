class Looper:
    def __init__(self, data):
        self.data = data
        self.pos = 0

    def ____(self):
        return self

    def __next__(self):
        if self.pos >= len(self.data):
            raise ____
        item = self.data[self.pos]
        self.pos = ____
        return item
