class Steps:
    def __init__(self, stop):
        self.n = 0
        self.stop = stop

    def __iter__(self):
        return self

    def __next__(self):
        if self.n >= self.stop:
            raise StopIteration
        self.n += 1
        return self.n


class Multiples(Steps):
    # 여기에 __init__ 과 __next__ 를 작성하세요
    pass
