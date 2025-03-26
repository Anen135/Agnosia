import keyboard
import time
import colorama

colorama.init()


class Console:
    CLEAR = '\033[2J\033[H'
    HOME = '\033[H'
    PREV = None

    def __init__(self):
        self.clear()
        self.x = 0
        self.y = 0

    def clear(self):
        print(self.CLEAR, end='')
        self.x = 0
        self.y = 0

    def goto(self, x, y=0):
        self.PREV = (self.x, self.y)
        print(f'\033[{x};{y}H', end='')
        self.x = x
        self.y = y

    def back(self):
        x, y = self.PREV
        print(f'\033[{x};{y}H', end='')


if __name__ == '__main__':
    cur = Console()

    print(f'АЗАЗА')
    print("123")
    cur.goto(1, 3)
    print("ХУЙ")

    pass
