# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part A: Single Player Infexion

import heapq
from collections import deque
from .utils import render_board
from .lines import getRLines, getQLines, getVLines


DIRECTIONS = ((1,-1), (1,0), (0,1), (-1,1), (-1,0), (0,-1))
DIM = 7
MAX_POWER = DIM - 1
ENEMY = {'r': 'b', 'b': 'r'}
MY_COLOUR = 'r'

# maps every node to a line of nodes based on directions 'r', 'q' and vertical
R_LINES = getRLines()
Q_LINES = getQLines()
V_LINES = getVLines()


def search(input: dict[tuple, tuple]) -> list[tuple]:
    """
    This is the entry point for your submission. The input is a dictionary
    of board cell states, where the keys are tuples of (r, q) coordinates, and
    the values are tuples of (p, k) cell states. The output should be a list of 
    actions, where each action is a tuple of (r, q, dr, dq) coordinates.

    See the specification document for more details.
    """

    # The render_board function is useful for debugging -- it will print out a 
    # board state in a human-readable format. Try changing the ansi argument 
    # to True to see a colour-coded version (if your terminal supports it).

    # initialise priority queue with initial board, with no spreads currently played
    pq = [((0,0), (0, (input, [])))]
    counter = 0

    # list that tracks boards reached from the A* search
    boardsReached = []

    # finds the heuristic value based on an enemy configuration of nodes
    enemyConfigs = {}

    # implement priority queue for A* search
    while pq:
        current = heapq.heappop(pq)[1][1]

        # the current position and corresponding sequence of spreads
        board = current[0]
        spreads = current[1]

        # keep track of boards reached
        boardsReached.append(board)

        # for every red node
        for (position, piece) in board.items():
            if piece[0] != MY_COLOUR:
                continue
            # and for every direction
            for direction in DIRECTIONS:
                # get the new board after spreading
                newBoard = board.copy()                                 
                spread(newBoard, position, direction)

                # skip over boards that have been reached
                if (newBoard in boardsReached):
                    continue

                # found a winning position, so return the sequence of spreads
                if victory(newBoard, MY_COLOUR):
                    spreads.append(position + direction)                                           
                    
                    return spreads
               
                # update spread sequence
                newSpreads = spreads.copy()
                newSpreads.append(position + direction) 
                
                # if a new configuration of enemy nodes is found (after a capture)
                # record the heuristic for this new configuration
                config = getConfig(newBoard, MY_COLOUR)
                if config not in enemyConfigs.keys():
                    heuristic = heuristicValue(newBoard, MY_COLOUR)
                    enemyConfigs[config] = heuristic
                else:
                    heuristic = enemyConfigs[config]
                
                # add to queue based on priority
                heapq.heappush(pq, 
                    (getPriority(newSpreads, heuristic), (counter,(newBoard, newSpreads))))
                counter += 1

    # initial position was already won, with no nodes on the board
    return []

def getPriority(newSpreads, heuristic):
    """
    Assigns priority given the heuristic value and sequence of spreads taken 
    to get to the board, for use alongside a priority queue to implement A* search

    Boards are ranked by lowest estimated total cost first, 
    and then by the higher number of spreads already played
    """

    # cost so far
    movesPlayed = len(newSpreads)

    # estimated total cost
    total = movesPlayed + heuristic

    return (total, -movesPlayed)


def getConfig(board, playerColour):
    """
    The positions of remaining enemy nodes on a board can be used as an identifier. 
    A sorted tuple of these positions can be used as a key, and the heuristic value 
    based on a particular configuration of nodes need to only be calculated once, and stored
    in a dictionary during the search algorithm.

    This function finds the sorted tuple configuration of the enemy node positions
    """

    newConfig = []
    for (position, piece) in board.items():
        if piece[0] != playerColour:
            newConfig.append(position)

    return tuple(sorted(newConfig))


def heuristicValue(board, playerColour):
    """
    Tries different combinations of 'lines' in the 'r', 'q' and vertical directions. The minimum
    number of lines to cross out all enemy nodes will correspond to a minimum number of moves to
    win, and hence leads to an admissible heuristic.

    A queue is implemented to explore combinations using breath-first search
    until the minimum number of lines needed is found
    """

    enemyColour = ENEMY[playerColour]
    
    # put board in queue with initially 0 'lines' used to cross out enemy nodes
    q = deque([(board, 0)])

    while q:
        current = q.popleft()

        # extract the current board and number of lines taken to get there
        currentBoard = current[0]
        numLines = current[1]

        # find the next enemy node position, and then we consider all 'r', 'q' and vertical lines
        # that pass through that node
        nextEnemy = findNextNode(currentBoard, enemyColour)
        
        # lines have crossed out all enemy nodes, so we have found our heuristic
        if not nextEnemy:
            return numLines
        
        # clear all enemy nodes in the 'r' direction, and add the board to the queue
        newBoard = currentBoard.copy()
        for node in R_LINES[nextEnemy]:
            newBoard.pop(node, None)
        q.append((newBoard, numLines + 1))

        # clear all enemy nodes in the 'q' direction, and add the board to the queue
        newBoard = currentBoard.copy()
        for node in Q_LINES[nextEnemy]:
            newBoard.pop(node, None)
        q.append((newBoard, numLines + 1))

        # clear all enemy nodes in the vertical direction, and add the board to the queue
        newBoard = currentBoard.copy()
        for node in V_LINES[nextEnemy]:
            newBoard.pop(node, None)
        q.append((newBoard, numLines + 1))


def findNextNode(board, colour):
    """ Finds the next node on the board with the specified colour """

    for (position, piece) in board.items():
        if piece[0] == colour:
            return position

    # No more nodes left on the board with colour specified
    return None

def victory(board, playerColour):
    """ checks if board has been won for a colour """

    enemyColour = ENEMY[playerColour]

    for piece in board.values():
        if piece[0] == enemyColour:
            return False
    
    return True

def spread(board: dict[tuple, tuple], piece: tuple, direction: tuple):
    """ Spreads a piece (its position) in a direction on the board """

    colour = board.get(piece)[0]
    spreadDistance = board.get(piece)[1]

    temp = piece 
    
    # go through all the spread distance
    while spreadDistance:
        newPosition = findNewPosition(temp, direction)
        spreadToNode(newPosition, board, colour)

        # set temp to new position to use again next iteration
        temp = newPosition

        spreadDistance -= 1

    # spreading piece leaves an empty node
    board.pop(piece)


def findNewPosition(position, direction):
    """ Finds the destination of a node after a move in a direction """

    newR = position[0] + direction[0]
    newQ = position[1] + direction[1]

    # require both r and q to be positive, and also less than the dimension
    if newR < 0:
        newR = DIM - 1
    elif newR >= DIM:
        newR = 0

    if newQ < 0:
        newQ = DIM - 1
    elif newQ >= DIM:
        newQ = 0

    return (newR, newQ)

def spreadToNode(newPosition, board, colour):
    """ 
    Increments power of a node and changes its colour if it is an enemy node, 
    or removing the node if the max power is reached 
    """

    if newPosition not in board.keys():
        board[newPosition] = (colour, 1)
    else:
        power = board.get(newPosition)[1]
        if power == MAX_POWER:
            board.pop(newPosition)
        else:
            board[newPosition] = (colour, 1 + power)
    return

