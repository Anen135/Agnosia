import curses
from winsound import PlaySound
import numpy as np
from pathlib import Path

from config import BASEDIR, LEVELS_DIR, MUSIC_DIR, INVENTORY_ITEMS
from maze import Maze
from menu import Menu
from entity import Player
from level import Level
from display import draw_title, draw_game_map, draw_map_panel
from inventory import use_map, use_compass, use_scanner, use_locator, INVENTORY_ACTIONS

_LEVEL_CACHE: dict[int, Level] = {}


def _load_levels():
    if _LEVEL_CACHE:
        return _LEVEL_CACHE
    for idx, path in enumerate(sorted(LEVELS_DIR.glob("l*.json"))):
        with open(path, encoding="utf-8") as f:
            data = __import__("json").load(f)
        _LEVEL_CACHE[idx] = Level.from_json(data)
    return _LEVEL_CACHE


def _get_level_names():
    return [lv.name for lv in _load_levels().values()]


class Game:
    def __init__(self, stdscr: curses.window):
        self.stdscr = stdscr
        curses.curs_set(0)
        self._init_colors()

        self.music_mode = False
        self.game_on = False
        self.current_level = 0

        self.main_menu = Menu(
            ["START", "OPTIONS", "LEVELS", "QUIT"],
            content=self._title_banner(),
            stdscr=stdscr,
        )
        self.options_menu = Menu(
            ["BACK", f"MUSIC {'ON' if self.music_mode else 'OFF'}"],
            stdscr=stdscr,
            start_x=10,
            start_y=9,
        )
        self.game_menu = Menu(
            ["GO", "BACK", "LEFT", "RIGHT", "INVENTORY", "QUIT"],
            stdscr=stdscr,
            width=30,
            height=15,
        )
        self.levels_menu = Menu(
            _get_level_names(),
            title="LEVELS\n",
            stdscr=stdscr,
            start_x=10,
            start_y=10,
        )
        self.message = ""

    def _init_colors(self):
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)

    def _title_banner(self):
        return (
            "    :::      ::::::::  ::::    :::  ::::::::   :::::::: :::::::::::     :::    \n"
            "  :+: :+:   :+:    :+: :+:+:   :+: :+:    :+: :+:    :+:    :+:       :+: :+:   \n"
            " +:+   +:+  +:+        :+:+:+  +:+ +:+    +:+ +:+           +:+      +:+   +:+  \n"
            "+#++:++#++: :#:        +#+ +:+ +#+ +#+    +:+ +#++:++#++    +#+     +#++:++#++: \n"
            "+#+     +#+ +#+   +#+# +#+  +#+#+# +#+    +#+        +#+    +#+     +#+     +#+ \n"
            "+#+     #+# #+#    #+# #+#   #+#+# #+#    #+# #+#    #+#    #+#     #+#     #+# \n"
            "###     ###  ########  ###    ####  ########   ######## ########### ###     ### "
        )

    def play_sound(self, filename: str, flag: int = 9):
        if not self.music_mode:
            return
        path = MUSIC_DIR / filename
        PlaySound(str(path), flag)

    def stop_sound(self):
        if self.music_mode:
            PlaySound(None, 0)

    def _draw_inventory_menu(self, player: Player):
        items = [f"{k.upper()}: {v}" for k, v in player.inventory.items()] + ["BACK"]
        self.inventory_menu = Menu(items, stdscr=self.stdscr)
        self.inventory_menu.display()

    def main_loop(self):
        self.play_sound("Main_menu.wav")
        while True:
            self.stdscr.clear()
            self.main_menu.display()
            choice = self.main_menu.navigate()
            match choice:
                case 0:  # START
                    self.game_on = True
                    self.game_loop()
                case 1:  # OPTIONS
                    self.setting_controller()
                case 2:  # LEVELS
                    self.levels_controller()
                case 3:  # QUIT
                    break

    def game_loop(self):
        self.play_sound("Background.wav")
        level = _load_levels()[self.current_level]
        maze = level.maze
        layer = np.array(maze.copy())
        config = maze.config

        player = Player(maze.get_object_position("S"))
        self.player = player

        self.stdscr.clear()
        self.stdscr.addstr(f"Level starting: {level.name}\n\n")
        self.stdscr.getch()
        self.stdscr.clear()

        self.game_on = True
        while self.game_on:
            if maze.is_end(player.position):
                self.print_msg("YOU ESCAPED!")
                self.stdscr.getch()
                break

            layer[player.position[0], player.position[1]] = player.sign
            self.game_controller(layer, player, config)

    def game_controller(self, layer, player, config):
        while True:
            look = player.look_around()
            self.game_menu.content = self._where_walls(layer, look, config)
            self.game_menu.content += self.message
            self.message = ""
            self.game_menu.display()
            key = self.game_menu.navigate()
            match key:
                case 0:  # GO
                    dx, dy = player.look_forward()
                    if layer[dx, dy] == config["wall"]:
                        self.message = "You hit a wall\n"
                    else:
                        layer[player.position[0], player.position[1]] = config["path"]
                        player.move()
                case 1:  # BACK
                    player.turn_back()
                case 2:  # LEFT
                    player.turn([-1, 1])
                case 3:  # RIGHT
                    player.turn([1, -1])
                case 4:  # INVENTORY
                    self.inventory_controller()
                case 5:  # QUIT
                    self.game_on = False
                case _:
                    self.print_msg("Invalid input")
            break

    def _where_walls(self, layer, look, config):
        labels = ["front", "right", "left", "back"]
        msg = ""
        for i, label in enumerate(labels):
            row = look[i * 2]
            col = look[i * 2 + 1]
            if layer[row, col] == config["wall"]:
                msg += f"There's a wall to the {label}\n"
        return msg

    def inventory_controller(self):
        self.inventory_menu = Menu(
            [f"{k.upper()}: {v}" for k, v in self.player.inventory.items()] + ["BACK"],
            stdscr=self.stdscr,
        )
        while True:
            self.inventory_menu.display()
            idx = self.inventory_menu.navigate()
            if idx == len(self.player.inventory):
                break  # BACK
            item = INVENTORY_ITEMS[idx]
            action = INVENTORY_ACTIONS[item]
            if item == "maps":
                action(self.stdscr, self.player, self.maze, self.config)
            else:
                action(self.stdscr, self.player)

    def setting_controller(self):
        while True:
            self.stdscr.clear()
            self.options_menu.options = ["BACK", f"MUSIC {'ON' if self.music_mode else 'OFF'}"]
            self.options_menu.display()
            idx = self.options_menu.navigate()
            match idx:
                case 0:  # BACK
                    break
                case 1:  # MUSIC
                    self.music_mode = not self.music_mode
                    self.stop_sound()
                    self.play_sound("Main_menu.wav")

    def levels_controller(self):
        self.levels_menu.select = self.current_level
        self.levels_menu.display()
        self.current_level = self.levels_menu.navigate()

    def print_msg(self, string: str, attr: int = 0):
        self.stdscr.addstr(str(string), attr)
        self.stdscr.refresh()


def main(stdscr: curses.window):
    try:
        game = Game(stdscr)
        game.main_loop()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    curses.wrapper(main)
