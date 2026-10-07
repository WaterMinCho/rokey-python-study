class Hero:
    def __init__(self, name, hp):
        self.name = name
        self.hp = hp

    def hit(self, damage):
        self.hp = self.hp - damage
        if self.hp < 0:
            ____ = 0

    def alive(self):
        return ____ > 0

    def heal(self, amount):
        if self.____():
            self.hp = self.hp + amount
