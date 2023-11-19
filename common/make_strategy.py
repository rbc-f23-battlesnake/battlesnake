
    
    
# Make singleplayer strategy

move_acronyms = {
    "u": "up",
    "l": "left",
    "r": "right",
    "d": "down"
}

def generate_strategy_11x11():
    strategy = {}
    for x in range(11):
        for y in range(11):
            tile = (x, y)
            # move = input(f"Move for {tile}: ")
            move = input()
            
            while move not in move_acronyms.keys():
                move = input()
            strategy[tile] = move_acronyms[move]
    
    print(strategy)
    
def generate_strategy_9x9():
    strategy = {}
    for x in range(1, 10):
        for y in range(1, 10):
            tile = (x, y)
            # move = input(f"Move for {tile}: ")
            move = input()
            while move not in move_acronyms.keys():
                move = input()
            strategy[tile] = move_acronyms[move]
    
    print(strategy)
        
if __name__ == "__main__":
    # generate_strategy_11x11()
    generate_strategy_11x11()
