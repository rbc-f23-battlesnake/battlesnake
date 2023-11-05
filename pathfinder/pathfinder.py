class Node:
    def __init__(self, tile, distFromStartNode: int, distFromEndNode: int, traversible: bool, parent=None) -> None:
        self.tile = tile
        self.g = distFromStartNode
        self.h = distFromEndNode
        self.totalCost = self.g + self.h
        self.traversible = traversible
        self.parent
        pass

# Create Pathfinder Node Board
class PathfinderBoard:
    def __init__(self, board, untraversible, startTile, endTile) -> None:
        self.grid = board # 11x11 grid
        self.untraversableTiles = untraversible # snake bodies + larger snake heads

    def applyUntraversableTiles(grid, untraversibleTiles):

        # Convert grid coordinates to Nodes

        pass


#algo A* path finding

#init OPEN // set of nodes to be evaluated
#init CLOSED // set of nodes already evaluated

# add startNode to OPEN (evaluate at start node first)

# LOOP
    # currNode = node in OPEN with lowest totalCost
    # remove currNode from OPEN
    # add currNode to CLOSED

    # if currNode == targetNode
        #return

    # foreach neighbor of currNode
        # if neighbour !traversable OR neighbour in CLOSED
            # skip to next neighbor
        
        # if newPath to neighbor is shorter OR neightbor is not in OPEN
            # set totalCost of neighbor
            # set parent of neighbor to currentNode
            # if neighbor is not in OPEN
                # add neighbor to OPEN
        





# from starting node, calculate values for surrounding nodes

# choose node with lowest totalCost
    # in case of tie, choose lowest h cost

