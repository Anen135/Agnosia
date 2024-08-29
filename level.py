from maze import Maze
class Level:
    def __init__(self, name, maze, description="No description", monster=None, dificulty=0, timelimit=0, config=None):
        if config is None:
            config = {"wall": "#", "path": " ", "start": "S", "end": "E"}
        self.name = name
        self.description = description
        self.maze = Maze(maze[0], maze[1], config)
        self.monster = monster
        self.dificulty = dificulty
        self.timelimit = timelimit