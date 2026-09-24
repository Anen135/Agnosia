import curses
import unittest
from unittest.mock import Mock, patch

from dev_console import DeveloperConsole, execute_command
from entity import Player
from menu import Menu
from test_stability import Screen
from display import draw_live_map
from maze import Maze


class ConsoleTests(unittest.TestCase):
    def test_mapmode_commands_and_validation(self):
        settings = DeveloperConsole()
        for command, expected in (("mapmode on", True), ("mapmode on", True),
                                  ("mapmode off", False), ("mapmode", True)):
            execute_command(command, None, settings)
            self.assertEqual(settings.map_mode, expected)
        self.assertIn("Usage", execute_command("mapmode invalid", None, settings))
        self.assertTrue(settings.map_mode)

    def test_live_map_tracks_player_without_mutating_maze(self):
        maze = Maze(21, 41)
        before = maze.copy()
        for position in ([1, 1], [19, 39], [10, 20]):
            screen = Screen(6, 12)
            draw_live_map(screen, maze.maze, position)
            rows = [text for y, _, text, _ in screen.writes if y > 0]
            self.assertEqual("".join(rows).count("@"), 1)
        self.assertEqual(maze.maze, before)

    def test_sidebar_reserves_space_and_can_be_disabled(self):
        maze = Maze(11, 21)
        windows = []
        def create(h, w, y, x):
            window = Screen(h, w)
            windows.append((window, x, w))
            return window
        with patch("curses.newwin", side_effect=create):
            menu = Menu(["GO", "INVENTORY"], stdscr=Screen(24, 80),
                        sidebar=lambda: (maze.maze, [1, 1]))
            menu.display()
            self.assertLess(menu.width, windows[-1][1])
            self.assertEqual(windows[-1][1] + windows[-1][2], 80)
            menu.sidebar = None
            menu.display()
            self.assertEqual(menu._sidebar_width, 0)

    def test_give_single_default_and_all(self):
        player = Player()
        execute_command("give maps 5", player)
        self.assertEqual(player.inventory["maps"], 8)
        execute_command(" GIVE LOCATORS ", player)
        self.assertEqual(player.inventory["locators"], 3)
        before = player.inventory.copy()
        execute_command("give all 10", player)
        self.assertEqual(player.inventory, {name: count + 10 for name, count in before.items()})

    def test_invalid_commands_never_modify_inventory(self):
        player = Player()
        before = player.inventory.copy()
        for command in ("give", "give maps 2 extra", "give unknown 2", "give maps -1",
                        "give maps 0", "give maps 10001", "give maps abc",
                        "give all 1.5", "give maps " + "9" * 5000, "unknown", "", "help"):
            with self.subTest(command=command[:60]):
                execute_command(command, player)
                self.assertEqual(player.inventory, before)

    def test_no_active_level(self):
        self.assertIn("Start a level", execute_command("give all 5", None))
        self.assertIn("maps", execute_command("help", None))

    def test_console_input_backspace_resize_and_close(self):
        player = Player()
        keys = [*map(ord, "give maps 9"), curses.KEY_BACKSPACE, ord("2"),
                curses.KEY_RESIZE, 10, curses.KEY_F12]
        screen = Screen(4, 18, keys)
        console = DeveloperConsole()
        console.open(screen, player)
        self.assertEqual(player.inventory["maps"], 5)
        self.assertIn("Added 2 to maps.", console.output)

    def test_menu_console_returns_to_same_selection(self):
        callback = Mock()
        screen = Screen()
        window = Screen(keys=[curses.KEY_DOWN, ord("~"), 10])
        with patch("curses.newwin", return_value=window):
            menu = Menu(["A", "B"], stdscr=screen, on_console=callback)
            self.assertEqual(menu.navigate(), 1)
        callback.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
