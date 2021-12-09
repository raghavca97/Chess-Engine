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
                        'B': 305,
                        'N': 295,
                        'P': 100}
    
    piece_value_black = {'k': 60000,
                        'q': 900,
                        'r': 490,
                        'b': 305,
                        'n': 295,
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

    white_material_score = white_score
    black_material_score = black_score
    

    bishop_pair_bonus = 15 #Bonus for having a bishop pair
    mobility_factor = 5 #Value yet to be incorporated and optimised

    castling_bonus = 100 #Castling implies a safer king and hence this bonus is given(value to be optimised)

    double_pawn_punishment = -40  # Give punishment if there are 2 pawns on the same column, maybe increase if late in game. Calibrate value
    isolated_pawn_punishment = -40  # If the pawn has no allies on the columns next to it, calibrate value later

    knight_endgame_punishment = -20  # Punishment for knights in endgame, per piece
    bishop_endgame_bonus = 20  # Bonus for bishops in endgame, per piece

    rook_on_semi_open_file_bonus = 40  # Give rook a bonus for being on an open file without any own pawns, right now it is per rook
    rook_on_open_file_bonus = 40  # Give rook a bonus for being on an open file without any pawns, right now it is per rook

    blocking_d_e_pawn_punishment = -60  # Punishment for blocking unmoved pawns on d and e file 

    knight_pawn_bonus = 10  # Knights better with lots of pawns
    bishop_pawn_punishment = -10  # Bishops worse with lots of pawns
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

    #if board.fullmove_number > 20 and board.fullmove_number <= 40:
        # Bonus for attacking squares in the center
        #white_score += center_attacks_white * center_attack_bonus_factor
        #black_score += center_attacks_black * center_attack_bonus_factor

# -------------------------------------------------------------------------------------------------
#                               Endgame related functions
# -------------------------------------------------------------------------------------------------

    if white_material_score+black_material_score < 38:

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

    print("White advantage: ", white_score - black_score + 1300)                    
    return black_score - white_score - 1300


