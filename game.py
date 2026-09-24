import curses
import json
import logging

try:
    from winsound import PlaySound
except ImportError:
    PlaySound = None
import numpy as np

from config import LEVELS_DIR, MUSIC_DIR, INVENTORY_ITEMS
from menu import Menu
from entity import Player, Wanderer
from level import Level
from inventory import INVENTORY_ACTIONS
from terminal import show_message
from dev_console import DeveloperConsole

logger = logging.getLogger(__name__)

_LEVEL_CACHE: dict[int, Level] = {}


def _load_levels():
    if _LEVEL_CACHE:
        return _LEVEL_CACHE
    for path in sorted(LEVELS_DIR.glob("l*.json")):
        try:
            with open(path, encoding="utf-8") as f:
                level = Level.from_json(json.load(f))
        except (OSError, ValueError, KeyError, TypeError) as exc:
            logger.warning("Skipping invalid level %s: %s", path, exc)
            continue
        _LEVEL_CACHE[len(_LEVEL_CACHE)] = level
    if not _LEVEL_CACHE:
        logger.warning("No valid levels in %s; using a built-in level", LEVELS_DIR)
        _LEVEL_CACHE[0] = Level("Default level", (11, 21))
    return _LEVEL_CACHE


def _get_level_names():
    return [lv.name for lv in _load_levels().values()]


class Game:
    def __init__(self, stdscr: curses.window):
        self.stdscr = stdscr
        try:
            curses.curs_set(0)
        except curses.error:
            pass  # Some terminals cannot hide the cursor.
        self._init_colors()

        self.music_mode = False
        self.game_on = False
        self.current_level = 0
        self.console = DeveloperConsole()
        self.monster = None

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

        for menu in (
            self.main_menu,
            self.options_menu,
            self.game_menu,
            self.levels_menu,
        ):
            menu.on_console = self.open_console
        self.game_menu.sidebar = self.live_map_data

    def live_map_data(self):
        if self.game_on and self.console.map_mode and hasattr(self, "player"):
            return (
                self.maze.maze,
                self.player.position,
                self.monster.position if self.monster else None,
            )
        return None

    def open_console(self):
        player = getattr(self, "player", None) if self.game_on else None
        self.console.open(self.stdscr, player)
        if player is not None and hasattr(self, "inventory_menu"):
            self.inventory_menu.options = [
                f"{item.upper()}: {player.inventory.get(item, 0)}"
                for item in INVENTORY_ITEMS
            ] + ["BACK"]

    def _init_colors(self):
        if not curses.has_colors():
            return
        try:
            curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
            curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        except curses.error:
            logger.warning(
                "Terminal color setup unavailable; continuing without colors"
            )

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
        if not self.music_mode or PlaySound is None:
            return
        path = MUSIC_DIR / filename
        try:
            if not path.is_file():
                raise OSError(f"Sound file not found: {path}")
            PlaySound(str(path), flag)
        except (OSError, RuntimeError) as exc:
            logger.warning("Audio disabled: %s", exc)
            self.stop_sound()
            self.music_mode = False

    def stop_sound(self):
        if PlaySound is not None:
            try:
                PlaySound(None, 0)
            except (OSError, RuntimeError) as exc:
                logger.warning("Could not stop audio: %s", exc)

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
                case 3 | None:  # QUIT
                    break

    def game_loop(self):
        self.play_sound("Background.wav")
        level = _load_levels()[self.current_level]
        maze = level.maze
        layer = np.array(maze.copy())
        config = maze.config
        self.maze = maze
        self.config = config
        self.message = ""

        player = Player(maze.get_object_position(config["start"]))
        self.player = player
        self.monster = Wanderer.spawn(maze) if level.monster == "wanderer" else None

        self.stdscr.clear()
        self.print_msg(level.name)
        self.stdscr.getch()
        self.stdscr.clear()

        self.game_on = True
        while self.game_on:
            if maze.is_end(player.position):
                self.print_msg("YOU ESCAPED!")
                self.stdscr.getch()
                self.game_on = False
                self.current_level = min(
                    self.current_level + 1, len(_load_levels()) - 1
                )
                break

            layer[player.position[0], player.position[1]] = player.sign
            self.game_controller(layer, player, config)
        self.play_sound("Main_menu.wav")

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
                    if self._is_wall(layer, dx, dy, config):
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
                case 5 | None:  # QUIT
                    self.game_on = False
                case _:
                    self.print_msg("Invalid input")
            if key in (0, 1, 2, 3):
                self._advance_monster(player)
            break

    def _advance_monster(self, player):
        monster = getattr(self, "monster", None)
        if monster is None:
            return
        # Resolve a player stepping onto the monster before it can walk away.
        if player.position != monster.position:
            if self.maze.is_end(player.position):
                return
            monster.wander(self.maze)
        if player.position == monster.position:
            self.game_on = False
            self.print_msg("CAUGHT.")
            self.stdscr.getch()

    @staticmethod
    def _is_wall(layer, row, col, config):
        return (
            not (0 <= row < len(layer) and 0 <= col < len(layer[row]))
            or layer[row][col] == config["wall"]
        )

    def _where_walls(self, layer, look, config):
        labels = ["front", "right", "left", "back"]
        msg = ""
        for i, label in enumerate(labels):
            row = look[i * 2]
            col = look[i * 2 + 1]
            if self._is_wall(layer, row, col, config):
                msg += f"There's a wall to the {label}\n"
        return msg

    def inventory_controller(self):
        self.inventory_menu = Menu(
            [f"{k.upper()}: {v}" for k, v in self.player.inventory.items()] + ["BACK"],
            stdscr=self.stdscr,
            on_console=self.open_console,
            sidebar=self.live_map_data,
        )
        while True:
            self.inventory_menu.options = [
                f"{item.upper()}: {self.player.inventory.get(item, 0)}"
                for item in INVENTORY_ITEMS
            ] + ["BACK"]
            self.inventory_menu.display()
            idx = self.inventory_menu.navigate()
            if idx is None or idx == len(INVENTORY_ITEMS):
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
            self.options_menu.options = [
                "BACK",
                f"MUSIC {'ON' if self.music_mode else 'OFF'}",
            ]
            self.options_menu.display()
            idx = self.options_menu.navigate()
            match idx:
                case 0 | None:  # BACK
                    break
                case 1:  # MUSIC
                    self.music_mode = not self.music_mode
                    self.stop_sound()
                    self.play_sound("Main_menu.wav")

    def levels_controller(self):
        self.levels_menu.select = self.current_level
        self.levels_menu.display()
        selected = self.levels_menu.navigate()
        if selected is not None:
            self.current_level = selected

    def print_msg(self, string: str, attr: int = 0):
        show_message(self.stdscr, string, attr)


def main(stdscr: curses.window):
    game = Game(stdscr)
    try:
        game.main_loop()
    finally:
        game.stop_sound()


if __name__ == "__main__":
    curses.wrapper(main)
