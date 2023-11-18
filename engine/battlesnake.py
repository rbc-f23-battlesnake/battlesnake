from data.board import Board, manhattan_dist
from data.snake import Snake

from time import time
from multiprocessing import Process, Array
import typing

from collections import deque
from math import inf
from numpy import minimum, maximum
import itertools
import common.moves as utils

moves = ["up", "left", "right", "down"]

BRANCH_LIMIT = 1800

class Battlesnake:
    def __init__(self, game_data: typing.Dict) -> None:
        self.board = Board(game_data)
        self.our_snake = self.board.get_our_snake()
        self.seen = set()
        self.branch_count = 0
        self.start_time = time()
        self.TIME_LIMIT = (int(game_data["game"]["timeout"]) / 1000)
        
        if len(self.board.snakes) >= 4:
            self.TIME_LIMIT *= 0.55
        elif len(self.board.snakes) == 3:
            self.TIME_LIMIT *= 0.65
        else:
            self.TIME_LIMIT *= 0.80

    def check_available_moves(self, snake: Snake, move: str):
        new_postion = utils.simulate_move(move, snake.get_head())
        
        open_spaces = utils.count_open_spaces()
        pass

    def is_diagonal_tile(self, tileA, tileB):
        return abs(tileA[0] - tileB[0]) == 1 and abs(tileA[1] - tileB[1]) == 1

    ##############################
    # Implement this             #
    ##############################
    def get_best_move(self) -> str:
        
        # check head on = TRUE, as long as we are tied or the largest snake
        safe_moves = [m for m in moves if self.__is_move_safe(self.our_snake, m, self.board, checkHeadOnHead=not self.board.can_do_head_on_head())]
        print(f"safe moves: {safe_moves}")
        if (len(safe_moves) == 0):
            print("No very safe moves, defaulting to last_ditch_moves")
            last_ditch_moves = [m for m in moves if self.__is_move_safe(self.our_snake, m, self.board, checkHeadOnHead=False)]
            return self.most_squares_move(last_ditch_moves, self.our_snake.id) if last_ditch_moves else "up"
        
        self.branch_count = 0
        safest_moves = [m for m in safe_moves if not self.is_stuck_in_dead_end(self.our_snake, 15, m)]
        print(f"safest moves: {safest_moves}")
        preferred_moves = safest_moves if safest_moves else safe_moves
    
    
        #####################################
        # Strategy Logic                    #
        #####################################
        best_move = None # Queue up move for final minimax check
        
        # Grow snake
        if self.board.get_food_count() > 0 and self.our_snake.health < 30:
            print("Regenerating Health")
            best_dir = self.best_direction_to_food(preferred_moves, self.our_snake.id)
            if best_dir:
                best_move = best_dir
            else:
                print("Can't find path to food, defaulting to minimax")

        # for dueling
        elif (len(self.board.snakes) == 2 and self.board.turn > 15 and self.can_trap_enemy()):
            print("It's time to dudududduel")
            enemy_snake = self.board.get_other_snakes(self.our_snake.id)[0]

            target_tile = enemy_snake.get_head()

            # push to edge
            move = self.find_shortest_path_to_tiles(preferred_moves, [target_tile])

            if move:
                best_move = move[0]

            if enemy_snake.get_head()[0] in (0,10) and enemy_snake.get_head()[1] in (0,10) and self.our_snake.get_head()[0] in (1,9) and self.our_snake.get_head()[1] in (1,9):
                if self.is_diagonal_tile(self.our_snake.get_head(), enemy_snake.get_head()):
                    best_moves = self.__get_safe_moves(enemy_snake, self.board, checkHeadOnHead=True)
                    if len(best_moves) == 1:
                        print("you've activated my trap card")
                        best_move = best_moves[0]
            

        # If we aren't the largest snake by at least 2 points, we need to be
        elif (self.board.get_food_count() > 0 and len(self.board.snakes) > 1 and not len(self.our_snake.tiles) > 1 + max([len(s.tiles) for s in self.board.get_other_snakes(self.our_snake.id)])):
            print("Growing!")
            best_dir = self.best_direction_to_food(preferred_moves, self.our_snake.id)
            if best_dir:
                best_move = best_dir
            else:
                print("Can't find path to food, defaulting to minimax")
        
        # If we are the largest snake, or can't find food, attack closest snake that is smaller than us
        elif len(self.board.snakes) > 1:
            print("Attacking!")

            # Target closest enemy
            closest_enemy = self.get_closest_snake(preferred_moves)
            
            if closest_enemy:
                possible_enemy_moves = self.__get_safe_moves(closest_enemy, self.board, checkHeadOnHead=False)
                if possible_enemy_moves:
                    # find algorithm to get best tile for enemy snake while also no killing ourselves
                    best_enemy_move_scores = self.execute_minimax(possible_enemy_moves, snakeId=closest_enemy.id, timeLimit=0.100)
                    best_enemy_move = max(best_enemy_move_scores, key=best_enemy_move_scores.get)
                    target_tile = utils.simulate_move(best_enemy_move, closest_enemy.get_head())
                    
                    print(f"Best Enemy move: {best_enemy_move} - targeting tile: {target_tile}")
                    path = self.find_shortest_path_to_tiles(preferred_moves, [target_tile])
                    if path:
                        best_move = path[0]
                    else:
                        print("ERROR: Can't find path to expected tile, defaulting to minimax")
                else:
                    print("ERROR: Can't see enemy's best moves")
            else:
                print("ERROR: No closest enemy")
        else:
            print("No explicit strategy defined so returning with minimax")
            
        #############################################
        # Otherwise, return minimax or sanity check #
        #############################################

        minimax_move_scores = self.execute_minimax(preferred_moves, self.our_snake.id)
        max_move = max(minimax_move_scores, key=minimax_move_scores.get)
        if best_move:
            # Return sanity-checked best-move
            max_move_score = minimax_move_scores[max_move]
            
            if minimax_move_scores[best_move] >= max_move_score * 0.8:
                print(f"Returning self-defined strategy move of [ {best_move} ] since it is within 80% of best minimax move")
                return best_move
            else:
                    print(f"!!! ERROR: Best move of [ {best_move} ] is not within 80% of minimax max move so defaulting to minimax: [ {max_move} ] !!!")
                
        # Otherwise no best move or best move is bad so return minimax
        return max_move
    
    
    def minimax_wrapper(self, depth: int, board: Board, snakeId: str, moveIdx: int, resultArray):
        move_score = self.minimax(depth, -inf, inf, board, False, snakeId)
        resultArray[moveIdx] = move_score
        
    def execute_minimax(self, preferred_moves, snakeId, timeLimit=None):
        if not timeLimit:
            timeLimit = self.TIME_LIMIT
        minimax_values = Array('i', len(preferred_moves))
        
        # Iterative deepening
        minimax_wrapper = self.minimax_wrapper
        last_complete_minimax_scores = None
        depth = 0
        
        while True:
            elapsed_time = time() - self.start_time

            if elapsed_time >= timeLimit:
                print(f"Minimax Calculation took {elapsed_time} seconds")
                break
            
            last_complete_minimax_scores = list(minimax_values)
            minimax_values = Array('i', len(preferred_moves))
            
            # Sort for performance - look at best branch first
            last_complete_minimax_scores, preferred_moves = zip(*sorted(zip(last_complete_minimax_scores, preferred_moves), reverse=True))
            
            current_processes = []
            runtime = (timeLimit - elapsed_time) * 0.8
            for i, move in enumerate(preferred_moves):
                board_copy = self.board.copy()
                board_copy.move_snake(snakeId, move, editBoard=False)
                args = [depth, board_copy, snakeId, i, minimax_values]
                p = Process(target=minimax_wrapper, args=args)
                p.start()
                
                current_processes.append(p)
            
            for p in current_processes:
                elapsed_time = time() - self.start_time
                if elapsed_time >= timeLimit:
                    print(f"Could not finish joining all threads for depth {depth}, terminating early")
                    break
                p.join(runtime)
            
            for p in current_processes:
                p.terminate()  
            
            current_processes.clear()              
            
            depth += 1

            
        minimax_result_dict = {preferred_moves[i]: last_complete_minimax_scores[i] for i in range(len(preferred_moves))}
        print(f"Got to minimax depth {depth}")
        if snakeId == self.our_snake.id:
            print("Minimax")
            print(minimax_result_dict)
        else:
            print(f"Possible enemy moves: {minimax_result_dict}")
        
        return minimax_result_dict
        # return max(minimax_result_dict, key=minimax_result_dict.get)

    def can_trap_enemy(self):
        enemy_snake = self.board.get_other_snakes(self.our_snake.id)[0]

        enemy_dist = manhattan_dist(enemy_snake.get_head(), (5,5))
        our_dist = manhattan_dist(self.our_snake.get_head(), (5,5))

        return our_dist <= enemy_dist and manhattan_dist(enemy_snake.get_head(), self.our_snake.get_head()) <= 3

    def get_preferred_moves(self, board, snake, deadEndDepth=15):
        safe_moves = [m for m in moves if self.__is_move_safe(snake, m, board)]
        safest_moves = [m for m in safe_moves if not self.is_stuck_in_dead_end(snake, deadEndDepth, m)]
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
            for other_snake in self.board.get_other_snakes(snake_copy.id):
                if head in other_snake.tiles:
                    collide=True
                    break
            if collide:
                continue
            
            # Not stuck up to <turns> deep into check
            stuck = stuck and self.__is_stuck_in_dead_end_wrapped(snake_copy, turns - 1)

        return stuck


    # For minimax
    def __get_score(self, snakeId: str, original_board: Board) -> float:
        score = 0

        original_board.adjudicate_board()
        snake = original_board.get_snake(snakeId)
        if not snake.is_alive:
            score -= 500

        if snake.has_killed:
            score += 150

        # win first
        if len(original_board.snakes) == 1:
            score += 175
        
        # tie for first
        elif len(original_board.snakes) == 0:
            score += 100

        # If we have access to alot of space, reward
        free_squares = self.get_free_squares("noMove", original_board, snakeId)
        score += free_squares

        return score
    
    def minimax(self, depth: int, alpha, beta, board: Board, isMaximizingSnake: bool, snakeId: str):
        other_snakes = board.get_other_snakes(snakeId)

        if depth == 0 or not board.get_snake(snakeId).is_alive or not other_snakes or not self.__get_safe_moves(board.get_snake(snakeId), board, checkHeadOnHead=False):
            board.adjudicate_board()
            return self.__get_score(snakeId, board)

        if isMaximizingSnake:
            value = -999999

            for nextMove in self.get_preferred_moves(board, board.get_snake(snakeId), deadEndDepth=12):
                child_board = board.copy()
                
                # Move "our" snake
                child_board.move_snake(snakeId, nextMove, editBoard=False)
                
                eval = self.minimax(depth - 1, alpha, beta, child_board, False, snakeId)
                value = maximum(value, eval)
                alpha = maximum(alpha, eval)
                if value >= beta:
                    break
            return value
        
        else:
            other_snake_moves = [moves for _ in other_snakes]
            move_combos = list(itertools.product(*other_snake_moves))

            # Minimax - spawn child process for each possible child node        
            value = 999999
            for move_combo in move_combos:
                child_base_board = board.copy()
                
                # Move other snakes - "our" snake has already moved
                for i in range(len(other_snakes)):
                    child_base_board.move_snake(other_snakes[i].id, move_combo[i], editBoard=False)
                child_base_board.adjudicate_board()
                
                eval = self.minimax(depth - 1, alpha, beta, child_base_board, True, snakeId)
                value = minimum(value, eval)
                beta = minimum(beta, eval)
                if value <= alpha:
                    break
            return value
                    

    def __get_safe_moves(self, snake, board, checkHeadOnHead=True):
        safe_moves = [m for m in moves if self.__is_move_safe(snake, m, board, checkHeadOnHead)]
        return safe_moves
    
    
    def most_squares_move(self, moveChoices, snakeId):
        bestMove = moveChoices[0]
        bestSquares = -1
        for move in moveChoices:
            squares = self.get_free_squares(move, self.board.copy(), snakeId)
            if squares > bestSquares:
                bestMove = move
        
        # print(f"Best move is: {bestMove} with {bestSquares} of squares")
        return bestMove
    
    
    def get_free_squares(self, move, board, snakeId):
        board_copy = None
        if move in moves:
            board_copy = board.copy()
            board_copy.move_snake(snakeId, move)
        else:
            board_copy = board.copy()
        snake_copy = board_copy.get_snake(snakeId)
        
        # If this move results in instant death, don't do it
        # TODO we can probably simulate making all other snakes pick a move that gives them food if they have one
        if not self.__get_safe_moves(snake_copy, board_copy, checkHeadOnHead=True):
            return -1
        
        # Determine number of tiles our snake can access
        # Create a board for flood fill algorithm
        snake_board = [[False for _ in range(board_copy.width)] for _ in range(board_copy.height)]
        
        # Populate tiles already covered by snakes        
        for snake in board_copy.snakes:
            if snake.is_alive:
                for x, y in snake.tiles:
                    if x not in range(self.board.width) or y not in range(self.board.height):
                        return -1
                    snake_board[y][x] = True
        
        self.seen = set()
        self.floodfill(snake_copy.tiles[0][0], snake_copy.tiles[0][1], snake_board)
        
        return len(self.seen)

    # Gets the closest snake that is smaller than us
    # TODO: This is buggy for some reason - look for "Can't connect path with enemy head, which shouldn't happen :("
    def get_closest_snake(self, preferredMoves):
        # Filter to be only snakes that are smaller than us
        other_snakes = [s for s in self.board.get_other_snakes(self.our_snake.id) if len(s.tiles) < len(self.our_snake.tiles)]
        other_snake_heads = [s.tiles[0] for s in other_snakes]
        print(f"Other snake heads: {other_snake_heads}")
        print(f"Our Head: {self.our_snake.tiles[0]}")
        
        closest_path = self.find_shortest_path_to_tiles(preferredMoves, other_snake_heads)
        print(f"Closest path: {closest_path}")
        if not closest_path:
            print("Can't find path to other snakes, will default to minimax")
            return None
        

        head = self.our_snake.tiles[0]
        for move in closest_path:
            head = utils.simulate_move(move, head)
        
        for i in range(len(other_snakes)):
            if head == other_snakes[i].tiles[0]:
                return other_snakes[i]
            
        print("Can't connect path with enemy head, which shouldn't happen :(")
        return None
    
    def get_safe_food(self, foodList: list):
        # only go for food that has 2 or more open spaces
        safe_food = list(filter(lambda x: len(utils.get_possible_moves(x, self.board)) >= 2, foodList))
        return safe_food
    
    # Find shortest path to food
    def best_direction_to_food(self, moveChoices, snakeId):
        uncontested_food = self.board.get_uncontested_food(snakeId)
        path = self.find_shortest_path_to_tiles(moveChoices, uncontested_food)
        return path[0] if path else None
    
    # check all directions, and add possible moves to self.seen
    def floodfill(self, x, y, snake_board):
        for dx, dy in [(-1, 0), (0, -1), (0, 1), (1, 0)]:
            if (x + dx, y + dy) in self.seen:
                continue

            # can't go OOB
            elif not ((0 <= x + dx < self.board.width) and (0 <= y + dy < self.board.width)):

                continue
            # Can't go on top of existing snakes
            elif snake_board[y + dy][x + dx]:
                continue
            
            self.seen.add((x, y))
            self.floodfill(x + dx, y + dy, snake_board)
    
    # BFS to find shortest path
    def find_shortest_path_to_tiles(self, initialMoveList, desiredTilesList, board=None):
        if board == None:
            board = self.board
        
        board_copy = board.copy()
        if len(desiredTilesList) == 0:
            print("ERROR: No tiles in desiredTilesList, returning None")
            return None     

        our_snake_copy = board_copy.get_our_snake()
        
        # Hotfix for in case food spawns in our path once we're committed
        # e.g. https://play.battlesnake.com/game/d0e9b478-c8de-48e9-812a-506f7a7ffce5
        our_snake_copy.tiles.append(tuple(our_snake_copy.tiles[-1]))
        
        visited = set()
        
        initial_head = tuple(our_snake_copy.tiles[0])
        
        visited.add(initial_head)
        to_visit = deque([(board_copy.copy(), [m]) for m in initialMoveList])
    
        while to_visit:
            board_copy, path = to_visit.popleft()
            snake_copy = board_copy.get_our_snake()
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
            
            if new_head in desiredTilesList:
                return path
            
            if new_head in visited:
                continue
            
            board_copy.move_snake(snake_copy.id, path[-1])

            visited.add(new_head)

            for m in self.__get_safe_moves(snake_copy, board_copy):
                new_path = path.copy()
                new_path.append(m)
                to_visit.append((board_copy.copy(), new_path))

        # Search failed
        print("Error can't find path to tile in desiredTilesList, returning None")
        return None

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
