class Elevator:
    def __init__(self, name):
        self.name = name
        self.people = 0

    def board(self):
        self.people += 1
        print(self.name, "탑승", self.people)

    def board_group(self, size):
        for i in range(size):
            self.board()
        print(self.name, "출발", self.people)


# 아래에 SmallElevator 클래스 작성
