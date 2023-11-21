import sys
import json
from engine.battlesnake import Battlesnake


def main():    
    filename = sys.argv[1]
    print(filename)
    game_data = json.load(open(filename))
    battlesnake = Battlesnake(game_data)
    battlesnake.get_best_move()

if __name__ == "__main__":
    main()