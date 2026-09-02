from maze import Maze
from config import DEFAULT_CONFIG


class Level:
    def __init__(
        self,
        name: str,
        maze: tuple[int, int],
        description: str = "No description",
        *,
        monster=None,
        difficulty: int = 0,
        timelimit: int = 0,
        config=None,
    ):
        if config is None:
            config = dict(DEFAULT_CONFIG)
        self.name = name
        self.description = description if description is not None else "No description"
        self.maze = Maze(maze[0], maze[1], config)
        self.monster = monster
        self.difficulty = difficulty
        self.timelimit = timelimit

    @classmethod
    def from_json(cls, data: dict):
        return cls(
            name=data["name"],
            maze=(data["maze"]["rows"], data["maze"]["cols"]),
            description=data.get("description"),  # None → constructor default
            difficulty=data.get("difficulty", 0),
            timelimit=data.get("timelimit", 0),
        )
