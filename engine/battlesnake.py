from data.board import Board
from data.snake import Snake

import numpy as np
import random
import typing
import concurrent.futures

from math import inf
from numpy import minimum, maximum
import itertools

moves = ["up", "left", "right", "down"]
BRANCH_LIMIT = 1800
depth = 0

class Battlesnake:
    def __init__(self, game_data: typing.Dict) -> None:
        self.board = Board(game_data)
        self.our_snake = self.board.get_our_snake()
        self.seen = set()
        self.shortest_path = []


    ##############################
    # Implement this             #
    ##############################
    def get_best_move(self) -> str:
        
        # Find safe moves
        safe_moves = [m for m in moves if self.__is_move_safe(self.our_snake, m, self.board)]
        
        # If making a move will put us in a spot that's really bad (only 1 tile of free space) 
        # then make a potentially unsafe move
        if (len(safe_moves) == 0):
            print("LAST DITCH MOVE")
            last_ditch_moves = [m for m in moves if self.__is_move_safe(self.our_snake, m, self.board, checkHeadOnHead=False)]
            return max({m: self.get_free_squares(m) for m in last_ditch_moves}) if last_ditch_moves else "up"
        
        #############################
        # Minimax                   #
        #############################
        best_move = safe_moves[0]
        best_value = -inf
        move_scores = {m: 0 for m in safe_moves}
        
        # Set up minimax threads
        minimax = self.minimax

        args = []
        for move in safe_moves:
            board_copy = self.board.copy()
            args.append([depth, -inf, inf, board_copy, True, move])
            
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(minimax, *arg) for arg in args]

            move_scores = {safe_moves[i]: f.result() for i, f in enumerate(futures)}

            print("Minimax")
            print(move_scores)
            return max(move_scores, key=move_scores.get)
    
    
    def __get_score(self, snakeId: str, original_board: Board, move: str) -> float:
        score = 0
        board = original_board.copy()
        snake = board.get_snake(snakeId)
        has_grown = board.move_snake(snakeId, move)
        
        board.adjudicate_board()
        
        if not snake.is_alive:
            return -inf
                
        other_snakes = board.get_other_snakes(snake.id)
        our_head = snake.tiles[0]

        if snake.has_killed:
            score += 150
        
        if move == self.best_direction_to_food(moves, original_board):
            if snake.health < 50:
                score += 25
            
            # We should be the largest snake
            if len(board.get_other_snakes(self.our_snake.id)) >= 1 and len(snake.tiles) < 1 + max([len(s.tiles) for s in board.get_other_snakes(self.our_snake.id)]):
                score += 25
        
        # If we have access to alot of space, reward
        free_squares = self.get_free_squares(move, original_board)
        # print(f'Move: {move} - free squares: {free_squares}')
        score += free_squares
        
        
        
        for other_snake in other_snakes:
            other_snake_head = other_snake.tiles[0]
            distance = abs(our_head[0] - other_snake_head[0]) + abs(our_head[1] - other_snake_head[1])

            if distance <= 3:
                # Penalize if we get too close to snakes
                if (len(other_snake.tiles)) > len(snake.tiles):
                    score -= 5
                
                # If we are near another snake's head that is shorter, reward
                else:
                    score += 15
        
        # # Stay away from corners
        # if (our_head[0] in range(0, 2) or our_head[0] in range(board.width - 2, board.width)) and (our_head[1] in range(0, 2) or our_head[1] in range(board.height - 2, board.height)):
        #     score -= 100
        
        # elif our_head[0] == 0 or our_head[0] == board.width - 1 or our_head[1] == 0 or our_head[1] == board.height:
        #     score -= 10
            
        return score
    
    def minimax(self, depth: int, alpha, beta, board: Board, isOurSnake: bool, move: str):
        other_snakes = board.get_other_snakes(board.get_our_snake().id)
        other_snake_moves = [self.__get_safe_moves(s, board, False) for s in other_snakes]

        if depth == 0 or not board.get_our_snake().is_alive or len([s for s in other_snakes if s.is_alive]) == 0 or len(self.__get_safe_moves(board.get_our_snake(), board, checkHeadOnHead=False)) == 0:
            return self.__get_score(board.get_our_snake().id, board, move)
        
        # Take our other_snakes if other_snake_moves is empty
        other_snakes_new = []
        other_snake_moves_new = []
        for i in range(len(other_snakes)):
            if len(other_snake_moves[i]) != 0:
                other_snakes_new.append(other_snakes[i])
                other_snake_moves_new.append(other_snake_moves[i])
        
        other_snakes = other_snakes_new
        other_snake_moves = other_snake_moves_new
        
        other_snakes_new = []
        other_snake_moves_new = []
        
        move_combos = list(itertools.product(*other_snake_moves))
        # print(move_combos)
    
        # Minimax - spawn child process for each possible child node
        value = -inf if isOurSnake else inf
        
        alphaBetaStop = False
        for move_combo in move_combos:
            if alphaBetaStop:
                break
            
            # print(move_combo)
            child_base_board = board.copy()
            
            # Move other snakes - our snake hasn't moved yet
            for i in range(len(other_snakes)):
                child_base_board.move_snake(other_snakes[i].id, move_combo[i])
            
            # We can move our snake now
            child_base_board.move_snake(child_base_board.get_our_snake().id, move)
            child_base_board.adjudicate_board()
            
            if isOurSnake:
                for move in self.__get_safe_moves(child_base_board.get_our_snake(), child_base_board, True):
                    child_board = child_base_board.copy()
                    value = maximum(value, self.minimax(depth - 1, alpha, beta, child_board, False, move))
                    alpha = maximum(alpha, value)
                    if value >= beta:
                        alphaBetaStop = True
                        break
            else:
                for move in self.__get_safe_moves(child_base_board.get_our_snake(), child_base_board, True):
                    child_board = child_base_board.copy()
                    value = minimum(value, self.minimax(depth - 1, alpha, beta, child_board, True, move))
                    beta = minimum(beta, value)
                    if value <= alpha:
                        alphaBetaStop = True
                        break
        return value
                    

    def __get_safe_moves(self, snake, board, checkHeadOnHead=True):
        safe_moves = [m for m in moves if self.__is_move_safe(snake, m, board, checkHeadOnHead)]
        return safe_moves
    
    
    def most_squares_move(self, moveChoices):
        bestMove = moveChoices[0]
        bestSquares = -1
        for move in moveChoices:
            squares = self.get_free_squares(move)
            if squares > bestSquares:
                bestMove = move
        
        # print(f"Best move is: {bestMove} with {bestSquares} of squares")
        return bestMove
    
    
    def get_free_squares(self, move, board=None):
        board_copy = board.copy() if board is not None else self.board.copy() # Dw bout it
        
        board_copy.move_snake(self.our_snake.id, move)
        our_snake_copy = board_copy.get_our_snake()
        
        # If this move results in instant death, don't do it
        # TODO we can probably simulate making all other snakes pick a move that gives them food if they have one
        if not self.__get_safe_moves(board_copy.get_our_snake(), board_copy, checkHeadOnHead=False):
            return -1
        
        # Determine number of tiles our snake can access
        # Create a board for flood fill algorithm
        snake_board = [[False for _ in range(board_copy.width)] for _ in range(board_copy.height)]
        
        # Populate        
        for snake in board_copy.snakes:
            if snake.is_alive:
                for x, y in snake.tiles:
                    if x not in range(self.board.width) or y not in range(self.board.height):
                        return -2
                    snake_board[y][x] = True
        
        self.seen = set()
        self.floodfill(our_snake_copy.tiles[0][0], our_snake_copy.tiles[0][1], snake_board)
        
        return len(self.seen)

    # Find shortest path to food
    def best_direction_to_food(self, moveChoices, board=None):
        return self.find_shortest_path_to_tiles(moveChoices, board.food if board is not None else self.board.food)[0]
    
    def floodfill(self, x, y, snake_board):
        for dx, dy in [(-1, 0), (0, -1), (0, 1), (1, 0)]:
            if (x + dx, y + dy) in self.seen:
                continue
            elif not ((0 <= x + dx < self.board.width) and (0 <= y + dy < self.board.width)):
                continue
            # Can't go on top of existing snake
            elif snake_board[y + dy][x + dx]:
                continue
            
            self.seen.add((x, y))
            self.floodfill(x + dx, y + dy, snake_board)
    
    # BFS to find shortest path
    def find_shortest_path_to_tiles(self, initialMoveList, desiredTilesList):
        if len(desiredTilesList) == 0:
            # print("ERROR: No tiles in desiredTilesList")
            return [random.choice(initialMoveList)] 
        
        our_snake = self.our_snake
        visited = set()
        
        initial_head = tuple(our_snake.tiles[0].tolist())
        
        visited.add(initial_head)
        to_visit = [(our_snake.copy(), [m]) for m in initialMoveList]
    
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
            
            snake_copy.move(path[-1], self.board.food)
            
            for f in desiredTilesList:
                if tuple(f.tolist()) == new_head:
                    return path
            
            visited.add(new_head)

            for m in self.__get_safe_moves(snake_copy, self.board):
                to_visit.append((snake_copy.copy(), path.copy() + [m]))

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
        if head[0] not in range(0, board.width) or head[1] not in range(0, board.height):
            # print("move not safe, boundaries")
            return False
        
        # Check if snake has no more health
        if snake_copy.health == 0:
            # print("move not safe, health")
            return False
        
        # Check if snake collides with itself
        for tile in snake_copy.tiles[1:]:
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

    #####################################################################
    # Archived Functions                                                #
    #####################################################################
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
