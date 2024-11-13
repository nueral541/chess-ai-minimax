import pygame
import chess

from minimax import best_move
from CONSTANTS import *

# Define constants for players
WHITE = 1
BLACK = 0

# Global variables
dragging = False
dragged_piece = None
dragged_piece_rect = None
original_row = None
original_col = None
turn = WHITE

# opening, endgame, pawn structure, promotion  logic, castling logic, better eval, castling logic, print_game func; prints the whole game when it ends.-

# pygame setup
pygame.init()
pygame.mixer.init()
board = chess.Board()
screen = pygame.display.set_mode((sq * 8, sq * 8))
clock = pygame.time.Clock()
running = True

# Load sounds
move_sound = pygame.mixer.Sound("sounds/move-self.mp3")
capture_sound = pygame.mixer.Sound("sounds/capture.mp3")

# List to store hitbox rectangles
rects = []

def build_checkerboard(screen, sq):
    for row in range(8):
        for col in range(8):
            color = dark_green if (row + col) % 2 == 0 else light_green
            pygame.draw.rect(screen, color, pygame.Rect(col * sq, row * sq, sq, sq))

def draw_board(screen, bitboards):
    for piece_type, bitboard in bitboards.items():
        piece_image = piece_images[piece_type]
        for i in range(64):
            if bitboard & (1 << i):
                row = i // 8
                col = i % 8
                screen.blit(piece_image, (col * sq, row * sq))

def combine_bitboards(bitboards):
    combined = 0
    for bitboard in bitboards.values():
        combined |= bitboard
    return combined

def make_hitboxes(screen, bits):
    rects.clear()
    piece_loc = combine_bitboards(bits)
    for i in range(64):
        if piece_loc & (1 << i):
            row = i // 8
            col = i % 8
            # Create a transparent surface
            hitbox_surface = pygame.Surface((sq, sq), pygame.SRCALPHA)
            # Create a rect for the hitbox
            hitbox_rect = pygame.Rect(col * sq, row * sq, sq, sq)
            rects.append(hitbox_rect)

            # Fill the surface with a transparent color
            hitbox_surface.fill(transparent_black)
            # Blit the transparent surface onto the main screen
            screen.blit(hitbox_surface, (col * sq, row * sq))

def find_piece_by_rect(rect):
    for piece_type, bitboard in bitboards.items():
        for i in range(64):
            if bitboard & (1 << i):
                row = i // 8
                col = i % 8
                if rect.collidepoint(col * sq, row * sq):
                    return piece_type

def remove_old_piece(piece, row, col):
    # Calculate the old and new positions
    old_location = row * 8 + col

    # Remove the piece from the old location
    bitboards[piece] &= ~(1 << old_location)

def update_bitboard(piece, new_row, new_col):
    # Calculate the new position
    new_location = new_row * 8 + new_col

    # Update the bitboard
    bitboards[piece] |= (1 << new_location)

def handle_en_passant(row, col):
    pos = row*8+col
    if turn == WHITE:
        bitboards['bp'] ^= (1 << (pos + 8))
    else:
        bitboards['wp'] ^= (1 << (pos - 8))

def handle_castle(move):
    global bitboards
    if move.from_square == chess.E1:
        if move.to_square == chess.G1:
            bitboards['wr'] &= ~(1 << 63)
            bitboards['wr'] |= (1 << 61)
            bitboards['wk'] &= ~(1 << 60)
            bitboards['wk'] |= (1 << 62)
        elif move.to_square == chess.C1:
            bitboards['wr'] &= ~(1 << 56)
            bitboards['wr'] |= (1 << 59)
            bitboards['wk'] &= ~(1 << 60)
            bitboards['wk'] |= (1 << 58)
    elif move.from_square == chess.E8:
        if move.to_square == chess.G8:
            bitboards['br'] &= ~(1 << 7)
            bitboards['br'] |= (1 << 5)
            bitboards['bk'] &= ~(1 << 4)
            bitboards['bk'] |= (1 << 6)
        elif move.to_square == chess.C8:
            bitboards['br'] &= ~(1 << 0)
            bitboards['br'] |= (1 << 3)
            bitboards['bk'] &= ~(1 << 4)
            bitboards['bk'] |= (1 << 2)

