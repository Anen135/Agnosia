import curses

from terminal import write
from dev_console import CONSOLE_KEYS
from display import draw_live_map


class Menu:
    """A menu that keeps the selected option visible in small terminals."""

    def __init__(self, options, title=None, stdscr=None, height=None, width=None, start_y=0, start_x=0, content=None, on_console=None, sidebar=None):
        if stdscr is None:
            raise ValueError("stdscr is required")
        self.select = 0
        self.options = list(options)
        self.title = title
        self.content = content
        self.on_console = on_console
        self.sidebar = sidebar
        self.stdscr = stdscr
        self.requested_height = height
        self.requested_width = width
        self.start_y = start_y or 0
        self.start_x = start_x or 0
        self.window = None
        self._geometry = None
        self._layout()

    def _header(self):
        return ((self.title or "") + (self.content or "")).splitlines()

    def _layout(self):
        lines = self._header()
        screen_h, screen_w = self.stdscr.getmaxyx()
        self._sidebar_data = self.sidebar() if self.sidebar else None
        self._sidebar_width = 0
        if self._sidebar_data is not None and screen_w >= 8:
            maze = self._sidebar_data[0]
            self._sidebar_width = min(len(maze[0]) + 1, screen_w // 2)
            screen_w -= self._sidebar_width + 1
        needed_h = max(self.requested_height or 0, len(lines) + len(self.options) + 2)
        needed_w = max(self.requested_width or 0, max((len(str(o)) + 3 for o in self.options), default=12), max((len(line) + 1 for line in lines), default=1))
        y = self.start_y if self.start_y + needed_h <= screen_h else 0
        x = self.start_x if self.start_x + needed_w <= screen_w else 0
        self.height = max(1, min(needed_h, screen_h - y))
        self.width = max(1, min(needed_w, screen_w - x))
        geometry = (self.height, self.width, y, x)
        if geometry != self._geometry:
            self.window = curses.newwin(*geometry)
            self.window.keypad(True)
            self._geometry = geometry

    def display(self):
        self._layout()
        self.stdscr.clear()
        self.stdscr.refresh()
        self.window.clear()
        if not self.options:
            write(self.window, 0, 0, "No options")
            self.window.refresh()
            return
        self.select = max(0, min(self.select, len(self.options) - 1))
        lines = self._header()
        header_rows = min(len(lines), max(0, self.height - min(len(self.options), self.height) - 1))
        for y, line in enumerate(lines[:header_rows]):
            write(self.window, y, 0, line)
        first_row = header_rows + (1 if header_rows else 0)
        visible = max(1, self.height - first_row)
        start = max(0, min(self.select - visible + 1, len(self.options) - visible))
        for y, idx in enumerate(range(start, min(len(self.options), start + visible)), first_row):
            write(self.window, y, 1 if self.width > 2 else 0, self.options[idx], curses.A_REVERSE if idx == self.select else 0)
        self.window.refresh()

        if self._sidebar_width:
            screen_h, screen_w = self.stdscr.getmaxyx()
            panel = curses.newwin(screen_h, self._sidebar_width, 0, screen_w - self._sidebar_width)
            draw_live_map(panel, *self._sidebar_data)

    def navigate(self):
        if not self.options:
            return None
        self.display()
        while True:
            key = self.window.getch()
            if key in CONSOLE_KEYS and self.on_console is not None:
                self.on_console()
            elif key == curses.KEY_UP:
                self.select = (self.select - 1) % len(self.options)
            elif key == curses.KEY_DOWN:
                self.select = (self.select + 1) % len(self.options)
            elif key in (10, 13, 32, curses.KEY_ENTER):
                return self.select
            elif key in (27, ord("q")):
                return None
            elif ord("1") <= key <= ord("9"):
                index = key - ord("1")
                if index < len(self.options):
                    self.select = index
            self.display()
