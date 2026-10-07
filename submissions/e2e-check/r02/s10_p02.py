class Shape:
    def __init__(self, name, sides):
        self.name = name
        self.sides = sides

    def info(self):
        return self.name + " " + str(self.sides)


class Polygon(Shape):
    def angle_sum(self):
        answer = 0
        return answer
