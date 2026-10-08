class Employee:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary

    def pay(self):
        return self.salary

    def tag(self):
        return self.name + "(사원)"


class Manager(Employee):
    def __init__(self, name, salary, bonus):
        pass

    def pay(self):
        pass

    def tag(self):
        pass
