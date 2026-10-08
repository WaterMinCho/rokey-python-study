# 여기에 코드를 작성하세요
class Trip:
    def __init__(self, city, days):
        self.city = city
        self.days = days
        self.nights = days -1
    def label(self):
        return f"{self.city} {self.nights}박 {self.days}일"
    def extend(self, days):
        self.days += days
        self.nights += days
    
