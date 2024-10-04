def update_bitboard(piece, new_row, new_col):
    # Find the current position of the piece
    for i in range(64):
        if bitboards[piece] & (1 << i):
            current_row = i // 8
            current_col = i % 8
            break

    # Clear the original position
    bitboards[piece] &= ~(1 << (current_row * 8 + current_col))

    # Clear any piece that might be at the new position
    for piece_type, bitboard in bitboards.items():
        if bitboard & (1 << (new_row * 8 + new_col)):
            bitboards[piece_type] &= ~(1 << (new_row * 8 + new_col))

    # Set the new position
    bitboards[piece] |= 1 << (new_row * 8 + new_col)