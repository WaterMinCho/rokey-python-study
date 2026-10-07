class Stack:
    def __init__(self):
        self.stack = ____

    def push(self, data):
        self.stack.____(data)

    def pop(self):
        if not self.is_empty():
            return self.stack.pop()
        return

    def is_empty(self):
        if len(self.stack) == 0:
            return True
        return False

    def peak(self):
        if not self.is_empty():
            return self.stack[____]
        return

    def status_stack(self):
        return self.stack
