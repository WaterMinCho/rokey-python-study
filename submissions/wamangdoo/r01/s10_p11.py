class Rect:
    kind = "직사각형"

    def __init__(self, width, height):
        self.width = width
        self.height = height
        print("도형 생성")

    def area(self):
        return self.width * self.height

    def info(self):
        print(self.kind, self.area())


# 아래에 Square 클래스를 작성하세요
# side, width, height 1 ~ 100
class Square(Rect):
    kind = "정사각형"
    
    def __init__(self, side):
        super().__init__(side, side)
        
    
