import typing
import numpy as np

class Snake:
    def __init__(self, *args): # (self, snake_data: typing.Dict, our_snake: bool = False):
        if (len(args)) == 0:
            self.health = 0
            self.id = ""
            self.is_our_snake = False
            self.is_alive = False
            self.has_killed = False
            self.tiles = np.array([])
        else:
            self.health = args[0]['health']
            self.id = args[0]['id']
            self.is_our_snake = False if len(args) == 1 else args[1]
            self.is_alive = True
            self.has_killed = False
            # The head is always the first index in the body
            self.tiles = np.asarray([np.array([posn['x'], posn['y']]) for posn in args[0]['body']])


    def copy(self) -> 'Snake':
        snake = Snake()
        snake.health = self.health
        snake.id = self.id
        snake.is_our_snake = self.is_our_snake
        snake.tiles = self.tiles.copy()
        snake.is_alive = self.is_alive
        snake.has_killed = self.has_killed
        return snake


    # when we move the snake we just delete the tail and add a new head in the direction we are going
    # return value is a tuple of (did we grow?, new food list)
    def move(self, direction: str, food: np.ndarray) -> typing.Tuple[bool, np.ndarray]:
        self.health -= 1
        
        new_head = (-1, -1)
        match direction:
            case 'up':
                new_head = (self.tiles[0][0], self.tiles[0][1] + 1)
            case 'down':
                new_head = (self.tiles[0][0], self.tiles[0][1] - 1)
            case 'left':
                new_head = (self.tiles[0][0] - 1, self.tiles[0][1])
            case 'right':
                new_head = (self.tiles[0][0] + 1, self.tiles[0][1])
        
        grown = False
        # Eating food        
        for food_dot in food:
            if new_head[0] == food_dot[0] and new_head[1] == food_dot[1]:
                self.health = 100
                grown = True
                # remove food from the board
                food = np.delete(food, np.where((food == food_dot).all(axis=1)), axis=0)
                break
        
        if grown:
            # grow the snake
            self.tiles = np.roll(self.tiles, 1, axis=0)
            self.tiles[0] = np.asarray(new_head)
            self.tiles = np.insert(self.tiles, -1, self.tiles[-1].copy(), axis=0)
        else: 
            # move the snake
            self.tiles = np.roll(self.tiles, 1, axis=0)
            self.tiles[0] = np.asarray(new_head)
        
        return grown, food
