from data.board import Board
from data.snake import Snake
import common.moves as common
import numpy as np
import random
import typing


moves = ["up", "left", "right", "down"]
BRANCH_LIMIT = 1800
depth = 0

class Battlesnake:
    def __init__(self, game_data: typing.Dict) -> None:
        self.board = Board(game_data)
        self.our_snake = self.board.get_our_snake()
        self.branch_count = 0
        self.shortest_path = []


    ##############################
    # Implement this             #
    ##############################
    def get_best_move(self) -> str:
        safe_moves = [m for m in moves if self.__is_move_safe(self.our_snake, m, self.board)]

        self.branch_count = 0
        safest_moves = [m for m in safe_moves if not self.is_stuck_in_dead_end(self.our_snake, 17, m)]

        preferred_moves = safest_moves if safest_moves else safe_moves
        
        if (len(preferred_moves) == 0):
            last_ditch_moves = [m for m in moves if self.__is_move_safe(self.our_snake, m, self.board, checkHeadOnHead=False)]
            return random.choice(last_ditch_moves) if last_ditch_moves else "up"
        
        # Grow if we are small or have low health
        if self.our_snake.health < 20 or len(self.our_snake.tiles) < 5: 
            print("Growing!")
            return self.best_direction_to_food(self.board, preferred_moves)
        
        # If we aren't the largest snake by at least 2 points, we need to be
        elif (len(self.board.snakes) > 1 and not len(self.our_snake.tiles) > 1 + max([len(s.tiles) for s in self.board.get_other_snakes(self.our_snake.id)])):
            print("Growing!")
            return self.best_direction_to_food(self.board, preferred_moves)
        
        # If we are the largest by at least 2 points, find and kill the 2nd largest enemy snake
        elif len(self.board.snakes) > 1 and len(self.our_snake.tiles) > max([len(s.tiles) for s in self.board.get_other_snakes(self.our_snake.id)]):
            #  Move towards 2nd largest enemy snake head
            largest_enemy = self.board.get_largest_enemy_snake()
            
            # Get array of enemy snakes possible moves (not wall, not neck)
            possible_enemy_moves = self.__get_safe_moves(largest_enemy, self.board)
            possible_enemy_tiles = []
            for m in possible_enemy_moves:
               possible_tile = common.simulate_move(m, largest_enemy.get_head())
               possible_enemy_tiles.append(possible_tile)
            # Out of the enemy snake's next possible moves, move towards the closest possible move if safe
            target_tile = random.choice(possible_enemy_tiles)
            
            # What do we need to be careful of when following enemy snake?
            move = self.best_direction_to_target_tile(target_tile, preferred_moves)

            print(f"LETS ATTACK: Move {move} to {target_tile}!")
            return move


        # Otherwise do random move
        return random.choice(preferred_moves)
        
        
    def __get_safe_moves(self, snake, board, checkHeadOnHead=True):
        safe_moves = [m for m in moves if self.__is_move_safe(snake, m, board, checkHeadOnHead)]
        return safe_moves
    

    def best_direction_to_target_tile(self, tile, safeMoveChoices):
        curr_head = self.our_snake.get_head()

        distance_x = abs(curr_head[0] - tile[0])
        distance_y = abs(curr_head[1] - tile[1])

        our_possible_heads = {}
        for m in safeMoveChoices:
            new_head = common.simulate_move(m, curr_head)
            
            # move: newHeadTile
            our_possible_heads[m] = new_head
        
        for direction, location in our_possible_heads.items():
            new_distance_x = abs(location[0] - tile[0])
            new_distance_y = abs(location[1] - tile[1])

            if new_distance_x < distance_x or new_distance_y < distance_y:
                return direction
        
    # Find shortest path to food
    def best_direction_to_food(self, board: Board, moveChoices):
        our_snake = board.get_our_snake()
        visited = set()
        
        initial_head = tuple(our_snake.tiles[0].tolist())
        
        visited.add(initial_head)
        to_visit = [(our_snake.copy(), [m]) for m in moveChoices]
        
        while to_visit:
            snake_copy, path = to_visit.pop(0)
            head = snake_copy.tiles[0]

            new_head = (-1, -1)
            match path[-1]:
                case 'up':
                    new_head = (head[0], head[1] + 1)
                case 'down':
                    new_head = (head[0], head[1] - 1)
                case 'left':
                    new_head = (head[0] - 1, head[1])
                case 'right':
                    new_head = (head[0] + 1, head[1])

            if new_head in visited:
                continue
            
            snake_copy.move(path[-1], board.food)
            
            for f in board.food:
                if tuple(f.tolist()) == new_head:
                    return path[0]
            
            visited.add(new_head)

            for m in self.__get_safe_moves(snake_copy, board):
                to_visit.append((snake_copy.copy(), path.copy() + [m]))

        print("Error can't find path to food")
        return random.choice(moveChoices)     


    def __is_move_safe(self, snake: Snake, move: str, board, checkHeadOnHead=True) -> bool:
        if not snake.is_alive:
            return False
        # print("Testing move " + move)
        if board.turn == 0:
            return True 
              
        snake_copy = snake.copy()
        snake_copy.move(move, board.food)
        head = snake_copy.tiles[0]
        
        # Check boundaries
        if head[0] not in range(0, board.width) or head[1] not in range(0, board.height):
            # print("move not safe, boundaries")
            return False
        
        # Check if snake has no more health
        if snake_copy.health == 0:
            # print("move not safe, health")
            return False
        
        # Check if snake collides with itself
        for tile in snake_copy.tiles[2:]:
            if np.array_equal(head, tile):
                # print("move not safe, self collision")
                return False
        
        other_snakes = board.get_other_snakes(snake.id)
        # Check if snake can possibly collide with other snakes' bodies
        for other_snake in other_snakes:
            for tile in other_snake.tiles[1:-1]:
                if np.array_equal(tile, head):
                    # print("Move not safe, other snake collision")
                    return False
                        
        # Check if head or tail collisions are possible
        for other_snake in other_snakes:
            # Simulate moving other snake, then check if collision
            for move in moves:
                other_snake_copy = other_snake.copy()
                other_snake_has_grown = other_snake_copy.move(move, board.food)[0]
                
                
                # Head-to-head possibility
                if checkHeadOnHead and np.array_equal(head, other_snake_copy.tiles[0]):
                    if len(snake_copy.tiles) <= len(other_snake_copy.tiles):
                        # print("Move not safe, head to head loss")
                        return False

                # Tail collision if snake has grown
                if (other_snake_has_grown or np.array_equal(other_snake_copy.tiles[-1], other_snake_copy.tiles[-2])) and np.array_equal(head, other_snake_copy.tiles[-1]):
                    # print("move not safe, tail collision")
                    return False
        # print("Move is safe!")
        return True


    # See if the snake still has #<turns> worth of moves to go to
    def is_stuck_in_dead_end(self, snake, turns, move):
        if len(snake.tiles) < 4:
            return False
        
        snake_moved = snake.copy()
        grown = snake_moved.move(move, self.board.food)[0]
        return self.__is_stuck_in_dead_end_wrapped(snake_moved, turns, grown)
        
        
    # Requires snake to have moved (safe move)
    def __is_stuck_in_dead_end_wrapped(self, snake, turns, grown=False):
        
        if turns == 0:
            return False
        
        stuck = True
        for move in moves:
            if self.branch_count == BRANCH_LIMIT:
                # print("Reached branch limit")
                return True
            
            self.branch_count += 1
            if not stuck:
                return False
            
            snake_copy = snake.copy()
            snake_copy.move(move, self.board.food)
            head = snake_copy.tiles[0]
            
            # Check boundaries
            if head[0] not in range(0, self.board.width) or head[1] not in range(0, self.board.height):
                continue
            
            # Check if snake collides with itself
            if grown:
                if np.array_equal(head, snake_copy.tiles[-1]):
                    continue
            
            collide = False
            for tile in snake_copy.tiles[2:]:
                if np.array_equal(head, tile):
                    collide = True
                    break
            if collide:
                continue
            
            stuck = stuck and self.__is_stuck_in_dead_end_wrapped(snake_copy, turns - 1)

        return stuck