def exterminate_position(row, col):
    pos = row * 8 + col
    for bit in bitboards:
        bitboards[bit] &= ~(1 << pos)

def handle_promotion(oldrow, oldcol, row, col):
    exterminate_position(row, col)
    exterminate_position(oldrow, oldcol)

    pos = row * 8 + col
    if turn == WHITE:
        bitboards['wq'] |= (1 << pos)
    else:
        bitboards['bq'] |= (1 << pos)

def update_board(piece, row, col, new_row, new_col):
    global turn
    move = chess.Move.from_uci(f"{chr(col + 97)}{8 - row}{chr(new_col + 97)}{8 - new_row}")
    if move in board.legal_moves:
        print(f"player move: {move}")
        if board.is_en_passant(move):
            handle_en_passant(new_row, new_col)
        elif board.is_castling(move):
            print('castle')
            handle_castle(move)
        handle_capture(piece, new_row, new_col)
        board.push(move)
        print(board)
        print("__________________")
        remove_old_piece(piece, row, col)
        update_bitboard(piece, new_row, new_col)
        turn = BLACK  # Change turn to BLACK after player's move
        clear_overlapping_pieces()
        return True  # Indicate that a valid move was made
    else:
        promotion_move = chess.Move.from_uci(f"{chr(col + 97)}{8 - row}{chr(new_col + 97)}{8 - new_row}q")
        if promotion_move in board.legal_moves:
            handle_capture(piece, new_row, new_col)
            board.push(promotion_move)
            print(board)
            print("__________________")
            handle_promotion(row, col, new_row, new_col)
            turn = BLACK  # Change turn to BLACK after player's move
            clear_overlapping_pieces()
            return True  # Indicate that a valid move was made
        else:
            # Return the piece to its original position
            update_bitboard(piece, row, col)
            return False  # Indicate that no valid move was made

    return False  # Indicate that no valid move was made

def handle_mouse():
    global dragging, dragged_piece, dragged_piece_rect, original_row, original_col
    if turn == WHITE:
        if dragged_piece is None:
            mouse_pos = pygame.mouse.get_pos()
            for rect in rects:
                if rect.collidepoint(mouse_pos):
                    row = rect.y // sq
                    col = rect.x // sq
                    piece = find_piece_by_rect(rect)
                    if (piece[0] == 'w' and turn == WHITE) or (piece[0] == 'b' and turn == BLACK):
                        dragging = True
                        dragged_piece_rect = rect
                        dragged_piece = piece
                        original_row = row
                        original_col = col
                        remove_old_piece(dragged_piece, row, col)
                        move_sound.play()

def handle_mouse_motion():
    global dragged_piece_rect
    if dragging and dragged_piece_rect:
        mouse_pos = pygame.mouse.get_pos()
        dragged_piece_rect.x = mouse_pos[0] - sq // 2
        dragged_piece_rect.y = mouse_pos[1] - sq // 2

def handle_end_game(board):
    global running
    if board.is_checkmate():
        if turn == WHITE:
            print("Black wins!")
        else:
            print("White wins!")
        print(board)
        pygame.time.wait(5000)
        running = False
    elif board.is_stalemate():
        print("Stalemate!")
        print(board)
        pygame.time.wait(5000)
        running = False
    elif board.is_insufficient_material():
        print("Insufficient material!")
        print(board)
        pygame.time.wait(5000)
        running = False
    elif board.is_seventyfive_moves():
        print("Seventy-five moves rule!")
        print(board)
        pygame.time.wait(5000)
        running = False
    elif board.is_fivefold_repetition():
        print("Fivefold repetition!")
        print(board)
        pygame.time.wait(5000)
        running = False

