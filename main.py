# Welcome to
# __________         __    __  .__                               __
# \______   \_____ _/  |__/  |_|  |   ____   ______ ____ _____  |  | __ ____
#  |    |  _/\__  \\   __\   __\  | _/ __ \ /  ___//    \\__  \ |  |/ // __ \
#  |    |   \ / __ \|  |  |  | |  |_\  ___/ \___ \|   |  \/ __ \|    <\  ___/
#  |________/(______/__|  |__| |____/\_____>______>___|__(______/__|__\\_____>
#
# This file is the main entry point for your Battlesnake. Do not add or remove functions from this file.
# You can add additional functions to this file or create new files and import them here.
#
# To get you started we've included code to prevent your Battlesnake from moving backwards.
# For more info see docs.battlesnake.com

from engine.battlesnake import Battlesnake
from server import run_server

import typing

# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data
def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "Globe Gliders", 
        "color": "#b5defc",
        "head": "top-hat",
        "tail": "bonhomme"
    }


# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print("GAME START")
    print(game_state["game"]["id"])


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")


# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: typing.Dict) -> typing.Dict:
    print(f"[MOVE {game_state['turn']} - {game_state['game']['id']}]")
    
    battle_snake = Battlesnake(game_state)
    best_move = None
    try:
        best_move = battle_snake.get_best_move()
    except Exception as e:
        print(e)
        print("!!! ERROR: Something happened in normal best-move !!!")
        best_move = battle_snake.backup_move()
        
        
    print(f"[Decided Move]: " + best_move)
    return {"move": best_move}

# Start server when `python main.py` is run
if __name__ == "__main__":
    run_server({"info": info, "start": start, "move": move, "end": end})
