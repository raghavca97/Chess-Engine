import chess # Assuming the latest version of chess is installed in the same directory
import random
# -------------------------------------------------------------------------------------------------
#                               Evaluation function
# -------------------------------------------------------------------------------------------------

def evaluate(board, depth): # Returns advantage of a particular player(scaled by 100 units)
    # Initialize scores and other parameters
    white_score = black_score = 0
    # Check if in checkmate or stalemate
    if board.is_checkmate():
        return 1e9 + depth if board.turn == chess.WHITE else -1e9 - depth
    if board.is_stalemate():
        return 0
    if board.is_insufficient_material():
        return 0
    
    piece_value_white = {'K': 60000,
                        'Q': 900,
                        'R': 490,
                        'B': 320,
                        'N': 290,
                        'P': 100}
    
    piece_value_black = {'k': 60000,
                        'q': 900,
                        'r': 490,
                        'b': 320,
                        'n': 290,
                        'p': 100}

    pos = str(board.fen)
    piecedict = {}
    for i in pos:
        if i in piecedict:
            piecedict[i] += 1
        else:
            piecedict[i] = 1
    
    white_score += piecedict['K']*piece_value_white['K'] + piecedict['Q']*piece_value_white['Q'] + piecedict['B']*piece_value_white['B'] + piecedict['N']*piece_value_white['N'] + piecedict['R']*piece_value_white['R'] + piecedict['P']*piece_value_white['P']
    black_score += piecedict['k']*piece_value_black['k'] + piecedict['q']*piece_value_black['q'] + piecedict['b']*piece_value_black['b'] + piecedict['n']*piece_value_black['n'] + piecedict['r']*piece_value_black['r'] + piecedict['p']*piece_value_black['p']

    bishop_pair_bonus = 15 #Bonus for having a bishop pair
    mobility_factor = 5 #Value yet to be incorporated and optimised

    castling_bonus = 50 #Castling implies a safer king and hence this bonus is given(value to be optimised)

    double_pawn_punishment = -40  # Give punishment if there are 2 pawns on the same column, maybe increase if late in game. Calibrate value
    isolated_pawn_punishment = -40  # If the pawn has no allies on the columns next to it, calibrate value later

    knight_endgame_punishment = -10  # Punishment for knights in endgame, per piece
    bishop_endgame_bonus = 10  # Bonus for bishops in endgame, per piece

    rook_on_semi_open_file_bonus = 20  # Give rook a bonus for being on an open file without any own pawns, right now it is per rook
    rook_on_open_file_bonus = 20  # Give rook a bonus for being on an open file without any pawns, right now it is per rook

    blocking_d_e_pawn_punishment = -40  # Punishment for blocking unmoved pawns on d and e file 

    knight_pawn_bonus = 2  # Knights better with lots of pawns
    bishop_pawn_punishment = -2  # Bishops worse with lots of pawns
    rook_pawn_punishment = -2  # Rooks worse with lots of pawns

    center_attack_bonus_factor = 1  # Factor to multiply with how many center squares are attacked by own pieces(yet to incorporate)
    king_attack_bonus_factor = 5  # Factor to multiply with how many squares around enemy king that are attacked by own pieces(yet to incorporate)

    real_board_squares = [21, 22, 23, 24, 25, 26, 27, 28,
                          31, 32, 33, 34, 35, 36, 37, 38,
                          41, 42, 43, 44, 45, 46, 47, 48,
                          51, 52, 53, 54, 55, 56, 57, 58,
                          61, 62, 63, 64, 65, 66, 67, 68,
                          71, 72, 73, 74, 75, 76, 77, 78,
                          81, 82, 83, 84, 85, 86, 87, 88,
                          91, 92, 93, 94, 95, 96, 97, 98]
    
    manhattan_distance = [6, 5, 4, 3, 3, 4, 5, 6,
                          5, 4, 3, 2, 2, 3, 4, 5,
                          4, 3, 2, 1, 1, 2, 3, 4,
                          3, 2, 1, 0, 0, 1, 2, 3,
                          3, 2, 1, 0, 0, 1, 2, 3,
                          4, 3, 2, 1, 1, 2, 3, 4,
                          5, 4, 3, 2, 2, 3, 4, 5,
                          6, 5, 4, 3, 3, 4, 5, 6]
    
    directions = [-10, -1, 10, 1, -11, -9, 9, 11]

    king_mid = [0,   0,   0,   0,   0,   0,   0,   0,   0, 0,
                0,   0,   0,   0,   0,   0,   0,   0,   0, 0,
                0, -30, -40, -40, -50, -50, -40, -40, -30, 0,
                0, -30, -40, -40, -50, -50, -40, -40, -30, 0,
                0, -30, -40, -40, -50, -50, -40, -40, -30, 0,
                0, -30, -40, -40, -50, -50, -40, -40, -30, 0,
                0, -20, -30, -30, -40, -40, -30, -30, -20, 0,
                0, -10, -20, -20, -20, -20, -20, -20, -10, 0,
                0,  20,  20,   0,   0,   0,   0,  20,  20, 0,
                0,  0,  20,   40,   0,   0,   0,  40,  20, 0,
                0,   0,   0,   0,   0,   0,   0,   0,   0, 0,
                0,   0,   0,   0,   0,   0,   0,   0,   0, 0]
    queen_mid = [0,   0,   0,   0,  0,  0,   0,   0,   0, 0,
                 0,   0,   0,   0,  0,  0,   0,   0,   0, 0,
                 0, -20, -10, -10, -5, -5, -10, -10, -20, 0,
                 0, -10,   0,   0,  0,  0,   0,   0, -10, 0,
                 0, -10,   0,   5,  5,  5,   5,   0, -10, 0,
                 0,  -5,   0,   5,  5,  5,   5,   0,  -5, 0,
                 0,  -5,   0,   5,  5,  5,   5,   0,  -5, 0,
                 0, -10,   5,   5,  5,  5,   5,   0, -10, 0,
                 0, -10,   0,   5,  0,  0,   0,   0, -10, 0,
                 0, -20, -10, -10,  0,  0, -10, -10, -20, 0,
                 0,   0,   0,   0,  0,  0,   0,   0,   0, 0,
                 0,   0,   0,   0,  0,  0,   0,   0,   0, 0]
    rook_mid = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 5, 15, 15, 15, 15, 15, 15, 5, 0,
                0, -5, 0, 0, 0, 0, 0, 0, -5, 0,
                0, -5, 0, 0, 0, 0, 0, 0, -5, 0,
                0, -5, 0, 0, 0, 0, 0, 0, -5, 0,
                0, -5, 0, 0, 0, 0, 0, 0, -5, 0,
                0, -5, 0, 0, 0, 0, 0, 0, -5, 0,
                0, 0, 0, 10, 10, 10, 10, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    bishop_mid = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                  0, -20, -10, -10, -10, -10, -10, -10, -20, 0,
                  0, -10, 0, 0, 0, 0, 0, 0, -10, 0,
                  0, -10, 0, 5, 10, 10, 5, 0, -10, 0,
                  0, -10, 5, 5, 10, 10, 5, 5, -10, 0,
                  0, -10, 0, 10, 10, 10, 10, 0, -10, 0,
                  0, -10, 10, 10, 10, 10, 10, 10, -10, 0,
                  0, -10, 10, 0, 10, 10, 0, 10, -10, 0,
                  0, -20, -10, -50, -10, -10, -50, -10, -20, 0,
                  0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    knight_mid = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                  0, -30, -30, -10, -10, -10, -10, -30, -30, 0,
                  0, -20, -20, 0, 0, 0, 0, -20, -20, 0,
                  0, -10, 0, 10, 15, 15, 10, 0, -10, 0,
                  0, -10, 5, 15, 20, 20, 15, 5, -10, 0,
                  0, -10, 0, 15, 20, 20, 15, 0, -10, 0,
                  0, -10, 5, 10, 15, 15, 10, 5, -10, 0,
                  0, -20, -20, 0, 5, 5, 0, -20, -20, 0,
                  0, -30, -30, -10, -10, -10, -10, -30, -30, 0,
                  0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    pawn_mid = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 50, 50, 50, 50, 50, 50, 50, 50, 0,
                0, 20, 20, 20, 30, 30, 20, 20, 20, 0,
                0, 10, 10, 10, 25, 25, 10, 10, 10, 0,
                0, 0, 0, 0, 20, 20, 0, 0, 0, 0,
                0, 5, -5, -10, 0, 0, -10, -5, 5, 0,
                0, 5, 10, 10, -20, -20, 10, 10, 5, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    king_end = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, -24, -23, -22, -21, -21, -22, -23, -24, 0,
                0, -23, -12, -10,  -10, -10, -10, -10, -23, 0,
                0, -22, -10,  20,  30, 30, 20, -10, -22, 0,
                0, -21, -10,  30,  40, 40, 30, -10, -21, 0,
                0, -21, -10,  30,  40, 40, 30, -10, -21, 0,
                0, -22, -10,  20,  30,  30,  20, -10, -22, 0,
                0, -23, -12, -10, -10, -10,  -10, -12, -23, 0,
                0, -24, -23, -22, -21, -21, -22, -23, -24, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    queen_end = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                 0, -20, -10, -10, -5, -5, -10, -10, -20, 0,
                 0, -10, 0, 0, 0, 0, 0, 0, -10, 0,
                 0, -10, 0, 5, 5, 5, 5, 0, -10, 0,
                 0, -5, 0, 5, 5, 5, 5, 0, -5, 0,
                 0, -5, 0, 5, 5, 5, 5, 0, -5, 0,
                 0, -10, 5, 5, 5, 5, 5, 0, -10, 0,
                 0, -10, 0, 5, 0, 0, 0, 0, -10, 0,
                 0, -20, -10, -10, 0, 0, -10, -10, -20, 0,
                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    rook_end = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 5, 15, 15, 15, 15, 15, 15, 5, 0,
                0, -5, 0, 0, 0, 0, 0, 0, -5, 0,
                0, -5, 0, 0, 0, 0, 0, 0, -5, 0,
                0, -5, 0, 0, 0, 0, 0, 0, -5, 0,
                0, -5, 0, 0, 0, 0, 0, 0, -5, 0,
                0, -5, 0, 0, 0, 0, 0, 0, -5, 0,
                0, 0, 0, 5, 10, 10, 5, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    bishop_end = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                  0, -20, -10, -10, -10, -10, -10, -10, -20, 0,
                  0, -10, 0, 0, 0, 0, 0, 0, -10, 0,
                  0, -10, 0, 5, 10, 10, 5, 0, -10, 0,
                  0, -10, 5, 5, 10, 10, 5, 5, -10, 0,
                  0, -10, 0, 10, 10, 10, 10, 0, -10, 0,
                  0, -10, 10, 10, 10, 10, 10, 10, -10, 0,
                  0, -10, 5, 0, 0, 0, 0, 5, -10, 0,
                  0, -20, -10, -10, -10, -10, -10, -10, -20, 0,
                  0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    knight_end = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                  0, -50, -40, -30, -30, -30, -30, -40, -50, 0,
                  0, -40, -20, 0, 0, 0, 0, -20, -40, 0,
                  0, -30, 0, 10, 15, 15, 10, 0, -30, 0,
                  0, -30, 5, 15, 20, 20, 15, 5, -30, 0,
                  0, -30, 0, 15, 20, 20, 15, 0, -30, 0,
                  0, -30, 5, 10, 15, 15, 10, 5, -30, 0,
                  0, -40, -20, 0, 5, 5, 0, -20, -40, 0,
                  0, -50, -40, -30, -30, -30, -30, -40, -50, 0,
                  0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    pawn_end = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 50, 50, 50, 50, 50, 50, 50, 50, 0,
                0, 30, 30, 30, 30, 30, 30, 30, 30, 0,
                0, 20, 20, 20, 25, 25, 20, 20, 20, 0,
                0, 10, 10, 10, 10, 10, 10, 10, 10, 0,
                0, -5, -5, -5, -5, -5, -5, -5, -5, 0,
                0, -10, -10, -10, -20, -20, -10, -10, -10, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

