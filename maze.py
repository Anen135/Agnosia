import random

class Maze:
    def __init__(self, rows, cols, config=None):
        if config is None:
            config = {"wall": "#", "path": " ", "start": "S", "end": "E"}
        self.rows = rows
        self.cols = cols
        self.config = config
        self.maze = self.generate_maze(rows, cols)

    def generate_maze(self, rows, cols):
        maze = [[self.config["wall"] for _ in range(cols)] for _ in range(rows)]
        def is_valid_move(row, col):
            return 0 <= row < rows and 0 <= col < cols and maze[row][col] == self.config["wall"]
        def generate_path(row, col):
            directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
            random.shuffle(directions)
            for drow, dcol in directions:
                new_row, new_col = row + 2*drow, col + 2*dcol
                if is_valid_move(new_row, new_col):
                    maze[row+drow][col+dcol] = self.config["path"]
                    maze[new_row][new_col] = self.config["path"]
                    generate_path(new_row, new_col)
        start_row, start_col = 1, 1
        maze[start_row][start_col] = self.config["start"]  # Вход
        generate_path(start_row, start_col)
        maze[rows-2][cols-1] = self.config["end"]  # Выход
        return maze
        
    def get_object_position(self, object):
        return next(([i, row.index(object)] for i, row in enumerate(self.maze) if object in row), None)

    def display(self):
        for row in self.maze:
            print("".join(row))

    def copy(self):
        return [row[:] for row in self.maze]
    
    def is_end(self, position):
        return self.maze[position[0]][position[1]] == self.config["end"]