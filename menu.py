import curses
class Menu:
    stdscr = None
    def __init__(self, stdscr, options, title=None):
        self.select = 0
        self.options = options
        self.stdscr = stdscr
        self.title = title
    
    def display(self):
        if self.title:
            self.stdscr.addstr(0, 0, self.title)
            self.stdscr.hline(1, 0, curses.ACS_HLINE, curses.COLS - 1)  
        for idx, option in enumerate(self.options):
            if idx == self.select:
                self.stdscr.addstr(option+"\n", curses.A_REVERSE)
            else:
                self.stdscr.addstr(option+"\n")
        self.stdscr.refresh()
    
    def navigate(self):
        length = len(self.options)
        while True:
            key = self.stdscr.getch()
            if key == curses.KEY_UP and self.select > 0:
                self.select -= 1
            elif key == curses.KEY_DOWN and self.select < length - 1:
                self.select += 1
            elif key in [10, 13, 32, curses.KEY_ENTER]:
                return self.select
            self.clear_last_lines(length)
            self.display()
    
    def clear_last_lines(self, num_lines):
        current_y, current_x = self.stdscr.getyx()
        for _ in range(num_lines):
            if current_y != 0:  
                current_y -= 1
                self.stdscr.move(current_y, 0) 
                self.stdscr.clrtoeol()  
