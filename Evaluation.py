#  --------------------------------------------------------------------------------
#                 Evaluates a given board and returns a score
#  --------------------------------------------------------------------------------
def evaluate(gamestate, depth):

    # Initialize scores and other parameters
    white_score = black_score = 0

    # Check if in checkmate or stalemate
    if gamestate.is_check_mate:
        return 1e9 + depth if gamestate.is_white_turn else -1e9 - depth
    if gamestate.is_stale_mate:
        return 0

    # Piece values with base and piece-dependent values (updated in make/unmake move functions)
    white_score += gamestate.piece_values[0]
    black_score += gamestate.piece_values[1]

    bishop_pair_bonus = 15
    mobility_factor = 5

    castling_bonus = 50 

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

    center_attack_bonus_factor = 1  # Factor to multiply with how many center squares are attacked by own pieces
    king_attack_bonus_factor = 5  # Factor to multiply with how many squares around enemy king that are attacked by own pieces

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
#                    Pre-calculated tables to speed up game
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

    center_attacks = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 1, 1, 1, 1, 0, 0, 0,
                      0, 0, 0, 1, 2, 2, 1, 0, 0, 0,
                      0, 0, 0, 1, 2, 2, 1, 0, 0, 0,
                      0, 0, 0, 1, 1, 1, 1, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

# -------------------------------------------------------------------------------------------------
#                          Up until endgame evaluation
# -------------------------------------------------------------------------------------------------

    # Opening related bonuses/punishment
    if len(gamestate.move_log) < 30:

        # Castling bonus
        if gamestate.white_has_castled:
            white_score += castling_bonus
        if gamestate.black_has_castled:
            black_score += castling_bonus

    # Punishment for pieces in front of undeveloped d and e pawns
    if gamestate.board[84] == 'wp' and gamestate.board[74] != '--':
        white_score += blocking_d_e_pawn_punishment
    if gamestate.board[85] == 'wp' and gamestate.board[75] != '--':
        white_score += blocking_d_e_pawn_punishment

    if gamestate.board[34] == 'bp' and gamestate.board[44] != '--':
        black_score += blocking_d_e_pawn_punishment
    if gamestate.board[35] == 'bp' and gamestate.board[45] != '--':
        black_score += blocking_d_e_pawn_punishment

    # Bishop pair bonus
    if gamestate.piece_dict[0]['B'] == 2:
        white_score += bishop_pair_bonus
    if gamestate.piece_dict[1]['B'] == 2:
        black_score += bishop_pair_bonus

    # Double pawn punishment
    white_pawns, black_pawns = set(gamestate.pawn_columns_list[0]), set(gamestate.pawn_columns_list[1])
    white_score += (len(gamestate.pawn_columns_list[0]) - len(white_pawns)) * double_pawn_punishment
    black_score += (len(gamestate.pawn_columns_list[1]) - len(black_pawns)) * double_pawn_punishment

    # Isolated pawn punishment
    white_score += len([i for i in white_pawns if i - 1 not in white_pawns and i + 1 not in white_pawns]) * isolated_pawn_punishment
    black_score += len([i for i in black_pawns if i - 1 not in black_pawns and i + 1 not in black_pawns]) * isolated_pawn_punishment

    # Rook on open and semi-open file bonus
    for rook in gamestate.rook_columns_list[0]:
        if rook not in white_pawns:
            white_score += rook_on_semi_open_file_bonus
            if rook not in black_pawns:
                white_score += rook_on_open_file_bonus
    for rook in gamestate.rook_columns_list[1]:
        if rook not in black_pawns:
            black_score += rook_on_semi_open_file_bonus
            if rook not in white_pawns:
                black_score += rook_on_open_file_bonus

    # Bonus for attacking squares around the enemy king
    white_score += gamestate.king_attacks_white * king_attack_bonus_factor
    black_score += gamestate.king_attacks_black * king_attack_bonus_factor