def clear_overlapping_pieces():
    global bitboards
    all_pieces = 0
    for piece, bitboard in bitboards.items():
        all_pieces |= bitboard

    for piece, bitboard in bitboards.items():
        bitboards[piece] &= all_pieces

def handle_black(board):
    global turn
    bestmove = best_move(board)
    if bestmove:
        print(f"Computer Move: {bestmove}")
        move = chess.Move.from_uci(bestmove)
        
        # Filter out non-queen promotion moves
        if move.promotion and move.promotion != chess.QUEEN:
            handle_black(board)
            return
        
        if move in board.legal_moves:
            piece = board.piece_at(move.from_square)
            if piece is None:
                return
            piece_type = piece.symbol()
            piece_type = 'w' + piece_type.lower() if piece_type.isupper() else 'b' + piece_type
            start_row = 7 - (move.from_square // 8)
            start_col = move.from_square % 8
            end_row = 7 - (move.to_square // 8)
            end_col = move.to_square % 8

            if board.is_en_passant(move):
                handle_en_passant(end_row, end_col)

            # Handle promotion
            if move.promotion:
                handle_promotion(start_row, start_col, end_row, end_col)
                board.push(move)
            elif board.is_castling(move):
                handle_castle(move)
                board.push(move)
                remove_old_piece(piece_type, start_row, start_col)
                update_bitboard(piece_type, start_row, start_col)
                handle_capture(piece_type, end_row, end_col)
                exterminate_position(start_row, start_col)
            else:
                board.push(move)
                remove_old_piece(piece_type, start_row, start_col)
                update_bitboard(piece_type, end_row, end_col)
                handle_capture(piece_type, end_row, end_col)

            print(board)
            print("_______________")

            # Clear overlapping pieces
            clear_overlapping_pieces()

            turn = WHITE
        else:
            print("Illegal move")
    else:
        print("No move found")

def mouse_up():
    global dragging, dragged_piece, dragged_piece_rect, original_row, original_col, turn
    if turn == WHITE:
        if dragging:
            mouse_pos = pygame.mouse.get_pos()
            new_col = mouse_pos[0] // sq
            new_row = mouse_pos[1] // sq
            if (new_row != original_row) or (new_col != original_col):
                dragged_piece_rect.x = new_col * sq
                dragged_piece_rect.y = new_row * sq
                valid_move = update_board(dragged_piece, original_row, original_col, new_row, new_col)

                # Immediately update the display to show the player's move
                build_checkerboard(screen, sq)
                draw_board(screen, bitboards)
                make_hitboxes(screen, bitboards)
                pygame.display.flip()  # Force the screen to update

                if valid_move and turn == BLACK:
                    pygame.time.wait(500)  # Add a short delay to allow visual confirmation
                    handle_black(board)
            else:
                # Place the piece back to its original position
                update_bitboard(dragged_piece, original_row, original_col)
                dragged_piece_rect.x = original_col * sq
                dragged_piece_rect.y = original_row * sq
            dragging = False
            dragged_piece = None
            dragged_piece_rect = None
            original_row = None
            original_col = None

def handle_capture(piece, row, col):
    piece_color = piece[0]
    opposite_color = 'b' if piece_color == 'w' else 'w'
    
    for piece_type, bitboard in bitboards.items():
        if piece_type[0] == opposite_color:
            for i in range(64):
                if bitboard & (1 << i):
                    if i // 8 == row and i % 8 == col:
                        capture_sound.play()
                        bitboards[piece_type] &= ~(1 << i)
                        return  # Exit after capturing a piece
    move_sound.play()

# Main game loop
while running:
    #check if game has ended
    handle_end_game(board)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            handle_mouse()
        elif event.type == pygame.MOUSEMOTION and dragging:
            handle_mouse_motion()
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_up()

    build_checkerboard(screen, sq)
    draw_board(screen, bitboards)
    make_hitboxes(screen, bitboards)

    # Draw the dragged piece at the current mouse position
    if dragging and dragged_piece:
        screen.blit(piece_images[dragged_piece], dragged_piece_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()