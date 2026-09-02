"""Unit tests for Agnosia core modules."""
import curses
import json
import unittest
from unittest.mock import MagicMock, patch

import numpy as np

from config import BASEDIR, LEVELS_DIR, DEFAULT_CONFIG, INVENTORY_ITEMS
from entity import Entity, Player
from level import Level
from maze import Maze
from menu import Menu


class EntityTests(unittest.TestCase):
    def test_default_position_and_direction(self):
        e = Entity()
        self.assertEqual(e.position, [1, 1])
        self.assertEqual(e.direction, [1, 0])

    def test_custom_position_and_direction(self):
        e = Entity(position=[3, 7], direction=[0, 1])
        self.assertEqual(e.position, [3, 7])
        self.assertEqual(e.direction, [0, 1])

    def test_move_straight(self):
        e = Entity(position=[2, 2], direction=[1, 0])
        e.move()
        self.assertEqual(e.position, [3, 2])
        e.move()
        self.assertEqual(e.position, [4, 2])

    def test_move_diagonal(self):
        e = Entity(position=[1, 1], direction=[1, 1])
        e.move()
        self.assertEqual(e.position, [2, 2])

    def test_turn_left(self):
        e = Entity(position=[1, 1], direction=[1, 0])  # facing down (row+)
        e.turn([-1, 1])  # left
        self.assertEqual(e.direction, [0, 1])  # facing right (col+)

    def test_turn_right(self):
        e = Entity(position=[1, 1], direction=[1, 0])
        e.turn([1, -1])  # right
        self.assertEqual(e.direction, [0, -1])  # facing left

    def test_turn_back(self):
        e = Entity(position=[1, 1], direction=[1, 0])
        e.turn_back()
        self.assertEqual(e.direction, [-1, 0])

    def test_look_forward(self):
        e = Entity(position=[2, 3], direction=[1, 0])
        fwd = e.look_forward()
        self.assertEqual(fwd, (3, 3))

    def test_look_around(self):
        e = Entity(position=[2, 2], direction=[1, 0])
        around = e.look_around()
        # [front_row, front_col, right_row, right_col, left_row, left_col, back_row, back_col]
        self.assertEqual(around, [3, 2, 2, 1, 2, 3, 1, 2])

    def test_swap(self):
        e = Entity(direction=[1, 0])
        e.swap()
        self.assertEqual(e.direction, [0, 1])
        e.swap()
        self.assertEqual(e.direction, [1, 0])


class PlayerTests(unittest.TestCase):
    def test_default_inventory(self):
        p = Player()
        self.assertEqual(p.sign, "P")
        self.assertIn("maps", p.inventory)
        self.assertIn("compasses", p.inventory)
        self.assertIn("scanners", p.inventory)
        self.assertIn("locators", p.inventory)

    def test_inheritance(self):
        p = Player(position=[5, 5], direction=[0, 1])
        self.assertIsInstance(p, Entity)
        p.move()
        self.assertEqual(p.position, [5, 6])

    def test_look_around_matches_entity(self):
        p = Player(position=[2, 2], direction=[0, 1])
        around = p.look_around()
        self.assertEqual(around, [2, 3, 3, 2, 1, 2, 2, 1])


class MazeTests(unittest.TestCase):
    def test_default_config(self):
        m = Maze(5, 5)
        self.assertEqual(m.config, DEFAULT_CONFIG)

    def test_dimensions(self):
        m = Maze(11, 21)
        self.assertEqual(len(m.maze), 11)
        for row in m.maze:
            self.assertEqual(len(row), 21)

    def test_start_and_end_present(self):
        m = Maze(11, 21)
        start = m.get_object_position("S")
        end = m.get_object_position("E")
        self.assertIsNotNone(start)
        self.assertEqual(start, [1, 1])
        self.assertIsNotNone(end)
        self.assertEqual(end, [m.rows - 2, m.cols - 1])

    def test_start_is_path(self):
        m = Maze(7, 13)
        start = m.get_object_position("S")
        self.assertEqual(m.maze[start[0]][start[1]], "S")
        self.assertTrue(m.config["path"] in m.maze[start[0]])

    def test_generates_reproducible_with_seed(self):
        import random
        random.seed(42)
        m1 = Maze(11, 21)
        random.seed(42)
        m2 = Maze(11, 21)
        for r in range(m1.rows):
            for c in range(m1.cols):
                self.assertEqual(m1.maze[r][c], m2.maze[r][c])

    def test_is_end_true(self):
        m = Maze(11, 21)
        end = m.get_object_position("E")
        self.assertTrue(m.is_end(end))

    def test_is_end_false(self):
        m = Maze(11, 21)
        self.assertFalse(m.is_end([1, 1]))

    def test_copy_is_independent(self):
        m = Maze(5, 5)
        c = m.copy()
        c[0][0] = "X"
        self.assertNotEqual(m.maze[0][0], "X")

    def test_has_no_isolated_walls(self):
        m = Maze(21, 41)
        from collections import deque
        start = m.get_object_position("S")
        visited = set()
        q = deque([start])
        while q:
            r, c = q.popleft()
            key = (r, c)
            if key in visited:
                continue
            visited.add(key)
            for dr, dc in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < m.rows and 0 <= nc < m.cols:
                    if m.maze[nr][nc] != m.config["wall"]:
                        q.append((nr, nc))
        for r in range(m.rows):
            for c in range(m.cols):
                if m.maze[r][c] != m.config["wall"]:
                    self.assertIn((r, c), visited,
                                  f"Unreachable non-wall at ({r},{c})")


