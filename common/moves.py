import numpy as np
from data.snake import Snake
from data.board import Board
import random

moves = ["up", "down", "left", "right"]

def simulate_move(direction: str, head):
        new_head = np.array([])
        match direction:
            case 'up':
                new_head = np.array([head[0], head[1] + 1])
            case 'down':
                new_head = np.array([head[0], head[1] - 1])
            case 'left':
                new_head = np.array([head[0] - 1, head[1]])
            case 'right':
                new_head = np.array([head[0] + 1, head[1]])
        return new_head

def get_possible_moves(snake: Snake, board: Board):
    possible_moves = np.array([])
    head = snake.get_head()

    for m in moves:
         new_head = simulate_move(m, head)
         
         print(f"\n\n\nNEW HEAD: {new_head}\n\n\n")
        # don't hit wall
         if new_head[0] == board.width or new_head[1] == board.height:
              continue
        # don't hit self
         elif new_head in snake.tiles:
              continue
         else:
              possible_moves.append(m)
    return possible_moves

#   # Find shortest path to food
# def best_direction_to_target(initial_head, board: Board, safe_moves, target_tiles):
#     our_snake = board.get_our_snake()
#     visited = set()

#     initial_head = tuple(our_snake.tiles[0].tolist())

#     visited.add(initial_head)
#     to_visit = [(our_snake.copy(), [m]) for m in safe_moves]

#     while to_visit:
#         snake_copy, path = to_visit.pop(0)
#         head = snake_copy.tiles[0]

#         new_head = (-1, -1)
#         match path[-1]:
#             case 'up':
#                 new_head = (head[0], head[1] + 1)
#             case 'down':
#                 new_head = (head[0], head[1] - 1)
#             case 'left':
#                 new_head = (head[0] - 1, head[1])
#             case 'right':
#                 new_head = (head[0] + 1, head[1])

#         if new_head in visited:
#             continue
        
#         snake_copy.move(path[-1], board.food)
        
#         for f in board.food:
#             if tuple(f.tolist()) == new_head:
#                 return path[0]
        
#         visited.add(new_head)

#         for m in self.__get_safe_moves(snake_copy, board):
#             to_visit.append((snake_copy.copy(), path.copy() + [m]))

#     print("Error can't find path to food")
#     return random.choice(moveChoices)  