#  --------------------------------------------------------------------------------
#           Pre-calculated tables to speed up game(Yet to incorporate)
#  --------------------------------------------------------------------------------

# Number of squares that a piece is attacking the opponent king
    piece_king_attack = {'K': 0,
                        'Q': 5,
                        'R': 2,
                        'B': 5,
                        'N': 5,
                        'p': 4}

    king_attack_squares = {}
    for square in real_board_squares:
        king_attack_squares[square] = []

    for square in real_board_squares:
        for d in directions:
            attack_square = square + d
            if attack_square in real_board_squares:
                king_attack_squares[square].append(attack_square)

# Number of squares that a piece is attacking in the center 4 squares and the surrounding ones
    piece_center_attack = {'K': 0,
                           'Q': 2,
                           'R': 2,
                           'B': 5,
                           'N': 5,
                           'p': 5}

# -------------------------------------------------------------------------------------------------
#                          Up until endgame evaluation
# -------------------------------------------------------------------------------------------------

    # Opening related bonuses/punishment
    if board.fullmove_number <= 20:

        # Castling bonus
        if board.has_castling_rights(chess.WHITE) == 0:
            white_score += castling_bonus
        if board.has_castling_rights(chess.BLACK) == 0:
            black_score += castling_bonus
    
    pm = board.piece_map()
    
    j = 0
    for i in chess.SQUARES:
        if pm.get(i) == "P":
            white_score += pawn_mid[j]
            j+=1
            continue
        if pm.get(i) == "p":
            black_score += pawn_mid[j]
            j+=1
            continue
        if pm.get(i) == "B":
            white_score += bishop_mid[j]
            j+=1
            continue
        if pm.get(i) == "b":
            black_score += bishop_mid[j]
            j+=1
            continue
        if pm.get(i) == "N":
            white_score += knight_mid[j]
            j+=1
            continue
        if pm.get(i) == "n":
            black_score += knight_mid[j]
            j+=1
            continue
        if pm.get(i) == "R":
            white_score += rook_mid[j]
            j+=1
            continue
        if pm.get(i) == "r":
            black_score += rook_mid[j]
            j+=1
            continue
        if pm.get(i) == "Q":
            white_score += queen_mid[j]
            j+=1
            continue    
        if pm.get(i) == "q":
            black_score += queen_mid[j]
            j+=1
            continue
        if pm.get(i) == "K":
            white_score += king_mid[j]
            j+=1
            continue
        if pm.get(i) == "k":
            black_score += king_mid[j]
            j+=1
            continue
    
    # Punishment for pieces in front of undeveloped d and e pawns
    if pm.get(chess.D2) == 'P' and pm.get(chess.D3) != 'None':
        white_score += blocking_d_e_pawn_punishment
    if pm.get(chess.E2) == 'P' and pm.get(chess.E3) != 'None':
        white_score += blocking_d_e_pawn_punishment

    if pm.get(chess.D7) == 'p' and pm.get(chess.D6) != 'None':
        black_score += blocking_d_e_pawn_punishment
    if pm.get(chess.E7) == 'p' and pm.get(chess.E6) != 'None':
        black_score += blocking_d_e_pawn_punishment

    # Bishop pair bonus
    if piecedict['B'] == 2:
        white_score += bishop_pair_bonus
    if piecedict['b'] == 2:
        black_score += bishop_pair_bonus

    # Double pawn punishment
    wsquares = list(board.pieces(chess.PAWN ,chess.WHITE))
    bsquares = list(board.pieces(chess.PAWN ,chess.BLACK))
    for i in range(len(wsquares)):
        for j in range(1,len(wsquares)):
            if (wsquares[j]-wsquares[i])%8 == 0:
                if wsquares[j]!=wsquares[i]:
                    white_score += double_pawn_punishment

    for i in range(len(bsquares)):
        for j in range(1,len(bsquares)):
            if (bsquares[j]-bsquares[i])%8 == 0:
                if bsquares[j]!=bsquares[i]:
                    black_score += double_pawn_punishment
    
    # Isolated pawn punishment
    for i in range(len(wsquares)):
        if wsquares[i]+1 not in wsquares and wsquares[i]-1 not in wsquares and wsquares[i]+7 not in wsquares and wsquares[i]+9 not in wsquares and wsquares[i]-7 not in wsquares and wsquares[i]-9 not in wsquares:
            if wsquares[i]+41 not in wsquares and wsquares[i]+39 not in wsquares and wsquares[i]+33 not in wsquares and wsquares[i]+31 not in wsquares and wsquares[i]+25 not in wsquares and wsquares[i]+23 not in wsquares and wsquares[i]+17 not in wsquares and wsquares[i]+15 not in wsquares:
                if wsquares[i]-41 not in wsquares and wsquares[i]-39 not in wsquares and wsquares[i]-33 not in wsquares and wsquares[i]-31 not in wsquares and wsquares[i]-25 not in wsquares and wsquares[i]-23 not in wsquares and wsquares[i]-17 not in wsquares and wsquares[i]-15 not in wsquares:
                    white_score += isolated_pawn_punishment

    for i in range(len(bsquares)):
        if bsquares[i]+1 not in bsquares and bsquares[i]-1 not in bsquares and bsquares[i]+7 not in bsquares and bsquares[i]+9 not in bsquares and bsquares[i]-7 not in bsquares and bsquares[i]-9 not in bsquares:
            if bsquares[i]+41 not in bsquares and bsquares[i]+39 not in bsquares and bsquares[i]+33 not in bsquares and bsquares[i]+31 not in bsquares and bsquares[i]+25 not in bsquares and bsquares[i]+23 not in bsquares and bsquares[i]+17 not in bsquares and bsquares[i]+15 not in bsquares:
                if bsquares[i]-41 not in bsquares and bsquares[i]-39 not in bsquares and bsquares[i]-33 not in bsquares and bsquares[i]-31 not in bsquares and bsquares[i]-25 not in bsquares and bsquares[i]-23 not in bsquares and bsquares[i]-17 not in bsquares and bsquares[i]-15 not in bsquares:
                    black_score += isolated_pawn_punishment
    
    # Rook on open and semi-open file bonus
    wrsquares = list(board.pieces(chess.ROOK ,chess.WHITE))
    brsquares = list(board.pieces(chess.ROOK ,chess.BLACK))
    for i in wrsquares:
        flag = 0
        j = i + 8
        last_rank = [56, 57, 58, 59, 60, 61, 62, 63]
        while j not in last_rank:
            if j in list(board.pieces(chess.PAWN ,chess.WHITE)):
                flag = 1
                break
            j += 8
        if flag == 0:
            white_score += rook_on_semi_open_file_bonus
    
    for i in brsquares:
        flag = 0
        j = i - 8
        last_rank = [0, 1, 2, 3, 4, 5, 6, 7]
        while j not in last_rank:
            if j in list(board.pieces(chess.PAWN ,chess.BLACK)):
                flag = 1
                break
            j -= 8
        if flag == 0:
            black_score += rook_on_semi_open_file_bonus
    
    for i in wrsquares:
        flag = 0
        j = i + 8
        last_rank = [56, 57, 58, 59, 60, 61, 62, 63]
        while j not in last_rank:
            if j in list(board.pieces(chess.PAWN ,chess.WHITE)) or j in list(board.pieces(chess.PAWN, chess.BLACK)):
                flag = 1
                break
            j += 8
        if flag == 0:
            white_score += rook_on_open_file_bonus
    
    for i in brsquares:
        flag = 0
        j = i - 8
        last_rank = [0, 1, 2, 3, 4, 5, 6, 7]
        while j not in last_rank:
            if j in list(board.pieces(chess.PAWN ,chess.BLACK)) or j in list(board.pieces(chess.PAWN ,chess.WHITE)):
                flag = 1
                break
            j -= 8
        if flag == 0:
            black_score += rook_on_open_file_bonus
    
    
    # Bonus for attacking squares around the enemy king (Yet to incorporate)
    #white_score += king_attacks_white * king_attack_bonus_factor
    #black_score += king_attacks_black * king_attack_bonus_factor

