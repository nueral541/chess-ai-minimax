def handle_en_passant(move):
    global bitboards
    if board.turn == chess.WHITE:
        captured_pawn_square = move.to_square + 8
        bitboards['bp'] &= ~(1 << captured_pawn_square)
    else:
        captured_pawn_square = move.to_square - 8
        bitboards['wp'] &= ~(1 << captured_pawn_square)