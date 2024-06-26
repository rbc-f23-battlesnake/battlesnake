from data.board import Board, manhattan_dist
from data.snake import Snake

from time import time
from multiprocessing import Process, Array, connection
import typing

from collections import deque
from math import inf
from numpy import minimum, maximum
import itertools
import common.moves as utils

moves = ["up", "left", "right", "down"]

# For 11x11
singleplayer_strategy = {(0, 0): 'up', (0, 1): 'right', (0, 2): 'up', (0, 3): 'right', (0, 4): 'up', (0, 5): 'right', (0, 6): 'up', (0, 7): 'right', (0, 8): 'up', (0, 9): 'right', (0, 10): 'right', (1, 0): 'left', (1, 1): 'right', (1, 2): 'left', (1, 3): 'right', (1, 4): 'left', (1, 5): 'right', (1, 6): 'left', (1, 7): 'right', (1, 8): 'left', (1, 9): 'up', (1, 10): 'right', (2, 0): 'left', (2, 1): 'right', (2, 2): 'left', (2, 3): 'right', (2, 4): 'left', (2, 5): 'right', (2, 6): 'left', (2, 7): 'right', (2, 8): 'left', (2, 9): 'down', (2, 10): 'right', (3, 0): 'left', (3, 1): 'right', (3, 2): 'left', (3, 3): 'right', (3, 4): 'left', (3, 5): 'right', (3, 6): 'left', (3, 7): 'right', (3, 8): 'up', (3, 9): 'left', (3, 10): 'right', (4, 0): 'left', (4, 1): 'right', (4, 2): 'left', (4, 3): 'right', (4, 4): 'left', (4, 5): 'right', (4, 6): 'left', (4, 7): 'right', (4, 8): 'left', (4, 9): 'down', (4, 10): 'right', (5, 0): 'left', (5, 1): 'right', (5, 2): 'left', (5, 3): 'right', (5, 4): 'left', (5, 5): 'right', (5, 6): 'left', (5, 7): 'right', (5, 8): 'up', (5, 9): 'left', (5, 10): 'right', (6, 0): 'left', (6, 1): 'right', (6, 2): 'left', (6, 3): 'right', (6, 4): 'left', (6, 5): 'right', (6, 6): 'left', (6, 7): 'right', (6, 8): 'left', (6, 9): 'down', (6, 10): 'right', (7, 0): 'left', (7, 1): 'right', (7, 2): 'left', (7, 3): 'right', (7, 4): 'left', (7, 5): 'right', (7, 6): 'left', (7, 7): 'right', (7, 8): 'up', (7, 9): 'left', (7, 10): 'right', (8, 0): 'left', (8, 1): 'right', (8, 2): 'left', (8, 3): 'right', (8, 4): 'left', (8, 5): 'right', (8, 6): 'left', (8, 7): 'right', (8, 8): 'left', (8, 9): 'down', (8, 10): 'right', (9, 0): 'left', (9, 1): 'up', (9, 2): 'left', (9, 3): 'up', (9, 4): 'left', (9, 5): 'up', (9, 6): 'left', (9, 7): 'up', (9, 8): 'up', (9, 9): 'left', (9, 10): 'right', (10, 0): 'left', (10, 1): 'down', (10, 2): 'down', (10, 3): 'down', (10, 4): 'down', (10, 5): 'down', (10, 6): 'down', (10, 7): 'down', (10, 8): 'down', (10, 9): 'down', (10, 10): 'down'}

# For 9x9
# singleplayer_strategy = {(1, 1): 'up', (1, 2): 'right', (1, 3): 'up', (1, 4): 'right', (1, 5): 'up', (1, 6): 'right', (1, 7): 'left', (1, 8): 'down', (1, 9): 'right', (2, 1): 'left', (2, 2): 'up', (2, 3): 'left', (2, 4): 'up', (2, 5): 'left', (2, 6): 'up', (2, 7): 'up', (2, 8): 'left', (2, 9): 'right', (3, 1): 'left', (3, 2): 'down', (3, 3): 'down', (3, 4): 'down', (3, 5): 'down', (3, 6): 'down', (3, 7): 'down', (3, 8): 'down', (3, 9): 'right', (4, 1): 'up', (4, 2): 'up', (4, 3): 'up', (4, 4): 'up', (4, 5): 'up', (4, 6): 'up', (4, 7): 'up', (4, 8): 'left', (4, 9): 'right', (5, 1): 'left', (5, 2): 'down', (5, 3): 'right', (5, 4): 'down', (5, 5): 'right', (5, 6): 'down', (5, 7): 'right', (5, 8): 'down', (5, 9): 'right', (6, 1): 'up', (6, 2): 'left', (6, 3): 'right', (6, 4): 'left', (6, 5): 'right', (6, 6): 'left', (6, 7): 'right', (6, 8): 'left', (6, 9): 'right', (7, 1): 'left', (7, 2): 'down', (7, 3): 'right', (7, 4): 'left', (7, 5): 'right', (7, 6): 'left', (7, 7): 'right', (7, 8): 'left', (7, 9): 'right', (8, 1): 'up', (8, 2): 'left', (8, 3): 'right', (8, 4): 'left', (8, 5): 'right', (8, 6): 'left', (8, 7): 'right', (8, 8): 'left', (8, 9): 'right', (9, 1): 'left', (9, 2): 'down', (9, 3): 'down', (9, 4): 'left', (9, 5): 'down', (9, 6): 'left', (9, 7): 'down', (9, 8): 'left', (9, 9): 'down'}


