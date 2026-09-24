"""Bounded drawing operations shared by terminal views."""
import curses


def write(window, y, x, text, attr=0):
    height, width = window.getmaxyx()
    if not (0 <= y < height and 0 <= x < width - 1):
        return
    text = str(text).split("\n", 1)[0][:width - x - 1]
    if not text:
        return
    try:
        window.addstr(y, x, text, attr)
    except curses.error:
        # The terminal may have shrunk between measuring and writing.
        pass


def show_message(screen, text, attr=0):
    screen.clear()
    for y, line in enumerate(str(text).splitlines()):
        write(screen, y, 0, line, attr)
    screen.refresh()
