class Snake:
    def __init__(self, *args): # (self, snake_data: typing.Dict, our_snake: bool = False):
        if (len(args)) == 0:
            self.health = 0
            self.id = ""
            self.name = ""
            self.is_our_snake = False
            self.is_alive = False
            self.has_killed = False
            self.tiles = None
        else:
            self.health = args[0]['health']
            self.id = args[0]['id']
            self.name = args[0]['name']
            self.is_our_snake = False if len(args) == 1 else args[1]
            self.is_alive = True
            self.has_killed = False
            # The head is always the first index in the body
            self.tiles = [(posn['x'], posn['y']) for posn in args[0]['body']]

    def get_length(self):
        return len(self.tiles)
    
    def get_head(self):
        return self.tiles[0]
    
    def get_neck(self):
        return self.tiles[1]

    def copy(self) -> 'Snake':
        snake = Snake()
        snake.health = self.health
        snake.id = self.id
        snake.is_our_snake = self.is_our_snake
        snake.tiles = [tuple(t) for t in self.tiles]
        snake.is_alive = self.is_alive
        snake.has_killed = self.has_killed
        return snake
            
    # when we move the snake we just delete the tail and add a new head in the direction we are going
    # return value is a tuple of (did we grow?, new food list)
    def move(self, direction, food, editFood=False):
        
        self.health -= 1

        direction_mapping = {
            'up': (0, 1),
            'down': (0, -1),
            'left': (-1, 0),
            'right': (1, 0)
        }

        new_head = (
            self.tiles[0][0] + direction_mapping[direction][0],
            self.tiles[0][1] + direction_mapping[direction][1]
        )

        grown = False
        
        # Eating food        
        for food_dot in food:
            if new_head == food_dot:
                self.health = 100
                grown = True
                # remove food from the board
                if editFood:
                    food = food.remove(food_dot)
                break
        
        if grown:
            # grow the snake
            self.tiles.insert(0, new_head)
        else: 
            # move the snake
            self.tiles.insert(0, new_head)
            self.tiles.pop()
        
        return grown, food


    def kill_this_snake(self):
        self.tiles.clear()
        self.is_alive = False  