# -------------------------------------------------------------------------------------------------
#                              Midgame related functions
# -------------------------------------------------------------------------------------------------

    if gamestate.endgame < 1:
        # Bonus for attacking squares in the center
        white_score += gamestate.center_attacks_white * center_attack_bonus_factor
        black_score += gamestate.center_attacks_black * center_attack_bonus_factor

# -------------------------------------------------------------------------------------------------
#                               Endgame related functions
# -------------------------------------------------------------------------------------------------

    if gamestate.endgame == 1:

        # Knights are worth slightly less in endgame
        white_score += gamestate.piece_dict[0]['N'] * knight_endgame_punishment
        black_score += gamestate.piece_dict[1]['N'] * knight_endgame_punishment

        # Bishops are worth slightly more in endgame
        white_score += gamestate.piece_dict[0]['B'] * bishop_endgame_bonus
        black_score += gamestate.piece_dict[1]['B'] * bishop_endgame_bonus

        # Knights better with lots of pawns, bishops worse. Rooks better with less pawns.
        white_score += (gamestate.piece_dict[0]['N'] * gamestate.piece_dict[0]['p']) * knight_pawn_bonus
        black_score += (gamestate.piece_dict[1]['N'] * gamestate.piece_dict[1]['p']) * knight_pawn_bonus

        white_score += (gamestate.piece_dict[0]['B'] * gamestate.piece_dict[0]['p']) * bishop_pawn_punishment
        black_score += (gamestate.piece_dict[1]['B'] * gamestate.piece_dict[1]['p']) * bishop_pawn_punishment

        white_score += (gamestate.piece_dict[0]['R'] * gamestate.piece_dict[0]['p']) * rook_pawn_punishment
        black_score += (gamestate.piece_dict[1]['R'] * gamestate.piece_dict[1]['p']) * rook_pawn_punishment

        # Finding mate with no pawns on the board and without syzygy.
        if gamestate.piece_dict[0]['p'] == gamestate.piece_dict[1]['p'] == 0:
            # Add a small term for piece values, otherwise the algorithm might sacrifice a piece sometimes for no reason.
            white_score = 0.05*gamestate.piece_values[0]
            black_score = 0.05*gamestate.piece_values[1]
            # White advantage (no rooks or queens on enemy side and a winning advantage)
            if gamestate.piece_dict[1]['R'] == gamestate.piece_dict[1]['Q'] == 0 and white_score > black_score:
                # Lone K vs K and (R, Q and/or at least 2xB). Only using mop-up evaluation.
                if gamestate.piece_dict[0]['R'] >= 1 or gamestate.piece_dict[0]['Q'] >= 1 or gamestate.piece_dict[0]['B'] >= 2:
                    black_king_real_pos = real_board_squares.index(gamestate.black_king_location)
                    white_score += 4.7 *manhattan_distance[black_king_real_pos] + 1.6 * (14 - gamestate.kings_distance)
                # Lone K vs K, N and B
                if gamestate.piece_dict[0]['R'] == gamestate.piece_dict[0]['Q'] == 0 and gamestate.piece_dict[0]['B'] >= 1 and gamestate.piece_dict[0]['N'] >= 1:
                    pass
            # Black advantage (no rooks or queens on enemy side and a winning advantage)
            if gamestate.piece_dict[0]['R'] == gamestate.piece_dict[0]['Q'] == 0 and black_score > white_score:
                # Lone K vs K and (R, Q and/or at least 2xB). Only using mop-up evaluation.
                if gamestate.piece_dict[1]['R'] >= 1 or gamestate.piece_dict[1]['Q'] >= 1 or gamestate.piece_dict[1]['B'] >= 2:
                    white_king_real_pos = real_board_squares.index(gamestate.white_king_location)
                    black_score += 4.7 * manhattan_distance[white_king_real_pos] + 1.6 * (14 - gamestate.kings_distance)
                # Lone K vs K, N and B
                if gamestate.piece_dict[1]['R'] == gamestate.piece_dict[1]['Q'] == 0 and gamestate.piece_dict[1]['B'] >= 1 and gamestate.piece_dict[1]['N'] >= 1:
                    pass

    return white_score - black_score