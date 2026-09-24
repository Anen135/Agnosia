"""Regression tests for inventory, terminal geometry and degraded resources."""
import curses
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import game
from config import DEFAULT_CONFIG
from display import draw_map_panel
from entity import Player
from inventory import use_map, use_compass, use_scanner, use_locator
from maze import Maze
from menu import Menu


class Screen:
    def __init__(self, height=24, width=80, keys=()):
        self.height, self.width = height, width
        self.keys = iter(keys)
        self.writes = []

    def getmaxyx(self):
        return self.height, self.width

    def addstr(self, y, x, text, attr=0):
        assert 0 <= y < self.height
        assert 0 <= x < self.width
        assert x + len(text) < self.width
        self.writes.append((y, x, text, attr))

    def clear(self):
        self.writes.clear()

    def refresh(self):
        pass

    def keypad(self, flag):
        pass

    def nodelay(self, flag):
        pass

    def getch(self):
        return next(self.keys)


class StabilityTests(unittest.TestCase):
    def test_map_supports_lists_and_numpy_without_mutation(self):
        original = Maze(21, 41).maze
        for maze in (original, np.array(original)):
            before = np.array(maze).copy()
            screen = Screen(8, 16)
            # Player is outside this viewport: no negative-index marker or crash.
            draw_map_panel(screen, maze, [1, 1], DEFAULT_CONFIG, [999, 999])
            np.testing.assert_array_equal(maze, before)
            self.assertFalse(any("O" in text for _, _, text, _ in screen.writes))
            draw_map_panel(screen, maze, [1, 1], DEFAULT_CONFIG, [0, 0])
            self.assertFalse(any("O" in text for _, _, text, _ in screen.writes))
            np.testing.assert_array_equal(maze, before)

    def test_map_scroll_and_resize_consume_one_item(self):
        player = Player()
        screen = Screen(5, 10, [curses.KEY_RIGHT, curses.KEY_DOWN, curses.KEY_RESIZE, ord("q")])
        maze = Maze(21, 41)
        before = maze.copy()
        use_map(screen, player, maze, maze.config)
        self.assertEqual(player.inventory["maps"], 2)
        self.assertEqual(maze.maze, before)

    def test_failed_map_render_does_not_consume_item(self):
        player = Player()
        maze = Maze(5, 5)
        with patch("inventory.draw_map_panel", side_effect=curses.error):
            with self.assertRaises(curses.error):
                use_map(Screen(), player, maze, maze.config)
        self.assertEqual(player.inventory["maps"], 3)

    def test_all_items_and_empty_inventory(self):
        for item, action in (("compasses", use_compass), ("scanners", use_scanner), ("locators", use_locator)):
            player = Player()
            player.inventory[item] = 1
            screen = Screen(2, 8, [10, 10])
            action(screen, player)
            action(screen, player)
            self.assertEqual(player.inventory[item], 0)
        player.inventory["maps"] = 0
        use_map(Screen(2, 8, [10]), player, None, None)
        self.assertEqual(player.inventory["maps"], 0)

    def test_menu_small_terminal_and_resize_keeps_selection_visible(self):
        screen = Screen(24, 80)
        def newwin(h, w, y, x):
            self.assertLessEqual(h + y, screen.height)
            self.assertLessEqual(w + x, screen.width)
            return Screen(h, w)
        with patch("curses.newwin", side_effect=newwin):
            menu = Menu([f"Option {i}" for i in range(20)], stdscr=screen,
                        content="Long header" * 20, start_x=10, start_y=10)
            for h, w in ((3, 12), (1, 1), (30, 100)):
                screen.height, screen.width = h, w
                menu.select = 19
                menu.display()
                if w > 1:
                    self.assertTrue(any(attr == curses.A_REVERSE for _, _, _, attr in menu.window.writes))

    def test_empty_menu_and_escape(self):
        with patch("curses.newwin", return_value=Screen(keys=[27])):
            self.assertIsNone(Menu([], stdscr=Screen()).navigate())
            self.assertIsNone(Menu(["A"], stdscr=Screen()).navigate())

    def test_level_loader_skips_bad_files_and_uses_contiguous_indices(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / "l0.json").write_text("{broken", encoding="utf-8")
            (folder / "l1.json").write_text(json.dumps({"name": "Good", "maze": {"rows": 5, "cols": 7}}), encoding="utf-8")
            with patch.object(game, "LEVELS_DIR", folder), patch.object(game, "_LEVEL_CACHE", {}):
                with self.assertLogs("game", level="WARNING"):
                    levels = game._load_levels()
                self.assertEqual(list(levels), [0])
                self.assertEqual(levels[0].name, "Good")

    def test_missing_levels_get_playable_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(game, "LEVELS_DIR", Path(directory)), patch.object(game, "_LEVEL_CACHE", {}):
                with self.assertLogs("game", level="WARNING"):
                    levels = game._load_levels()
                self.assertIsNotNone(levels[0].maze.get_object_position("E"))

    def test_invalid_maze_dimensions(self):
        for dimensions in ((0, 5), (4, 5), (5, 2), (5, 99999), (True, 5), (5, "7")):
            with self.subTest(dimensions=dimensions), self.assertRaises(ValueError):
                Maze(*dimensions)

    def test_movement_cannot_wrap_or_leave_map(self):
        controller = game.Game.__new__(game.Game)
        controller.game_menu = MagicMock()
        controller.game_menu.navigate.return_value = 0
        controller.message = ""
        layer = np.full((3, 3), " ")
        for position, direction in (([0, 0], [-1, 0]), ([2, 2], [1, 0]), ([0, 0], [0, -1]), ([2, 2], [0, 1])):
            player = Player(position, direction)
            controller.game_controller(layer, player, DEFAULT_CONFIG)
            self.assertEqual(player.position, position)
            self.assertIn("wall", controller.message)

    def test_audio_failure_does_not_abort_and_stop_works_when_disabled(self):
        controller = game.Game.__new__(game.Game)
        controller.music_mode = True
        with patch.object(game, "PlaySound", side_effect=RuntimeError("no audio")), patch.object(Path, "is_file", return_value=True):
            with self.assertLogs("game", level="WARNING"):
                controller.play_sound("test.wav")
        self.assertFalse(controller.music_mode)
        with patch.object(game, "PlaySound") as sound:
            controller.stop_sound()
            sound.assert_called_once_with(None, 0)

    def test_game_session_initializes_map_context_and_refreshes_inventory(self):
        screen = MagicMock()
        screen.getmaxyx.return_value = (30, 100)
        window = MagicMock()
        window.getmaxyx.return_value = (30, 100)
        with patch("curses.newwin", return_value=window), patch("curses.curs_set"), patch("curses.has_colors", return_value=False):
            controller = game.Game(screen)
        controller.game_menu.navigate = MagicMock(side_effect=[4, 5])
        # Real inventory dispatcher opens map, compass, then returns.
        with patch("curses.newwin", return_value=window), patch.object(Menu, "navigate", side_effect=[0, 1, 4]), patch("inventory.draw_map_panel", return_value=(screen, (0, 0))):
            screen.getch.side_effect = [10, ord("q"), 10]
            controller.game_loop()
        self.assertEqual(controller.player.inventory["maps"], 2)
        self.assertEqual(controller.player.inventory["compasses"], 1)
        self.assertIn("MAPS: 2", controller.inventory_menu.options)
        self.assertIn("COMPASSES: 1", controller.inventory_menu.options)
        self.assertIs(controller.config, controller.maze.config)


if __name__ == "__main__":
    unittest.main()
