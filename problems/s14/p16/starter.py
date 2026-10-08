import re


class FormatError(Exception):
    pass


class Field:
    label = "값"
    pattern = r".+"

    def __init__(self, text):
        if not re.match(self.pattern, text):
            raise FormatError(self.label + " 형식 오류: " + text)
        self.text = text

    def show(self):
        print(self.label, self.text)


# 아래에 Phone, Date 클래스를 작성하세요
