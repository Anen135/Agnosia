import json
import unittest
from unittest.mock import MagicMock, patch

import numpy as np

from config import LEVELS_DIR
from display import draw_live_map, draw_map_panel
from entity import Wanderer, Player
from game import Game
from level import Level
from maze import Maze
from test_stability import Screen


class MonsterTests(unittest.TestCase):
    def test_level_configuration(self):
        tutorial = Level.from_json(json.loads((LEVELS_DIR / "l0.json").read_text()))
        next_level = Level.from_json(json.loads((LEVELS_DIR / "l1.json").read_text()))
        self.assertIsNone(tutorial.monster)
        self.assertEqual(next_level.monster, "wanderer")
        with self.assertRaises(ValueError):
            Level("bad", (5, 5), monster="unknown")

    def test_spawn_excludes_start_exit_and_walls(self):
        maze = Maze(11, 21)
        for _ in range(100):
            monster = Wanderer.spawn(maze)
            row, col = monster.position
            self.assertEqual(maze.maze[row][col], maze.config["path"])
        self.assertIsNone(Wanderer.spawn(Maze(3, 3)))

    def test_random_walk_stays_on_adjacent_passages(self):
        maze = Maze(11, 21)
        before = maze.copy()
        monster = Wanderer.spawn(maze)
        for _ in range(500):
            row, col = monster.position
            monster.wander(maze)
            nr, nc = monster.position
            self.assertEqual(abs(nr - row) + abs(nc - col), 1)
            self.assertNotEqual(maze.maze[nr][nc], maze.config["wall"])
        self.assertEqual(maze.maze, before)

    def test_trapped_monster_stays_put(self):
        maze = Maze(5, 5)
        maze.maze = [list("#####") for _ in range(5)]
        maze.maze[2][2] = " "
        monster = Wanderer([2, 2])
        monster.wander(maze)
        self.assertEqual(monster.position, [2, 2])

    def controller(self, monster_position):
        game = Game.__new__(Game)
        game.maze = Maze(5, 5)
        game.maze.maze[1][2] = " "
        game.player = Player([1, 1], [0, 1])
        game.monster = Wanderer(monster_position)
        game.game_on = True
        game.stdscr = MagicMock()
        game.print_msg = MagicMock()
        game.message = ""
        game.game_menu = MagicMock()
        return game

    def test_player_walks_into_monster_before_it_can_move(self):
        game = self.controller([1, 2])
        game.game_menu.navigate.return_value = 0
        with patch.object(game.monster, "wander") as wander:
            game.game_controller(
                np.array(game.maze.copy()), game.player, game.maze.config
            )
        wander.assert_not_called()
        self.assertFalse(game.game_on)
        game.print_msg.assert_called_once_with("CAUGHT.")

    def test_monster_can_walk_into_player(self):
        game = self.controller([1, 2])
        with patch("entity.random.choice", return_value=[1, 1]):
            game._advance_monster(game.player)
        self.assertFalse(game.game_on)

    def test_turns_and_blocked_moves_advance_but_inventory_does_not(self):
        for action in (0, 1, 2, 3, 4, 5, None):
            game = self.controller([3, 3])
            game.player.direction = [-1, 0]
            game.inventory_controller = MagicMock()
            game.game_menu.navigate.return_value = action
            with patch.object(game.monster, "wander") as wander:
                game.game_controller(
                    np.array(game.maze.copy()), game.player, game.maze.config
                )
            self.assertEqual(wander.call_count, 1 if action in (0, 1, 2, 3) else 0)

    def test_map_views_have_no_legend_and_item_has_no_entities(self):
        maze = Maze(11, 21)
        before = maze.copy()
        screen = Screen(24, 80)
        draw_live_map(screen, maze.maze, [1, 1], [1, 2])
        text = "".join(line for _, _, line, _ in screen.writes)
        self.assertEqual(text.count("@"), 1)
        self.assertEqual(text.count("M"), 1)
        self.assertNotIn("player", text.lower())
        draw_map_panel(screen, maze.maze, [1, 1], maze.config, [0, 0])
        text = "".join(line for _, _, line, _ in screen.writes)
        self.assertNotIn("@", text)
        self.assertNotIn("M", text)
        self.assertNotIn("scroll", text.lower())
        self.assertEqual(maze.maze, before)


if __name__ == "__main__":
    unittest.main()
