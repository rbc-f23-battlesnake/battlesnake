import numpy as np
from data.snake import Snake
from data.board import Board

moves = ["up", "down", "left", "right"]

def simulate_move(direction: str, head):
        match direction:
            case 'up':
                new_head = np.array([head[0], head[1] + 1])
            case 'down':
                new_head = np.array(head[0], head[1] - 1)
            case 'left':
                new_head = np.array([head[0] - 1, head[1]])
            case 'right':
                new_head = np.array([head[0] + 1, head[1]])
        return new_head

def get_possible_moves(snake: Snake, board: Board):
    possible_moves = np.array([])
    head = snake.get_head()
    neck = snake.get_neck()

    for m in moves:
         new_head = simulate_move(m, head)
         
        # don't hit wall
         if new_head[0] == board.width or new_head[1] == board.height:
              continue
        # don't hit self
         elif new_head in snake.tiles:
              continue
         else:
              possible_moves.append(m)
    return possible_moves