class LevelTests(unittest.TestCase):
    def test_from_json(self):
        data = {
            "name": "Test Level",
            "maze": {"rows": 7, "cols": 13},
            "description": "A test",
            "difficulty": 3,
            "timelimit": 120,
        }
        lv = Level.from_json(data)
        self.assertEqual(lv.name, "Test Level")
        self.assertEqual(lv.maze.rows, 7)
        self.assertEqual(lv.maze.cols, 13)
        self.assertEqual(lv.difficulty, 3)
        self.assertEqual(lv.timelimit, 120)

    def test_from_json_defaults(self):
        data = {"name": "X", "maze": {"rows": 5, "cols": 5}}
        lv = Level.from_json(data)
        # from_json passes no description → constructor keeps its default
        self.assertEqual(lv.description, "No description")
        self.assertEqual(lv.difficulty, 0)
        self.assertEqual(lv.timelimit, 0)

    def test_full_constructor(self):
        lv = Level("Foo", (5, 5), "desc", difficulty=1, timelimit=60)
        self.assertEqual(lv.maze.rows, 5)
        self.assertEqual(lv.maze.cols, 5)
        self.assertEqual(lv.difficulty, 1)
        self.assertEqual(lv.timelimit, 60)


class ConfigTests(unittest.TestCase):
    def test_basedir(self):
        self.assertTrue(BASEDIR.exists())

    def test_levels_dir(self):
        self.assertTrue(LEVELS_DIR.exists())

    def test_inventory_items(self):
        self.assertEqual(len(INVENTORY_ITEMS), 4)
        self.assertIn("maps", INVENTORY_ITEMS)
        self.assertIn("compasses", INVENTORY_ITEMS)
        self.assertIn("scanners", INVENTORY_ITEMS)
        self.assertIn("locators", INVENTORY_ITEMS)

    def test_default_config(self):
        self.assertEqual(DEFAULT_CONFIG["wall"], "#")
        self.assertEqual(DEFAULT_CONFIG["path"], " ")
        self.assertEqual(DEFAULT_CONFIG["start"], "S")
        self.assertEqual(DEFAULT_CONFIG["end"], "E")


class MenuTests(unittest.TestCase):
    def setUp(self):
        self.patcher_newwin = patch("curses.newwin")
        self.mock_newwin = self.patcher_newwin.start()
        self.addCleanup(self.patcher_newwin.stop)
        self.mock_stdscr = MagicMock()
        self.mock_stdscr.getyx.return_value = (0, 0)

    def _make_mock_window(self, key_sequence):
        mq = list(key_sequence)
        w = MagicMock()
        w.keypad = MagicMock()
        w.getch = MagicMock(side_effect=lambda: mq.pop(0) if mq else -1)
        w.clear = MagicMock()
        w.addstr = MagicMock()
        w.refresh = MagicMock()
        w.hline = MagicMock()
        w.getyx.return_value = (0, 0)
        return w

    def test_navigate_selects_on_enter(self):
        w = self._make_mock_window([curses.KEY_DOWN, 10])
        self.mock_newwin.return_value = w
        menu = Menu(["A", "B", "C"], stdscr=self.mock_stdscr)
        choice = menu.navigate()
        self.assertEqual(choice, 1)

    def test_navigate_selects_on_digit(self):
        w = self._make_mock_window([ord("2")])
        self.mock_newwin.return_value = w
        menu = Menu(["A", "B", "C"], stdscr=self.mock_stdscr)
        choice = menu.navigate()
        self.assertEqual(choice, 1)

    def test_navigate_wraps_around(self):
        w = self._make_mock_window([
            curses.KEY_UP,
            curses.KEY_DOWN,
            10,
        ])
        self.mock_newwin.return_value = w
        menu = Menu(["A", "B"], stdscr=self.mock_stdscr)
        choice = menu.navigate()
        self.assertEqual(choice, 0)

    def test_navigate_ignores_invalid_keys(self):
        w = self._make_mock_window([-1, -1, 10])
        self.mock_newwin.return_value = w
        menu = Menu(["A"], stdscr=self.mock_stdscr)
        choice = menu.navigate()
        self.assertEqual(choice, 0)

    def test_display_calls_window_methods(self):
        w = self._make_mock_window([])
        self.mock_newwin.return_value = w
        menu = Menu(["X", "Y"], stdscr=self.mock_stdscr, title="T")
        menu.display()
        w.clear.assert_called_once()
        w.addstr.assert_called()
        w.refresh.assert_called_once()


class NumpyMazeTests(unittest.TestCase):
    def test_maze_copy_to_numpy(self):
        m = Maze(5, 5)
        arr = np.array(m.copy())
        self.assertEqual(arr.shape, (5, 5))
        self.assertTrue(np.all(arr == m.maze))


if __name__ == "__main__":
    unittest.main()