BRANCH_LIMIT = 1800

class Battlesnake:
    def __init__(self, game_data: typing.Dict) -> None:
        self.board = Board(game_data)
        self.our_snake = self.board.get_our_snake()
        self.seen = set()
        self.branch_count = 0
        self.start_time = time()
        self.TIME_LIMIT = (int(game_data["game"]["timeout"]) / 1000) - 0.085 # 85ms of overhead
        self.backup_move = None

    def check_available_moves(self, snake: Snake, move: str):
        new_postion = utils.simulate_move(move, snake.get_head())
        
        open_spaces = utils.count_open_spaces()
        pass

    def is_diagonal_tile(self, tileA, tileB):
        return abs(tileA[0] - tileB[0]) == 1 and abs(tileA[1] - tileB[1]) == 1

    # !!! Emergencies only !!!
    def get_backup_move(self) -> str:
        print("!!! ERROR: Something went wrong, going with backup move if it exists, or picking random safe move")
        if self.backup_move:
            return self.backup_move
        
        last_ditch_moves = [m for m in moves if self.__is_move_safe(self.our_snake, m, self.board, checkHeadOnHead=False)]
        return self.most_squares_move(last_ditch_moves, self.our_snake.id) if last_ditch_moves else "up"
        
    ##############################
    # Implement this             #
    ##############################
    def get_best_move(self) -> str:
        # I don't think it's possible to always win singleplayer because of health.
        # But if we're lucky we can
        
        
        if len(self.board.snakes) == 1:
            # Strategy: Since we are on an m x n board where m, n are both odd
            #           we create a hamiltonian circuit that only misses the top left corner (v)
            #            - if food spawns at v, path to from the circuit, then return to the closest tile in the circuit
            if (0, 10) in self.board.food:
                if self.our_snake.get_head() == (0, 9):
                    return "up"
                
            return singleplayer_strategy[self.our_snake.get_head()]
        
        # check head on = TRUE, as long as we are tied or the largest snake
        safe_moves = [m for m in moves if self.__is_move_safe(self.our_snake, m, self.board, checkHeadOnHead=True)]
        safest_moves = None
        preferred_moves = None
        # print(f"safe moves: {safe_moves}")
        if (len(safe_moves) == 0):
            print("No very safe moves, defaulting to last_ditch_moves")
            last_ditch_moves = [m for m in moves if self.__is_move_safe(self.our_snake, m, self.board, checkHeadOnHead=False)]
            return self.most_squares_move(last_ditch_moves, self.our_snake.id) if last_ditch_moves else "up"

        self.branch_count = 0
        safest_moves = [m for m in safe_moves if not self.is_stuck_in_dead_end(self.our_snake, 15, m)]
        # print(f"safest moves: {safest_moves}")
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
                self.backup_move = best_dir
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
                self.backup_move = move[0]

            if enemy_snake.get_head()[0] in (0,10) and enemy_snake.get_head()[1] in (0,10) and self.our_snake.get_head()[0] in (1,9) and self.our_snake.get_head()[1] in (1,9):
                if self.is_diagonal_tile(self.our_snake.get_head(), enemy_snake.get_head()):
                    best_moves = self.__get_safe_moves(enemy_snake, self.board, checkHeadOnHead=True)
                    if len(best_moves) == 1:
                        print("you've activated my trap card")
                        best_move = best_moves[0]
                        self.backup_move = best_moves[0]
            

        # If we aren't the largest snake by at least 2 points, we need to be
        elif (self.board.get_food_count() > 0 and len(self.board.snakes) > 1 and not len(self.our_snake.tiles) > 1 + max([len(s.tiles) for s in self.board.get_other_snakes(self.our_snake.id)])):
            print("Growing!")
            best_dir = self.best_direction_to_food(preferred_moves, self.our_snake.id)
            if best_dir:
                best_move = best_dir
                self.backup_move = best_dir
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
                    best_enemy_move_scores = self.execute_minimax(possible_enemy_moves, snakeId=closest_enemy.id, timeLimit=0.125)
                    best_enemy_move = max(best_enemy_move_scores, key=best_enemy_move_scores.get)
                    target_tile = utils.simulate_move(best_enemy_move, closest_enemy.get_head())
                    
                    print(f"Best Enemy move: {best_enemy_move} - targeting tile: {target_tile}")
                    path = self.find_shortest_path_to_tiles(preferred_moves, [target_tile])
                    if path:
                        best_move = path[0]
                        self.backup_move = path[0]
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

        minimax_move_scores = self.execute_minimax(preferred_moves, self.our_snake.id, self.TIME_LIMIT)
        max_move = max(minimax_move_scores, key=minimax_move_scores.get)
        if best_move:
            # Return sanity-checked best-move
            max_move_score = minimax_move_scores[max_move]
            
            if minimax_move_scores[best_move] >= max_move_score * 0.93:
                print(f"Returning self-defined strategy move of [ {best_move} ] since it is within 93% of best minimax move")
                return best_move
            else:
                    print(f"!!! ERROR: Best move of [ {best_move} ] is not within 93% of minimax max move so defaulting to minimax: [ {max_move} ] !!!")
                
        # Otherwise no best move or best move is bad so return minimax
        self.backup_move = max_move
        return max_move
    
    
    def minimax_wrapper(self, depth: int, board: Board, snakeId: str, moveIdx: int, resultArray):
        move_score = self.minimax(depth, -inf, inf, board, False, snakeId)
        resultArray[moveIdx] = move_score
        
    def execute_minimax(self, preferred_moves, snakeId, timeLimit):
        minimax_values = Array('i', len(preferred_moves))
        
        # Iterative deepening
        minimax_wrapper = self.minimax_wrapper
        depth = 0
        
        current_processes = []
        background_processes = []
        while True:
            elapsed_time = time() - self.start_time

            if elapsed_time >= timeLimit:
                print(f"Minimax Calculation took {elapsed_time} seconds")
                break
            
            # Sorting pruning optimization
            # if not depth % 4 and depth:
            #     # cleanup

            #     for p in background_processes:
            #         p.kill()
            #         p.join()
            #         p.close()

            #     background_processes.clear()
                
            #     # print("Before sort")
            #     # print(list(minimax_values))
            #     # print(list(preferred_moves))
            #     values = list(minimax_values)
            #     values, preferred_moves = (list(t) for t in zip(*sorted(zip(values, preferred_moves), reverse=True)))
                
            #     for i in range(len(values)):
            #         minimax_values[i] = values[i] 
            #     # print("After sort")
            #     # print(list(minimax_values))
            #     # print(list(preferred_moves))
            runtime = (timeLimit - elapsed_time)

            for i, move in enumerate(preferred_moves):
                child_board = self.board.copy()
                child_board.move_snake(snakeId, move, editFood=False)
                args = [depth, child_board, snakeId, i, minimax_values]
                p = Process(target=minimax_wrapper, args=args)
                p.start()
                current_processes.append(p)

            # Join all processes at the same time
            connection.wait((p.sentinel for p in current_processes), timeout=runtime) 
            
            background_processes += current_processes
            current_processes.clear()              
            
            depth += 1
        
        # cleanup
        for p in background_processes:
            p.kill()
            p.join()
            p.close()

        # Reformat results and return them
        minimax_result_dict = {move: list(minimax_values)[i] for i, move in enumerate(preferred_moves)}
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

    def get_preferred_moves(self, board, snake, deadEndDepth=12):
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
            if head in snake_copy.tiles[1:]:
                collide = True
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
        snake = original_board.get_snake(snakeId)
        alive_snakes = [s for s in original_board.snakes if s.is_alive]
        
        if snake.has_killed:
            score += 150
            
        if not snake.is_alive:
            # tie for first
            if not alive_snakes:
                score += 75
            else:
                score -= 500
            return score
        
        #######################################
        # Snake is alive beyond this point    #
        #######################################
        
        # We are last snake alive so we win
        elif len(alive_snakes) == 1:
            score += 175
        
        # If we have access to alot of space, reward
        free_squares = self.get_free_squares("noMove", original_board, snakeId)
        score += free_squares
        
        # Calculate the distance to the center of the board
        distance_to_center = abs(snake.get_head()[0] - 5) + abs(snake.get_head()[1] - 5)

        # Encourage controlling the center of the board
        center_control_bonus = 50
        score += center_control_bonus // (distance_to_center + 1)

        return score
    
    def minimax(self, depth: int, alpha, beta, board: Board, isMaximizingSnake: bool, snakeId: str):
        other_snakes = board.get_other_snakes(snakeId)

        if depth == 0 or not board.get_snake(snakeId).is_alive or not other_snakes or not self.__get_safe_moves(board.get_snake(snakeId), board, checkHeadOnHead=False):
            
            # if isMaximizingSnake=True: Caller has moved all enemy snakes in response to us moving our snake
            # if isMaximizingSnake=False: Caller has only moved our snake 
            # So, we want to only do collision checks if all other enemy snakes have moved in response to us (isMaximizingSnake=True)
            board.adjudicate_board(doCollisionChecks=isMaximizingSnake)
            return self.__get_score(snakeId, board)

        if isMaximizingSnake:
            value = -999999

            for nextMove in self.get_preferred_moves(board, board.get_snake(snakeId), deadEndDepth=12):
                child_board = board.copy()
                
                # Move "our" snake
                child_board.move_snake(snakeId, nextMove, editFood=False)
                
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
                    child_base_board.move_snake(other_snakes[i].id, move_combo[i], editFood=False)
                child_base_board.adjudicate_board()
                
                eval = self.minimax(depth - 1, alpha, beta, child_base_board, True, snakeId)
                value = minimum(value, eval)
                beta = minimum(beta, eval)
                if value <= alpha:
                    break
            return value
                    

    def __get_safe_moves(self, snake, board, checkHeadOnHead=True, customFood=None, checkOtherSnakeCollisions=True):
        return [m for m in moves if self.__is_move_safe(snake, m, board, checkHeadOnHead, customFood, checkOtherSnakeCollisions)]
    

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

        closest_path = self.find_shortest_path_to_tiles(preferredMoves, other_snake_heads)

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
        path = self.find_shortest_path_to_tiles(moveChoices, self.board.food)
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

        our_snake_copy = board_copy.get_our_snake().copy()
        
        # Remove our snake from the board
        board_copy.snakes.remove(board_copy.get_our_snake())
        
        # Hotfix for in case food spawns in our path once we're committed
        # e.g. https://play.battlesnake.com/game/d0e9b478-c8de-48e9-812a-506f7a7ffce5
        our_snake_copy.tiles.append(tuple(our_snake_copy.tiles[-1]))
        
        visited = set()
        
        initial_head = tuple(our_snake_copy.tiles[0])
        
        visited.add(initial_head)
        to_visit = deque([(our_snake_copy.copy(), board_copy.food.copy(), [m]) for m in initialMoveList])
        depth = 0
        while to_visit and depth <= 250:
            snake, food, path = to_visit.popleft()
            snake_copy = snake.copy()
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
            
            snake_copy.move(path[-1], food, editFood=True)

            visited.add(new_head)

            for m in self.__get_safe_moves(snake_copy, board_copy, customFood=food):
                new_path = path.copy()
                new_path.append(m)
                to_visit.append((snake_copy.copy(), food.copy(), new_path))
            depth += 1

        # Search failed
        print("Error can't find path to tile in desiredTilesList, returning None")
        return None

    def __is_move_safe(self, snake: Snake, move: str, board, checkHeadOnHead=True, customFood=None, checkOtherSnakeCollisions=True) -> bool:
        if not snake.is_alive:
            return False
        # print("Testing move " + move)
        if board.turn == 0:
            return True 
              
        snake_copy = snake.copy()
        if customFood:
            snake_copy.move(move, customFood)
        else:
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
        if head in snake_copy.tiles[1:]:
            # print("move not safe, self collision")
            return False
        
        if not checkOtherSnakeCollisions:
            return True
        
        other_snakes = board.get_other_snakes(snake.id)                
        other_snake_safe_moves = {s.id: self.__get_safe_moves(s, board, checkHeadOnHead=False, customFood=None, checkOtherSnakeCollisions=False) for s in other_snakes}
        
        # Check if snake can possibly collide with other snakes' bodies
        for other_snake in other_snakes:
            if head in other_snake.tiles[1:-1]:
                # This is kinda wacky but we can actually move into another snake's body if it kills itself first
                if other_snake_safe_moves[other_snake.id]: # So only return false if the other snake can stay alive
                    return False

        # Check if head or tail collisions are possible
        for other_snake in other_snakes:
            # Simulate moving other snake, then check if collision
            for move in other_snake_safe_moves[other_snake.id]:
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
        return True
