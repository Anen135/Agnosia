from maze import Maze
from config import DEFAULT_CONFIG


class Level:
    def __init__(self, name: str, maze: tuple[int, int], description: str = "No description", *, monster=None, difficulty: int = 0, timelimit: int = 0, config=None):
        if config is None:
            config = dict(DEFAULT_CONFIG)
        if monster not in (None, "wanderer"):
            raise ValueError("Unknown monster type")
        self.name = name
        self.description = description if description is not None else "No description"
        self.maze = Maze(maze[0], maze[1], config)
        self.monster = monster
        self.difficulty = difficulty
        self.timelimit = timelimit

    @classmethod
    def from_json(cls, data: dict):
        if not isinstance(data, dict) or not isinstance(data.get("maze"), dict):
            raise ValueError("Level must contain a maze object")
        if not isinstance(data.get("name"), str) or not data["name"].strip():
            raise ValueError("Level must have a nonempty name")
        return cls(
            name=data["name"],
            maze=(data["maze"]["rows"], data["maze"]["cols"]),
            description=data.get("description"),  # None → constructor default
            difficulty=data.get("difficulty", data.get("dificulty", 0)),
            timelimit=data.get("timelimit", 0),
            config=data.get("config"),
            monster=data.get("monster"),
        )
