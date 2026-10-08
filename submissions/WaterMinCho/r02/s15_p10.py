class Rewinder:
    def __init__(self, data):
        self.data = data
        self.pos = ____

    def __iter__(self):
        return self

    def __next__(self):
        if ____:
            raise StopIteration
        item = self.data[self.pos]
        self.pos = self.pos - 1
        return item
