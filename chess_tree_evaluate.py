#!/usr/bin/env python
# coding: utf-8

# In[3]:


import chess
import random

class MoveNode:
    def __init__(self, Board):
        self.board = Board
        self.children = []
        self.eval = 0
        self.next = None
        self.nextmove = None
        
def evaluate(board):
    #Random number generator for evaluation for now
    return random.gauss(0, 1)
    
    
def wfa(node, depth):
    #evaluate current board
    node.eval = evaluate(node.board)
    
    #return if max depth has been reached
    if depth == 0:
        return node.eval
    
    #create an indexable list of legal moves
    lm = list(node.board.legal_moves)
    childeval = []

    if len(lm) == 0:
        return node.eval
    
    # iterate through each legal move and call bfd to evaluate each child
    for i in range(len(lm)):
        child = MoveNode(node.board.copy())
        child.board.push(lm[i])
        node.children.append(child)
        childeval.append(bfd(child, depth-1))
    
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
        
def bfd(node, depth):
    #evaluate current board
    node.eval = evaluate(node.board)
    
    #return if max depth has been reached
    if depth == 0:
        return node.eval
    
    #create an indexable list of legal moves
    lm = list(node.board.legal_moves)
    childeval = []
    
    if len(lm) == 0:
        return node.eval
    
    # iterate through each legal move and call wfa to evaluate each child
    for i in range(len(lm)):
        child = MoveNode(node.board.copy())
        child.board.push(lm[i])
        node.children.append(child)
        childeval.append(wfa(child, depth-1))
    
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

def treestart(node, depth):
    if node.board.turn == chess.WHITE:
        return wfa(node, depth)
    else:
        return bfd(node, depth)


def simulategame(s, d):
    random.seed(s)
    depth = d
    board = chess.Board()
    nmoves = 0
    while board.is_game_over() == False and nmoves <30:
        print(board, '\n')
        root = MoveNode(board)
        ev = treestart(root, depth)
        print("eval: ",ev)
        board.push(root.nextmove)
        nmoves += 1
        
        
def evalposfromfen(fen, d):
    depth = d
    board = chess.Board(fen)
    print(board, '\n')
    root = MoveNode(board)
    ev = wfa(root, depth)
    print("eval: ",ev)

    temp = root
    print()
    i = 0;
    while (i < depth) and temp.board.is_checkmate()==False:
        print(temp.nextmove, end = ' -> ')
        temp = temp.next
        i=i+1
    print('...')

# In[4]:


evalposfromfen("rnbqk2r/pppp1ppp/5n2/2b5/4Pp2/2NP4/PPP3PP/R1BQKBNR w KQkq - 0 5", 3)






