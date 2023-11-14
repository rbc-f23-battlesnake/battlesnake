import numpy as np
from data.snake import Snake
from data.board import Board
import random

direction_mapping = {
    'up': (0, 1),
    'down': (0, -1),
    'left': (-1, 0),
    'right': (1, 0)
}


def simulate_move(direction: str, head):

        new_head = (
           head[0] + direction_mapping[direction][0],
           head[1] + direction_mapping[direction][1]
        )
        
        return new_head

# get possible moves on a specific tile. (cannot touch any snake tile)
def get_possible_moves(tile, board: Board):
    possible_moves = {}
    for m in direction_mapping.keys():
         possible_space = simulate_move(m, tile)
         
         # check if wall
         if possible_space[0] == board.width or possible_space[1] == board.height:
              continue
         
         # check if any snakes in vicinity
         occupied = False
         for s in board.snakes:
              if possible_space in s.tiles:
                   occupied = True
                   break
         if occupied:
            continue
         else:
            possible_moves[m] = possible_space
    return possible_moves