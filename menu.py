import curses

class Menu:
    stdscr = None
    
    def __init__(self, options, title=None, stdscr=None, height=None, width=None, start_y=0, start_x=0, content=None):
        self.select = 0
        self.options = options
        self.title = title
        self.content = content

        # Initialize stdscr or use the provided one
        self.stdscr = stdscr or Menu.stdscr

        # Calculate the height and width of the menu window
        self.height = height or (len(options) + 2 + (1 if title else 0))
        self.width = width or max(len(option) for option in options) + 4
        x, y = self.stdscr.getyx()
        self.start_y = start_y or y
        self.start_x = start_x or x

        # Create a new window for the menu
        self.window = curses.newwin(self.height, self.width, self.start_y, self.start_x)
        self.window.keypad(True)

    def display(self):
        self.window.clear()  # Clear the window before displaying the menu

        if self.title:
            self.window.addstr(self.title, curses.A_VERTICAL)
            self.window.hline(curses.ACS_HLINE, self.width - 1)
        if self.content: 
            self.window.addstr(self.content)
        
        y, x = self.window.getyx()

        for idx, option in enumerate(self.options):
            if idx == self.select: self.window.addstr(idx + y+1, 1, option, curses.A_REVERSE)  # noqa: E701
            else: self.window.addstr(idx + y+1, 1, option)  # noqa: E701
        
        self.window.refresh()

    def navigate(self):
        length = len(self.options)
        while True:
            key = self.window.getch()
            if key == curses.KEY_UP and self.select > 0: self.select -= 1  # noqa: E701
            elif key == curses.KEY_DOWN and self.select < length - 1: self.select += 1  # noqa: E701
            elif key in [10, 13, 32, curses.KEY_ENTER]: return self.select  # noqa: E701

            self.display()