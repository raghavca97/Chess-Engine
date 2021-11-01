# -------------------------------------------------------------------------------------------------
#                               Movemaker function
# -------------------------------------------------------------------------------------------------

def move():
    turn = 0
    board = chess.Board('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')#initialize the board
    print(board)
    while board.legal_moves != 0:# the game will end if there's no legal move for one player
        turn = turn + 1
        print('Move number {} '.format(board.fullmove_number))
        #b = board.piece_map()   #where the piece is<a dictionary>
        if turn%2 != 0:
            print('White to move')
        else:
            print('Black to move')
        a = board.legal_moves

        print(a)
        i = input('Enter your move: ')
        d = eval(input("Enter depth: "))
        if i != "end":
            move = chess.Move.from_uci(str(board.parse_san(i)))
            board.push(move)
            black_adv = evaluate(board, d)
        print("Black advantage: ", black_adv)
        print(board)
    return(i)

# -------------------------------------------------------------------------------------------------
#                                       Main function
# -------------------------------------------------------------------------------------------------

def main():
    n = 1
    while n:
        turn = move()
        if turn%2 !=0:
            print('Black win')
        else:
            print('White win')
        n = 0
        new = input('Type 1 if you want to start a new game')
        if new == 1:
            n = 1
main()
