from data.snake import Snake

class Board:
    def __init__(self, *args):
        if len(args) == 0:
            self.width = 0
            self.height = 0
            self.food = None
            self.snakes = None
            self.turn = 0

        else:
            game_data = args[0]
            self.width = game_data['board']['width']
            self.height = game_data['board']['height']
            
            self.food = [(posn['x'], posn['y']) for posn in game_data['board']['food']]
            self.turn = game_data['turn']
            
            # read in the snakes
            self.snakes = []
            
            for snake in game_data['board']['snakes']:
                if snake['id'] == game_data['you']['id']:
                    self.snakes.append(Snake(snake, True))
                else:
                    self.snakes.append(Snake(snake))


    def copy(self):
        # Fill values with the same data
        board = Board()
        
        board.width = self.width
        board.height = self.height
        board.food = [tuple(f) for f in self.food]
        board.snakes = [s.copy() for s in self.snakes]
        board.turn = self.turn
        return board
    
    def get_food_count(self) -> int:
        return len(self.food)
    
    def get_largest_enemy_snake(self) -> Snake:
        enemy = None
        largest = 0
        for snake in self.get_other_snakes(self.get_our_snake().id):
            if snake.is_alive and snake.get_length() > largest:
                largest = snake.get_length()
                enemy = snake
   
        return enemy
    
    def get_our_snake(self) -> Snake:
        for s in self.snakes:
            if s.is_our_snake:
                return s
    
    
    def get_snake(self, snake_id: str):
        for s in self.snakes:
            if s.id == snake_id:
                return s
    
    def get_other_snakes(self, snake_id: str):
        return [s for s in self.snakes if s.is_alive and s.id != snake_id]
    
    
    # Preferred method of moving the snake
    def move_snake(self, snake_id: str, direction: str) -> None:
        for snake in self.snakes:
            if snake.is_alive and snake.id == snake_id:
                has_grown = snake.move(direction, self.food, editBoard=True)[0]
                return has_grown


    # Checks all snakes to see if any should die :skull_emoji:
    # Requires all snakes on the board have already made their move
    def adjudicate_board(self):
        for snake in self.snakes:
            if not snake.is_alive:
                # print("Snake already dead")
                continue
            
            elif snake.health <= 0:
                snake.kill_this_snake()
                continue
            
            head = snake.tiles[0]
            # Check if snake collides with itself
            for tile in snake.tiles[1:]:
                if tile == head:
                    snake.kill_this_snake()
                    break

            if not snake.is_alive:
                continue
            
            # Check boundaries
            if head[0] not in range(0, self.width) or head[1] not in range(0, self.height):
                snake.kill_this_snake()
                continue          

            # Check collision with other snakes
            for other_snake in self.get_other_snakes(snake.id):
                if not other_snake.is_alive:
                    continue
                
                # Check head-on-head collision
                if other_snake.tiles[0] == head:
                    # If current snake longer, it wins
                    if len(snake.tiles) > len(other_snake.tiles):
                        snake.has_killed = True
                        other_snake.kill_this_snake()
                        continue
                    
                    # If both same length, both die
                    elif len(snake.tiles) == len(other_snake.tiles):
                        snake.kill_this_snake()
                        other_snake.kill_this_snake()
                        continue
                    
                    # Otherwise we lose
                    else:
                        other_snake.has_killed = True
                        snake.kill_this_snake()
                        continue
                    
                # Check body collision
                for tile in other_snake.tiles[1:]:
                    if tile == head:
                        other_snake.has_killed = True
                        snake.kill_this_snake()
                        break 