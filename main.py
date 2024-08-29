import curses
from winsound import PlaySound
import numpy as np
# import time
from maze import Maze
from menu import Menu
from entity import Player
from os.path import abspath, dirname, join
from level import Level
# from ssetcolor import red
import json
from os import listdir


здесь = abspath(dirname(__file__))
титул = """
    :::      ::::::::  ::::    :::  ::::::::   :::::::: :::::::::::     :::     
  :+: :+:   :+:    :+: :+:+:   :+: :+:    :+: :+:    :+:    :+:       :+: :+:   
 +:+   +:+  +:+        :+:+:+  +:+ +:+    +:+ +:+           +:+      +:+   +:+  
+#++:++#++: :#:        +#+ +:+ +#+ +#+    +:+ +#++:++#++    +#+     +#++:++#++: 
+#+     +#+ +#+   +#+# +#+  +#+#+# +#+    +#+        +#+    +#+     +#+     +#+ 
#+#     #+# #+#    #+# #+#   #+#+# #+#    #+# #+#    #+#    #+#     #+#     #+# 
###     ###  ########  ###    ####  ########   ######## ########### ###     ### \n\n"""

class Game:
    def __init__(self, stdscr):
        self.maze = Maze(11*2-1, 21*2-1)
        self.config = self.maze.config
        self.music_mode = False
        self.game_on = False
        self.layer = self.maze.copy()
        self.player = Player(self.maze.get_object_position('S'))
        self.stdscr = stdscr
        Menu.stdscr = stdscr
        self.current_level = 0
        self.main_menu = Menu(stdscr, ["START", "OPTIONS", "LEVELS", "QUIT"])
        self.options_menu = Menu(stdscr, ["BACK", f"MUSIC {'ON' if self.music_mode else 'OFF'}"])
        self.game_menu = Menu(stdscr, ["GO", "BACK", "LEFT", "RIGHT", "INVENTORY", "QUIT"])
        self.inventory_menu = Menu(stdscr, [f"{key.upper()}: {value}" for key, value in self.player.inventory.items()]+["BACK"])
        self.levels_menu = Menu(stdscr, self.get_level_names(здесь + "\\levels"), title="LEVELS")
        self.message = ""
        self.colorset()
        curses.curs_set(0)
        
    # settings
    def colorset(self):
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)

    def background_music(self, path):
        # 0     - PLAYANDSTOP               # 1     - ASYNC
        # 2     - NODEFULT                  # 4     - MEMORY                    
        # 8     - LOOP                      # 9     - ON (1 + 8)                
        # 16    - NOSTOP                    # 64    - PURGE (not supported)     
        # 128   - NOWAIT (not supported)    # 65536 - ALIAS                     
        if self.music_mode:
            PlaySound(здесь + path, 9)
    
    @staticmethod
    def load_level(number):
        with open(f"{здесь}/levels/l{number}.json", 'r') as f:
            data = json.load(f)

        return Level(
            name=data["name"],
            description=data["description"],
            maze=data["maze"],
            monster=data["monster"],
            dificulty=data["dificulty"],
            timelimit=data["timelimit"]
        )
    
    @staticmethod
    def get_level_names(folder_path):
        level_names = []

        for filename in listdir(folder_path):
            with open(join(folder_path, filename), 'r', encoding='utf-8') as file:
                data = json.load(file)
                level_names.append(data['name'])

        return level_names
    
    #loop
    def game_loop(self):
        self.background_music("\\music\\Background.wav")
        while self.game_on: # step
            if self.maze.is_end(self.player.position):
                self.print("YOU ESCAPED!")
                self.stdscr.getch()
                break
            self.layer[self.player.position[0]][self.player.position[1]] = self.player.sign
            self.game_controller()

    def main_loop(self):
        while True:
            self.stdscr.clear()
            self.background_music("\\music\\Main_menu.wav")
            self.print(титул)
            self.main_menu.display()
            key = self.main_menu.navigate()
            match key:
                case 0: # start
                    self.game_on = True
                    self.game_loop()
                case 1: # options
                    self.setting_controller()
                case 2: # levels
                    self.levels_controller()
                case 3: # quit
                    break
    
    #display
    def display_inventory(self):
        self.stdscr.clear()
        self.inventory_menu.options = [f"{key.upper()}: {value}" for key, value in self.player.inventory.items()] + ["BACK"]
        self.inventory_menu.display()
    
    def display_options(self):
        self.stdscr.clear()
        self.options_menu.options = ["BACK", f"MUSIC {'ON' if self.music_mode else 'OFF'}"]
        self.options_menu.display()
    
    def display_game(self):
        self.stdscr.clear()
        self.print(self.whereWalls(self.player.look_around()))
        self.print(self.message)
        self.message = ""
        self.game_menu.display()
    
    def display_levels(self):
        self.stdscr.clear()
        self.levels_menu.select = self.current_level
        self.levels_menu.display()

        
    # controller
    def game_controller(self):
        while True:
            self.display_game()
            key = self.game_menu.navigate()
            match key:
                case 0: # GO
                    dx, dy = self.player.look_forward()
                    if self.layer[dx][dy] == self.config["wall"]:
                        self.message = "You hit a wall\n"
                    else:
                        self.layer[self.player.position[0]][self.player.position[1]] = self.config["path"]
                        self.player.move()
                case 1: # BACK
                    self.player.turn_back()
                case 2: # LEFT
                    self.player.turn([-1, 1])
                case 3: # RIGHT
                    self.player.turn([1, -1])
                case 4: # INVENTORY
                    self.inventory_controller()
                case 5: #QUIT
                    self.game_on = False
                case _:
                    self.print("Invalid input")
            break
    
    def inventory_controller(self):
        self.inventory_menu.select = 0
        while True:
            self.display_inventory()
            itemidx = self.inventory_menu.navigate()
            match itemidx:
                case 0: #MAP
                    self.use_map()
                case 1: #COMPASS
                    self.use_compass()
                case 2: #SCANNER
                    self.use_scanner()
                case 3: #LOCATOR
                    self.use_locator()
                case 4: #BACK
                    break

    def setting_controller(self):
        self.options_menu.select = 0
        while True:
            self.display_options()
            idx_option = self.options_menu.navigate() 
            match idx_option:
                case 0: # BACK
                    break
                case 1: # MUSIC
                    self.music_mode = not self.music_mode
                    PlaySound(None, 0)
                    self.background_music("\\music\\Main_menu.wav")
            
    def levels_controller(self):
        self.display_levels()
        self.current_level = self.levels_menu.navigate()
            
        
    #Curses methods
    def print(self, string, attr = 0):
        string = str(string)
        self.stdscr.addstr(string, attr)
        self.stdscr.refresh()        
        
    #Player actions
    def wait(func):
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self.stdscr.getch()
            self.stdscr.refresh()
        return wrapper

    def use_map(self):
        height, width = self.stdscr.getmaxyx()
        maze = np.array(self.maze.maze)
        
        x = width - 50
        y = 0

        panel = curses.newwin(23, 50, y, x)

        start_x = 0
        start_y = 0

        scroll_window_height = 10
        scroll_window_width = 20
        
        max_scroll_y = max(0, len(maze) - scroll_window_height)
        max_scroll_x = max(0, len(maze[0]) - scroll_window_width)
        
        while True:
            panel.clear()
            #panel.box()

            buffer = maze[start_y:start_y + scroll_window_height, start_x:start_x + scroll_window_width]

            panel.addstr(0, 0, f"Scroll: {start_y} {start_x} {max_scroll_y} {max_scroll_x}")

            for y, row in enumerate(buffer):
                for x, cell in enumerate(row):
                    if cell in ["S", "E"]: panel.addch(y + 1, x + 2, cell, curses.color_pair(1)) #noqa 800
                    else: panel.addch(y + 1, x + 2, cell) #noqa 800

            panel.refresh()

            # Handle user input for scrolling
            key = self.stdscr.getch()

            if key == curses.KEY_UP and start_y > 0:
                start_y -= 1
            elif key == curses.KEY_DOWN and start_y < max_scroll_y:
                start_y += 1
            elif key == curses.KEY_LEFT and start_x > 0:
                start_x -= 1
            elif key == curses.KEY_RIGHT and start_x < max_scroll_x:
                start_x += 1
            elif key == ord('q'):
                break
                
    @wait
    def use_compass(self):
        self.player.inventory["compasses"] -= 1
        self.stdscr.addstr("Voice: ")
        self.stdscr.addstr("There's darkness everywhere\n", curses.color_pair(1))
        match self.player.direction:
            case [1, 0]:
                self.stdscr.addstr("Compass: ")
                self.stdscr.addstr("0", curses.color_pair(1))
            case [0, 1]:
                self.stdscr.addstr("Compass: ")
                self.stdscr.addstr("1", curses.color_pair(1))
            case [-1, 0]:
                self.stdscr.addstr("Compass: ")
                self.stdscr.addstr("2", curses.color_pair(1))
            case [0, -1]:
                self.stdscr.addstr("Compass: ")
                self.stdscr.addstr("3", curses.color_pair(1))
        self.stdscr.addstr("\n")
                
    @wait
    def use_scanner(self):
        self.player.inventory["scanners"] -= 1
        self.stdscr.addstr("Voice: ")
        self.stdscr.addstr("These walls are familiar to you?\n", curses.color_pair(1))
        self.stdscr.addstr("Scanner: [")
        for i in self.player.look_around():
            self.stdscr.addstr(str(i))
        self.stdscr.addstr("]")
        self.stdscr.addstr("\n")
    
    @wait
    def use_locator(self):
        self.player.inventory["locators"] -= 1
        self.stdscr.addstr("Voice: ")
        self.stdscr.addstr("I can see you...\n", curses.color_pair(1))
        self.stdscr.addstr("Locator: ")
        self.stdscr.addstr(f"[{self.player.position[0]}{self.player.position[1]}]\n")
        self.stdscr.addstr("\n")
    
    def whereWalls(self, sides):
        to_sides = [self.layer[sides[i]][sides[i+1]] for i in range(0, len(sides), 2)] # Returns the blocks around. 0 = front, 1 = right, 2 = left, 3 = back
        message = ""
        if to_sides[0] == self.config["wall"]:
            message += "There's a wall in front\n"
        if to_sides[1] == self.config["wall"]:
            message += "There's a wall to the right\n"
        if to_sides[2] == self.config["wall"]:
            message += "There's a wall to the left\n"
        if to_sides[3] == self.config["wall"]:
            message += "There's a wall behind\n"
        return message

def main(stdscr):
    game = Game(stdscr)
    game.main_loop()

curses.wrapper(main)