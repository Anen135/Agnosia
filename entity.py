class Player:
    def __init__(self, position=None, direction=None):
        if position is None:
            position = [1, 1]
        if direction is None:
            direction = [1, 0]
        self.sign = "P"
        self.position = position
        self.direction = direction
        self.inventory = {
            "maps": 0,
            "compasses": 0,
            "scanners": 0,
            "locators": 0
        }
        self.name = ""
        self.steps = 0
        self.level = 0
        self.settings = {
            "music": True,
        }
        

    def move(self):
        self.position = [self.position[0] + self.direction[0], self.position[1] + self.direction[1]]
    
    def turn(self, side=None):
        #[1,-1] - RIGHT, [-1,1] - LEFT
        if side is None:
            side = [1,-1]
        self.swap()
        self.direction = side[0] * self.direction[0], side[1] * self.direction[1]
            
    def look_forward(self):
        return self.position[0] + self.direction[0], self.position[1] + self.direction[1]
    
    def look_around(self): # Returns a list of all possible player movements
        return [self.position[0] + self.direction[0],
                self.position[1] + self.direction[1],
                self.position[0] + self.direction[1],
                self.position[1] - self.direction[0],
                self.position[0] - self.direction[1],
                self.position[1] + self.direction[0],
                self.position[0] - self.direction[0],
                self.position[1] - self.direction[1]]      
    
    def turn_back(self):
        self.direction = [-self.direction[0], -self.direction[1]]
    
    def swap(self):
        self.direction = [self.direction[1], self.direction[0]]
