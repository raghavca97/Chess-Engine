import chess
from Evaluation import evaluate

class MoveNode:
    def __init__(self, Board):
        self.board = Board
        self.children = []
        self.eval = 0
        self.next = None
        self.nextmove = None
    
    
    
#White player trying to maximize advantage
#Inputs:
#node: Node object of board and evaluation and an array of children nodes
#depth: remaining plys to investigate
#currentdepth: number of plys investigated so far in recursive tree building
#al: alpha, the highest advantage the minimizing player has allowed thus far, given in centipawn advantage for white
#be: beta, the lowest advantage the maximizing player can attain thus far, given in centipawn advantage for white
#tolerance: tolerance for positions that are lower than the beta but will not be pruning by alpha-beta pruning, given in centipawn advantage for white
#Outputs:
#ev: evaluation of the board associated with the input node, given in centipawn advantage for white
def whiteForAdvantage(node, depth, currentdepth, al, be, tolerance):
    #evaluate current board
    #print("white to move, depth = ", currentdepth," remaining = ",depth," ",al," ",be, "\n")
    node.eval = -1*evaluate(node.board, currentdepth)
    print(node.board, '\n\n')
    
    #return if max depth has been reached
    if depth == 0:
        return node.eval
    
    #create an indexable list of legal moves
    lm = list(node.board.legal_moves)
    childeval = []

    
    
    if len(lm) == 0:
        return node.eval
    
    # iterate through each legal move and call blackForDefense to evaluate each child
    for i in range(len(lm)):
        child = MoveNode(node.board.copy())
        child.board.push(lm[i])
        ev = blackForDefense(child, depth-1, currentdepth+1, al, be, tolerance)
        
        if ev>al:
            al = ev
        
        if ev>=be-tolerance or len(childeval) == 0:
            if len(childeval) ==0:
                be = ev
            node.children.append(child)
            childeval.append(ev)
               
    #iterate through list of children nodes to get the node with the max eval
    node.eval = childeval[0]
    node.next = node.children[0]
    node.nextmove = lm[0]
    for i in range(len(childeval)):
        if node.eval < childeval[i]:
            node.eval = childeval[i]
            node.next = node.children[i]
            node.nextmove = lm[i]
    return node.eval



#Black player trying to minimize advantage
#Inputs:
#node: Node object of board and evaluation and an array of children nodes
#depth: remaining plys to investigate
#currentdepth: number of plys investigated so far in recursive tree building
#al: alpha, the highest advantage the minimizing player has allowed thus far, given in centipawn advantage for white
#be: beta, the lowest advantage the maximizing player can attain thus far, given in centipawn advantage for white
#tolerance: tolerance for positions that are higher than alpha but will not be pruning by alpha-beta pruning, given in centipawn advantage for white
#Outputs:
#ev: evaluation of the board associated with the input node, given in centipawn advantage for white
def blackForDefense(node, depth, currentdepth, al, be, tolerance):
    #evaluate current board
    print("Black to move, depth = ", currentdepth," remaining = ",depth," ",al," ",be, "\n")
    node.eval = -1*evaluate(node.board, currentdepth)
    print(node.board, '\n\n')
    
    #return if max depth has been reached
    if depth == 0:
        return node.eval
    
    #create an indexable list of legal moves
    lm = list(node.board.legal_moves)
    childeval = []
    
    if len(lm) == 0:
        return node.eval
    
    # iterate through each legal move and call whiteForAdvantage to evaluate each child
    for i in range(len(lm)):
        child = MoveNode(node.board.copy())
        child.board.push(lm[i])
        
        ev = whiteForAdvantage(child, depth-1, currentdepth+1, al, be, tolerance)
        
        if ev<be:
            be = ev
        
        if ev<=al+tolerance or len(childeval) == 0:
            if len(childeval) ==0:
                al = ev
            node.children.append(child)
            childeval.append(ev)
            
    #iterate through list of children nodes to get the node with the min eval
    node.eval = childeval[0]
    node.next = node.children[0]
    node.nextmove = lm[0]
    for i in range(len(childeval)):
        if node.eval > childeval[i]:
            node.eval = childeval[i]
            node.next = node.children[i]
            node.nextmove = lm[i]
    return node.eval



#Determines whos move it is and starts recursive tree search with the corresponding player
#Inputs:
#node: Node object of board and evaluation and an array of children nodes
#depth: remaining plys to investigate
#tolerance: tolerance for positions that are higher than alpha but will not be pruning by alpha-beta pruning, given in centipawn advantage for white
#Outputs:
#ev: evaluation of the board associated with the input node, given in centipawn advantage for white
def treestart(node, depth, tolerance):
    al = be = -1*evaluate(node.board, 0)
    if node.board.turn == chess.WHITE:
        return whiteForAdvantage(node, depth, 0, al, be, tolerance)
    else:
        return blackForDefense(node, depth, 0, al, be, tolerance)


#Accepts a board and uses tree functions to get evaluation
#Inputs:
#Board: python-chess board object
#depth: remaining plys to investigate
#Outputs:
#ev: evaluation of the board associated with the input node, given in centipawn advantage for white
def evalboard(board, depth):
    root = MoveNode(board)
    ev = treestart(root, depth, 0)
    temp = root
    print("eval: ",ev)
    i = 0
    while (i < depth) and temp.board.is_checkmate()==False:
        print(temp.nextmove, end = ' -> ')
        temp = temp.next
        i=i+1
    print('...')
    return ev
        
        
def evalposfromfen(fen, depth):
    board = chess.Board(fen)
    evalboard(board,depth)
        
        
def evalpostest():
    board = chess.Board()
    evaluate(board,0)   

    
    
#evalposfromfen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", 3)
