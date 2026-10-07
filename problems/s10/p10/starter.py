class Announcer:
    def __init__(self, place):
        self.place = place

    def prefix(self):
        return "[안내]"

    def say(self, text):
        print(self.prefix() + " " + self.place + ": " + text)


# 아래에 EmergencyAnnouncer 클래스를 작성하세요
