from data.board import Board
from data.snake import Snake

import random
import typing
import concurrent.futures

from collections import deque
from math import inf
from numpy import minimum, maximum
import itertools

moves = ["up", "left", "right", "down"]
depth = 3

BRANCH_LIMIT = 1800

class Battlesnake:
    def __init__(self, game_data: typing.Dict) -> None:
        self.board = Board(game_data)
        self.our_snake = self.board.get_our_snake()
        self.seen = set()
        self.shortest_path = []
        self.branch_count = 0

    ##############################
    # Implement this             #
    ##############################
    def get_best_move(self) -> str:
        safe_moves = [m for m in moves if self.__is_move_safe(self.our_snake, m, self.board)]

        if (len(safe_moves) == 0):
            last_ditch_moves = [m for m in moves if self.__is_move_safe(self.our_snake, m, self.board, checkHeadOnHead=False)]
            return random.choice(last_ditch_moves) if last_ditch_moves else "up"
        
        self.branch_count = 0
        safest_moves = [m for m in safe_moves if not self.is_stuck_in_dead_end(self.our_snake, 15, m)]
        preferred_moves = safest_moves if safest_moves else safe_moves
        
        # Grow snake
        if self.our_snake.health < 50:
            print("Regenerating Health")
            return self.best_direction_to_food(preferred_moves, self.board)

        # If we aren't the largest snake by at least 2 points, we need to be
        elif (len(self.board.snakes) > 1 and not len(self.our_snake.tiles) > 1 + max([len(s.tiles) for s in self.board.get_other_snakes(self.our_snake.id)])):
            print("Growing!")
            return self.best_direction_to_food(preferred_moves, self.board)

        #############################
        # Otherwise, return minimax #
        #############################
        move_scores = {m: 0 for m in preferred_moves}
        
        # Set up minimax threads
        minimax = self.minimax

        args = []
        for move in preferred_moves:
            board_copy = self.board.copy()
            args.append([depth, -inf, inf, board_copy, True, move])
            
        with concurrent.futures.ThreadPoolExecutor(4) as executor:
            futures = [executor.submit(minimax, *arg) for arg in args]

            move_scores = {preferred_moves[i]: f.result() for i, f in enumerate(futures)}

            print("Minimax")
            print(move_scores)
            return max(move_scores, key=move_scores.get)

    def get_preferred_moves(self, board, snake, deadEndDepth):
        safe_moves = [m for m in moves if self.__is_move_safe(snake, m, board)]
        safest_moves = [m for m in safe_moves if not self.is_stuck_in_dead_end(snake, 15, m)]
        return safest_moves if safest_moves else safe_moves

    # See if the snake still has #<turns> worth of moves to go to
    # DFS to find if a branch of length 
    def is_stuck_in_dead_end(self, snake, turns, move):
        # Base cases
        if len(snake.tiles) < 4:
            return False
        
        snake_moved = snake.copy()
        snake_moved.move(move, self.board.food)
            
        return self.__is_stuck_in_dead_end_wrapped(snake_moved, turns)
        
    # Requires snake to have moved (safe move)
    def __is_stuck_in_dead_end_wrapped(self, snake, turns):
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
            
            # Check self-collision
            collide = False
            for tile in snake_copy.tiles[1:]:
                if head == tile:
                    collide = True
                    break
            if collide:
                continue
            
            # Check collision with other snakes
            for other_snake in self.board.get_other_snakes(self.our_snake.id):
                for tile in other_snake.tiles[1:-2]: # Optimization: Don't look at tail
                    if head == tile:
                        collide = True
                        break
                if collide:
                    continue
                
            stuck = stuck and self.__is_stuck_in_dead_end_wrapped(snake_copy, turns - 1)

        return stuck


    # For minimax
    def __get_score(self, snakeId: str, original_board: Board, move: str) -> float:
        score = 0
        board = original_board.copy()
        snake = board.get_snake(snakeId)
        board.move_snake(snakeId, move)
        
        board.adjudicate_board()
        
        if not snake.is_alive:
            return -inf

        if snake.has_killed:
            score += 50

        if len(board.snakes) == 1:
            score += 75
        
        # If we have access to alot of space, reward
        free_squares = self.get_free_squares(move, original_board)
        score += free_squares

        return score
    
    def minimax(self, depth: int, alpha, beta, board: Board, isOurSnake: bool, move: str):
        other_snakes = board.get_other_snakes(board.get_our_snake().id)
        other_snake_moves = [self.__get_safe_moves(s, board, False) for s in other_snakes]

        if depth == 0 or not board.get_our_snake().is_alive or not (s for s in other_snakes if s.is_alive) or not self.__get_safe_moves(board.get_our_snake(), board, checkHeadOnHead=False):
            return self.__get_score(board.get_our_snake().id, board, move)

        if isOurSnake:
            value = -999999
            child_base_board = board.copy()
            
            # We can move our snake now
            child_base_board.move_snake(self.our_snake.id, move)
            child_base_board.adjudicate_board()

            for move in self.get_preferred_moves(child_base_board, child_base_board.get_our_snake(), deadEndDepth=12):
                child_board = child_base_board.copy()
                eval = self.minimax(depth - 1, alpha, beta, child_board, False, move)
                value = maximum(value, eval)
                alpha = maximum(alpha, value)
                if value >= beta:
                    break
            return value
        
        else:
            # Take our other_snakes if other_snake_moves is empty
            for i in range(len(other_snakes)):
                if not other_snake_moves[i]:
                    other_snakes.pop(i)
                    other_snake_moves.pop(i)
                    i -= 1
            move_combos = list(itertools.product(*other_snake_moves))

            # Minimax - spawn child process for each possible child node        
            alphaStop = False
            value = 999999
            for move_combo in move_combos:
                if alphaStop:
                    break
                child_base_board = board.copy()
                
                # Move other snakes - our snake has already moved
                for i in range(len(other_snakes)):
                    child_base_board.move_snake(other_snakes[i].id, move_combo[i])
                
                child_base_board.adjudicate_board()
                for move in self.__get_safe_moves(child_base_board.get_our_snake(), child_base_board.copy(), True):
                    child_board = child_base_board.copy()
                    eval = self.minimax(depth - 1, alpha, beta, child_board, True, move)
                    value = minimum(value, eval)
                    beta = minimum(beta, value)
                    if value <= alpha:
                        alphaStop = True
                        break
            return value
                    

    def __get_safe_moves(self, snake, board, checkHeadOnHead=True):
        safe_moves = (m for m in moves if self.__is_move_safe(snake, m, board, checkHeadOnHead))
        return safe_moves
    
    
    def most_squares_move(self, moveChoices):
        bestMove = moveChoices[0]
        bestSquares = -1
        for move in moveChoices:
            squares = self.get_free_squares(move, self.board.copy())
            if squares > bestSquares:
                bestMove = move
        
        # print(f"Best move is: {bestMove} with {bestSquares} of squares")
        return bestMove
    
    
    def get_free_squares(self, move, board):
        board_copy = board.copy()
        
        board_copy.move_snake(self.our_snake.id, move)
        our_snake_copy = board_copy.get_our_snake()
        
        # If this move results in instant death, don't do it
        # TODO we can probably simulate making all other snakes pick a move that gives them food if they have one
        if not self.__get_safe_moves(our_snake_copy, board_copy, checkHeadOnHead=True):
            return -1
        
        # Determine number of tiles our snake can access
        # Create a board for flood fill algorithm
        snake_board = [[False for _ in range(board_copy.width)] for _ in range(board_copy.height)]
        
        # Populate        
        for snake in board_copy.snakes:
            if snake.is_alive:
                for x, y in snake.tiles:
                    if x not in range(self.board.width) or y not in range(self.board.height):
                        return -1
                    snake_board[y][x] = True
        
        self.seen = set()
        self.floodfill(our_snake_copy.tiles[0][0], our_snake_copy.tiles[0][1], snake_board)
        
        return len(self.seen)

    # Find shortest path to food
    def best_direction_to_food(self, moveChoices, board):

        path = self.find_shortest_path_to_tiles(moveChoices, board.food)
        # print(path)
        return path[0]
    
    def floodfill(self, x, y, snake_board):
        for dx, dy in [(-1, 0), (0, -1), (0, 1), (1, 0)]:
            if (x + dx, y + dy) in self.seen:
                continue
            elif not ((0 <= x + dx < self.board.width) and (0 <= y + dy < self.board.height)):
                continue
            # Can't go on top of existing snake
            elif snake_board[y + dy][x + dx]:
                continue
            
            self.seen.add((x, y))
            self.floodfill(x + dx, y + dy, snake_board)
    
    # BFS to find shortest path
    def find_shortest_path_to_tiles(self, initialMoveList, desiredTilesList, board=None):
        if board == None:
            board = self.board.copy()
        if len(desiredTilesList) == 0:
            # print("ERROR: No tiles in desiredTilesList")
            return [random.choice(initialMoveList)] 

        our_snake = board.get_our_snake()
        visited = set()
        
        initial_head = our_snake.tiles[0]
        
        visited.add(initial_head)
        to_visit = deque([(our_snake.copy(), [m]) for m in initialMoveList])
    
        while to_visit:
            snake_copy, path = to_visit.popleft()
            direction_mapping = {
                'up': (0, 1),
                'down': (0, -1),
                'left': (-1, 0),
                'right': (1, 0)
            }
        
            new_head = (
                snake_copy.tiles[0][0] + direction_mapping[path[-1]][0],
                snake_copy.tiles[0][1] + direction_mapping[path[-1]][1]
            )

            if new_head in visited:
                continue
            
            snake_copy.move(path[-1], board.food)
            
            for f in desiredTilesList:
                if f == new_head:
                    return path
            
            visited.add(new_head)

            for m in self.__get_safe_moves(snake_copy, board):
                to_visit.append((snake_copy.copy(), path + [m]))

        # Search failed
        # print("Error can't find path to tile in desiredTilesList")
        return [random.choice(initialMoveList)]     

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
        if not (0 <= head[0] < board.width) or not (0 <= head[1] < board.height):
            # print("move not safe, boundaries")
            return False
        
        # Check if snake has no more health
        if snake_copy.health == 0:
            # print("move not safe, health")
            return False
        
        # Check if snake collides with itself
        for tile in snake_copy.tiles[1:]:
            if head == tile:
                # print("move not safe, self collision")
                return False
        
        other_snakes = board.get_other_snakes(snake.id)
        # Check if snake can possibly collide with other snakes' bodies
        for other_snake in other_snakes:
            for tile in other_snake.tiles[1:-1]:
                if head == tile:
                    # print("Move not safe, other snake collision")
                    return False
                        
        # Check if head or tail collisions are possible
        for other_snake in other_snakes:
            # Simulate moving other snake, then check if collision
            for move in moves:
                other_snake_copy = other_snake.copy()
                other_snake_has_grown = other_snake_copy.move(move, board.food)[0]
                
                
                # Head-to-head possibility
                if checkHeadOnHead and head == other_snake_copy.tiles[0]:
                    if len(snake_copy.tiles) <= len(other_snake_copy.tiles):
                        # print("Move not safe, head to head loss")
                        return False

                # Tail collision if snake has grown
                if (other_snake_has_grown or other_snake_copy.tiles[-1] == other_snake_copy.tiles[-2]) and head == other_snake_copy.tiles[-1]:
                    # print("move not safe, tail collision")
                    return False
        # print("Move is safe!")
        return True