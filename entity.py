class Entity:
    """Base entity with position and direction."""

    def __init__(self, position=None, direction=None):
        if position is None:
            position = [1, 1]
        if direction is None:
            direction = [1, 0]
        self.position = list(position)
        self.direction = list(direction)
        self.sign = None
        self.name = ""

    def move(self):
        self.position[0] += self.direction[0]
        self.position[1] += self.direction[1]

    def turn_back(self):
        self.direction[0] = -self.direction[0]
        self.direction[1] = -self.direction[1]

    def swap(self):
        self.direction[0], self.direction[1] = self.direction[1], self.direction[0]

    def turn(self, side=None):
        """Turn left or right. side=[1,-1] → right, [-1,1] → left."""
        if side is None:
            side = [1, -1]
        self.swap()
        self.direction[0] = side[0] * self.direction[0]
        self.direction[1] = side[1] * self.direction[1]

    def look_forward(self):
        return (
            self.position[0] + self.direction[0],
            self.position[1] + self.direction[1],
        )

    def look_around(self):
        """Return all 8 cells around the entity in [front, right, left, back] order."""
        d = self.direction
        return [
            self.position[0] + d[0],       # front (row)
            self.position[1] + d[1],       # front (col)
            self.position[0] + d[1],       # right (row)
            self.position[1] - d[0],       # right (col)
            self.position[0] - d[1],       # left (row)
            self.position[1] + d[0],       # left (col)
            self.position[0] - d[0],       # back (row)
            self.position[1] - d[1],       # back (col)
        ]


class Player(Entity):
    """Player entity with inventory and game state."""

    def __init__(self, position=None, direction=None):
        super().__init__(position, direction)
        self.sign = "P"
        self.inventory = {
            "maps": 3,
            "compasses": 2,
            "scanners": 2,
            "locators": 2,
        }
        self.steps = 0
