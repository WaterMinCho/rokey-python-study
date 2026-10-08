class Course:
    def __init__(self, title, hours):
        self.title = title
        self.hours = hours

    def summary(self):
        return self.title + " " + str(self.hours) + "시간"


class OnlineCourse(____):
    def __init__(self, title, hours, site):
        ____(title, hours)
        self.site = site

    def summary(self):
        return ____ + " (" + self.site + ")"
