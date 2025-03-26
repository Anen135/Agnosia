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
        maze = [[self.config['wall'] for _ in range(cols)] for _ in range(rows)]
        directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]

        stack = [(1, 1)]  # Начальная точка
        maze[1][1] = self.config['start']  # Открываем стартовую клетку

        while stack:
            x, y = stack[-1]  # Берём последний элемент из стека
            random.shuffle(directions)  # Перемешиваем направления

            for dx, dy in directions:
                nx, ny = x + dx, y + dy  # Новая позиция
                if 0 < nx < cols - 1 and 0 < ny < rows - 1 and maze[ny][nx] == self.config['wall']:
                    # Убираем стену между текущей и следующей ячейкой
                    maze[y + dy // 2][x + dx // 2] = self.config['path']
                    maze[ny][nx] = self.config['path']
                    stack.append((nx, ny))
                    break
            else:
                stack.pop()  # Если нет доступных направлений, удаляем из стека
        maze[rows - 2][cols - 1] = self.config['end']
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


if __name__ == '__main__':
    maze = Maze(11, 21)
    maze.display()
