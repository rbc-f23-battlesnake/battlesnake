import numpy as np
from data.snake import Snake

class Board:
    def __init__(self, *args):
        if len(args) == 0:
            self.width = 0
            self.height = 0
            self.food = np.array([])
            self.snakes = np.array([])
            self.turn = 0

        else:
            game_data = args[0]
            self.width = game_data['board']['width']
            self.height = game_data['board']['height']
            
            self.food = np.asarray([np.asarray([posn['x'], posn['y']]) for posn in game_data['board']['food']])
            self.turn = game_data['turn']
            
            # read in the snakes
            self.snakes = []
            
            for snake in game_data['board']['snakes']:
                if snake['id'] == game_data['you']['id']:
                    self.snakes.append(Snake(snake, True))
                else:
                    self.snakes.append(Snake(snake))

            self.snakes = np.asarray(self.snakes)


    def copy(self):
        # Fill values with the same data
        board = Board()
        
        board.width = self.width
        board.height = self.height
        board.food = self.food.copy()
        board.snakes = self.snakes.copy()
        board.turn = self.turn
        return board
    
    def get_largest_enemy_snake(self) -> Snake:
        for snake in self.snakes:
            enemy = None
            largest = 0
            if not snake.is_our_snake and snake.is_alive:
                if snake.get_length() > largest:
                    largest = snake.get_length()
                    enemy = snake
            return enemy

    def get_our_snake(self) -> Snake:
        return [snake for snake in self.snakes if snake.is_our_snake][0]
    
    
    def get_snake(self, snake_id: str):
        return [s for s in self.snakes if s.id == snake_id][0]
    
    
    def get_other_snakes(self, snake_id: str) -> np.ndarray:
        other_snakes = []
        for snake in self.snakes:
            if snake.is_alive and snake.id != snake_id:
                other_snakes.append(snake)
        return np.asarray(other_snakes)
    
    
    # Preferred method of moving the snake
    def move_snake(self, snake_id: str, direction: str) -> None:
        for snake in self.snakes:
            if snake.is_alive and snake.id == snake_id:
                has_grown, self.food = snake.move(direction, self.food)
                return has_grown


    # Checks all snakes to see if any should die :skull_emoji:
    # Requires all snakes on the board have already made their move
    def adjudicate_board(self):
        for snake in self.snakes:
            if not snake.is_alive:
                continue
            
            elif snake.health == 0:
                snake.tiles = np.ndarray([])
                snake.is_alive = False
                continue
            
            head = snake.tiles[0]
            # Check if snake collides with itself
            for tile in snake.tiles[2:]:
                if np.array_equal(head, tile):
                    snake.tiles = np.ndarray([])
                    snake.is_alive = False
                    break

            if not snake.is_alive:
                continue
            
            # Check boundaries
            if head[0] not in range(0, self.width) or head[1] not in range(0, self.height):
                snake.tiles = np.ndarray([])
                snake.is_alive = False
                continue          

            # Check collision with other snakes
            for other_snake in self.get_other_snakes(snake.id):
                if not other_snake.is_alive:
                    continue
                
                # Check head-on-head collision
                if np.array_equal(other_snake.tiles[0], head):
                    # If current snake longer, it wins
                    if len(snake.tiles) > len(other_snake.tiles):
                        snake.has_killed = True
                        other_snake.tiles = np.ndarray([])
                        other_snake.is_alive = False
                        continue
                    
                    # If both same length, both die
                    elif len(snake.tiles) == len(other_snake.tiles):
                        snake.tiles = np.ndarray([])
                        snake.is_alive = False
                        other_snake.tiles = np.ndarray([])
                        other_snake.is_alive = False
                        continue
                    
                    # Otherwise we lose
                    else:
                        other_snake.has_killed = True
                        snake.tiles = np.ndarray([])
                        snake.is_alive = False
                        continue
                    
                # Check body collision
                for tile in other_snake.tiles[1:]:
                    if np.array_equal(tile, head):
                        other_snake.has_killed = True
                        snake.tiles = np.ndarray([])
                        snake.is_alive = False
                        break 
                