# -------------------------------------------------------------------------------------------------
#                              Midgame related functions(Yet to incorporate)
# -------------------------------------------------------------------------------------------------

    #if board.fullmove_number > 20 and board.fullmove_number <= 35:
        # Bonus for attacking squares in the center
        #white_score += center_attacks_white * center_attack_bonus_factor
        #black_score += center_attacks_black * center_attack_bonus_factor

# -------------------------------------------------------------------------------------------------
#                               Endgame related functions
# -------------------------------------------------------------------------------------------------

    if board.fullmove_number > 35:

        j = 0
        for i in chess.SQUARES:
            j += 1
            if pm.get(i) == "P":
                white_score += pawn_end[j]
                j+=1
                continue
            if pm.get(i) == "p":
                black_score += pawn_end[j]
                j+=1
                continue
            if pm.get(i) == "B":
                white_score += bishop_end[j]
                j+=1
                continue
            if pm.get(i) == "b":
                black_score += bishop_end[j]
                j+=1
                continue
            if pm.get(i) == "N":
                white_score += knight_end[j]
                j+=1
                continue
            if pm.get(i) == "n":
                black_score += knight_end[j]
                j+=1
                continue
            if pm.get(i) == "R":
                white_score += rook_end[j]
                j+=1
                continue
            if pm.get(i) == "r":
                black_score += rook_end[j]
                j+=1
                continue
            if pm.get(i) == "Q":
                white_score += queen_end[j]
                j+=1
                continue    
            if pm.get(i) == "q":
                black_score += queen_end[j]
                j+=1
                continue
            if pm.get(i) == "K":
                white_score += king_end[j]
                j+=1
                continue
            if pm.get(i) == "k":
                black_score += king_end[j]
                j+=1
                continue    

        # Knights are worth slightly less in endgame
        white_score += piecedict['N'] * knight_endgame_punishment
        black_score += piecedict['n'] * knight_endgame_punishment

        # Bishops are worth slightly more in endgame
        white_score += piecedict['B'] * bishop_endgame_bonus
        black_score += piecedict['b'] * bishop_endgame_bonus

        # Knights better with lots of pawns, bishops worse. Rooks better with less pawns.
        white_score += piecedict['N'] * piecedict['P'] * knight_pawn_bonus
        black_score += piecedict['n'] * piecedict['p'] * knight_pawn_bonus

        white_score += piecedict['B'] * piecedict[0]['P'] * bishop_pawn_punishment
        black_score += piecedict['b'] * piecedict[1]['p'] * bishop_pawn_punishment

        white_score += piecedict['R'] * piecedict['P'] * rook_pawn_punishment
        black_score += piecedict['r'] * piecedict['p'] * rook_pawn_punishment

        # Finding mate with no pawns on the board and without syzygy endgame tablebase.
        if piecedict['p'] == piecedict['P'] == 0:
            # Add a small term for piece values, otherwise the algorithm might sacrifice a piece sometimes for no reason.
            white_score = 0.05*piecedict['K']*piece_value_white['K'] + piecedict['Q']*piece_value_white['Q'] + piecedict['B']*piece_value_white['B'] + piecedict['N']*piece_value_white['N'] + piecedict['R']*piece_value_white['R'] + piecedict['P']*piece_value_white['P']
            black_score = 0.05*piecedict['k']*piece_value_black['k'] + piecedict['q']*piece_value_black['q'] + piecedict['b']*piece_value_black['b'] + piecedict['n']*piece_value_black['n'] + piecedict['r']*piece_value_black['r'] + piecedict['p']*piece_value_black['p']
            # White advantage (no rooks or queens on enemy side and a winning advantage)
            if piecedict['r'] == piecedict['q'] == 0 and white_score > black_score:
                # Lone K vs K and (R, Q and/or at least 2xB). Only using mop-up evaluation.
                if piecedict['R'] >= 1 or piecedict['Q'] >= 1 or piecedict['B'] >= 2:
                    black_king_real_pos = real_board_squares.index(board.king(chess.BLACK))
                    white_king_real_pos = real_board_squares.index(board.king(chess.WHITE))
                    white_score += 4.7 *manhattan_distance[black_king_real_pos] + 1.6 * (14 - manhattan_distance[black_king_real_pos] - manhattan_distance[white_king_real_pos])
                # Lone K vs K, N and B
                if piecedict['R'] == piecedict['Q'] == 0 and piecedict['B'] >= 1 and piecedict['N'] >= 1:
                    pass
            # Black advantage (no rooks or queens on enemy side and a winning advantage)
            if piecedict['R'] == piecedict['Q'] == 0 and black_score > white_score:
                # Lone K vs K and (R, Q and/or at least 2xB). Only using mop-up evaluation.
                if piecedict['r'] >= 1 or piecedict['q'] >= 1 or piecedict['b'] >= 2:
                    white_king_real_pos = real_board_squares.index(board.king(chess.WHITE))
                    black_king_real_pos = real_board_squares.index(board.king(chess.BLACK))
                    black_score += 4.7 * manhattan_distance[white_king_real_pos] + 1.6 * (14 - manhattan_distance[white_king_real_pos] - manhattan_distance[black_king_real_pos])
                # Lone K vs K, N and B
                if piecedict['r'] == piecedict['q'] == 0 and piecedict['b'] >= 1 and piecedict['n'] >= 1:
                    pass

    print("White advantage: ", white_score - black_score + 1560)                    
    return black_score - white_score - 1560


# -------------------------------------------------------------------------------------------------
#         Tree algorithm to evaluate to the given depth (Yet to incorporate to main function)
# -------------------------------------------------------------------------------------------------
class MoveNode:
    def __init__(self, Board):
        self.board = Board
        self.children = []
        self.eval = 0
        self.next = None
        self.nextmove = None

def wfa(node, depth):
    #evaluate current board
    node.eval = evaluate(node.board, depth)
    
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
    node.eval = evaluate(node.board, depth)
    
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


def simulategame(s, d, nm):
    random.seed(s)
    depth = d
    board = chess.Board()
    nmoves = 0
    while board.is_game_over() == False and nmoves < nm:
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
    i = 0
    while (i < depth) and temp.board.is_checkmate()==False:
        print(temp.nextmove, end = ' -> ')
        temp = temp.next
        i=i+1
    print('...')

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