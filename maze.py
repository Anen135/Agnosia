import random
from config import DEFAULT_CONFIG


class Maze:
    def __init__(self, rows: int, cols: int, config=None):
        if config is None:
            config = dict(DEFAULT_CONFIG)
        self.rows = rows
        self.cols = cols
        self.config = config
        self.maze = self._generate(rows, cols)

    def _generate(self, rows: int, cols: int):
        maze = [[self.config["wall"] for _ in range(cols)] for _ in range(rows)]
        directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]

        stack = [(1, 1)]
        maze[1][1] = self.config["start"]

        while stack:
            x, y = stack[-1]
            random.shuffle(directions)

            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 < nx < cols - 1 and 0 < ny < rows - 1 and maze[ny][nx] == self.config["wall"]:
                    maze[y + dy // 2][x + dx // 2] = self.config["path"]
                    maze[ny][nx] = self.config["path"]
                    stack.append((nx, ny))
                    break
            else:
                stack.pop()

        maze[rows - 2][cols - 1] = self.config["end"]
        return maze

    def get_object_position(self, obj: str):
        for i, row in enumerate(self.maze):
            if obj in row:
                return [i, row.index(obj)]
        return None

    def copy(self):
        return [row[:] for row in self.maze]

    def is_end(self, position):
        return self.maze[position[0]][position[1]] == self.config["end"]

    def display(self):
        for row in self.maze:
            print("".join(row))


if __name__ == "__main__":
    Maze(11, 21).display()
