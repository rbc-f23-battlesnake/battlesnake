from data.snake import Snake
from math import inf

def manhattan_dist(tileA, tileB):
    return sum(abs(val1-val2) for val1, val2 in zip(tileA, tileB))
    
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

    def hash_board(self):
        return hash(self)
    
    
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
    
    def can_do_head_on_head(self) -> bool:
        if len(self.snakes) == 2:
            return self.get_our_snake().get_length() > self.get_largest_enemy_snake().get_length()
        return False
    

    # Only contested if larger snake is near 
    def get_uncontested_food(self, snakeId):
        uncontested_food = self.food.copy()
        for snake in self.snakes:
            if snake.id == snakeId or len(snake.tiles) <= len(self.get_our_snake().tiles):
                continue
            uncontested_food = [f for f in uncontested_food if manhattan_dist(snake.tiles[0], f) > 2]

        return uncontested_food
 
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
    def move_snake(self, snake_id: str, direction: str, editFood=True) -> None:
        for snake in self.snakes:
            if snake.is_alive and snake.id == snake_id:
                has_grown = snake.move(direction, self.food, editFood=editFood)[0]
                return has_grown


    # Checks all snakes to see if any should die :skull_emoji:
    # Requires all snakes on the board have already made their move
    # - doCollisionChecks is set to false when we only move our snake (for minimax reasons)
    def adjudicate_board(self, doCollisionChecks=True):
        
        # rules are applied in a certain order - https://github.com/BattlesnakeOfficial/rules/blob/main/standard.go#L188-L189
        
        # 1. Remove food if there's a snake on it
        # Clean up food that has been eaten
        for snake in self.snakes:
            if snake.is_alive and snake.tiles[0] in self.food:
                self.food.remove(snake.tiles[0])
        
        # 2. Check if snakes die because of board  (go off boundaries or die from health)
        for snake in self.snakes:
            if snake.is_alive:
                head = snake.tiles[0]
                # Check boundaries
                if not ((0 <= head[0] < self.width) and (0 <= head[1] < self.height)):
                    snake.kill_this_snake() 
                elif snake.health <= 0:
                    snake.kill_this_snake() 
        
        
        # If we are just scoring our move, only check self-collisions then return
        if not doCollisionChecks:
            our_snake = self.get_our_snake()
            if our_snake.is_alive:
                head = our_snake.tiles[0]
                # Check if snake collides with itself
                for tile in our_snake.tiles[1:]:
                    if tile == head:
                        our_snake.kill_this_snake()
                        break
            return
        
        
        # 3. Do snake collisions
        for snake in self.snakes:
            if not snake.is_alive and not snake.tiles:
                # print("Snake already dead")
                continue
            
            head = snake.tiles[0]
            # Check if snake collides with itself
            for tile in snake.tiles[1:]:
                if tile == head:
                    snake.is_alive = False
                    break

            # Check collision with other snakes
            for other_snake in self.get_other_snakes(snake.id):
                if not other_snake.is_alive:
                    continue
                
                # Check head-on-head collision
                if other_snake.tiles[0] == head:
                    # If current snake longer, it wins
                    if len(snake.tiles) > len(other_snake.tiles):
                        snake.has_killed = True
                        other_snake.is_alive = False
                        continue
                    
                    # If both same length, both die
                    elif len(snake.tiles) == len(other_snake.tiles):
                        snake.is_alive = False
                        other_snake.is_alive = False
                        continue
                    
                    # Otherwise we lose
                    else:
                        other_snake.has_killed = True
                        snake.is_alive = False
                        continue
                    
                # Check body collision
                for tile in other_snake.tiles[1:]:
                    if tile == head:
                        other_snake.has_killed = True
                        snake.is_alive = False
                        break 
        
        # Clean up snakes that we left "psudo-alive" (set is_alive=False but kept tiles for collisions)
        # Kind of like "applying" the eliminations
        for snake in self.snakes:
            if not snake.is_alive and snake.tiles:
                snake.kill_this_snake()
