# Contains functions to map nodes to lines of nodes on the board based on direction 'r' ,'q', 'v'

DIM = 7

def getRLines():
    lines = {}

    for q in range(DIM):
        tup = tuple(((i, q) for i in range(DIM)))
        for r in range(DIM):
            lines[(r,q)] = tup

    return lines

def getQLines():
    lines = {}

    for r in range(DIM):
        tup = tuple(((r, i) for i in range(DIM)))
        for q in range(DIM):
            lines[(r,q)] = tup

    return lines

def getVLines():
    lines = {} 

    linesTemp = []
    for i in range(DIM):
        start = (0, i)
        oneLine = [start]
        for j in range(DIM - 1):
            r = oneLine[j][0] + 1
            q = oneLine[j][1] - 1
            if q < 0:
                q = DIM - 1
            oneLine.append((r,q))
        linesTemp.append(tuple(oneLine))

    for vLine in linesTemp:
        for position in vLine:
            lines[position] = vLine
    
    return lines