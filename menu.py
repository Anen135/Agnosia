import curses
from typing import List, Optional


class Menu:
    """A scrollable text menu rendered in a curses window."""

    def __init__(
        self,
        options: List[str],
        title: Optional[str] = None,
        stdscr: Optional[curses.window] = None,
        height: Optional[int] = None,
        width: Optional[int] = None,
        start_y: int = 0,
        start_x: int = 0,
        content: Optional[str] = None,
    ):
        self.select = 0
        self.options = list(options)
        self.title = title
        self.content = content
        self.stdscr = stdscr

        self.height = height or (len(options) + 2 + (1 if title else 0))
        self.width = width or max((len(o) for o in options), default=10) + 4

        if stdscr is None:
            raise ValueError("stdscr is required")

        y, x = stdscr.getyx()
        self.start_y = start_y if start_y is not None else y
        self.start_x = start_x if start_x is not None else x

        self.window = curses.newwin(self.height, self.width, self.start_y, self.start_x)
        self.window.keypad(True)

    def display(self):
        self.window.clear()

        if self.title:
            self.window.addstr(self.title)

        if self.content:
            self.window.addstr(self.content)

        y, _ = self.window.getyx()

        for idx, option in enumerate(self.options):
            y_pos = idx + y + 1
            x_pos = 1
            if idx == self.select:
                self.window.addstr(y_pos, x_pos, option, curses.A_REVERSE)
            else:
                self.window.addstr(y_pos, x_pos, option)

        self.window.refresh()

    def navigate(self) -> int:
        """Block until a selection is made. Returns selected index."""
        length = len(self.options)
        while True:
            key = self.window.getch()
            if key == curses.KEY_UP:
                self.select = (self.select - 1) % length
            elif key == curses.KEY_DOWN:
                self.select = (self.select + 1) % length
            elif key in (10, 13, 32, curses.KEY_ENTER):
                return self.select
            elif ord("0") <= key <= ord("9"):
                index = key - ord("0") - 1
                if 0 <= index < length:
                    self.select = index
            self.display()
