import pygame
import chess

# Define constants for players
WHITE = 1
BLACK = 0

dark_green = (118, 150, 86)
light_green = (238, 238, 210)
transparent_black = (0, 0, 0, 0)
blue = (0, 0, 255, 100)
red = (255, 0, 0, 100)

# Global variables
dragging = False
dragged_piece = None
dragged_piece_rect = None
original_row = None
original_col = None
sq = 100
turn = WHITE

piece_images = {
    'bb': pygame.transform.scale(pygame.image.load("/Users/pista/Desktop/GitHub/illegal-chess/pieces_img/black-bishop.png"), (sq, sq)),
    'bk': pygame.transform.scale(pygame.image.load("/Users/pista/Desktop/GitHub/illegal-chess/pieces_img/black-king.png"), (sq, sq)),
    'bn': pygame.transform.scale(pygame.image.load("/Users/pista/Desktop/GitHub/illegal-chess/pieces_img/black-knight.png"), (sq, sq)),
    'bp': pygame.transform.scale(pygame.image.load("/Users/pista/Desktop/GitHub/illegal-chess/pieces_img/black-pawn.png"), (sq, sq)),
    'bq': pygame.transform.scale(pygame.image.load("/Users/pista/Desktop/GitHub/illegal-chess/pieces_img/black-queen.png"), (sq, sq)),
    'br': pygame.transform.scale(pygame.image.load("/Users/pista/Desktop/GitHub/illegal-chess/pieces_img/black-rook.png"), (sq, sq)),
    'wb': pygame.transform.scale(pygame.image.load("/Users/pista/Desktop/GitHub/illegal-chess/pieces_img/white-bishop.png"), (sq, sq)),
    'wk': pygame.transform.scale(pygame.image.load("/Users/pista/Desktop/GitHub/illegal-chess/pieces_img/white-king.png"), (sq, sq)),
    'wn': pygame.transform.scale(pygame.image.load("/Users/pista/Desktop/GitHub/illegal-chess/pieces_img/white-knight.png"), (sq, sq)),
    'wp': pygame.transform.scale(pygame.image.load("/Users/pista/Desktop/GitHub/illegal-chess/pieces_img/white-pawn.png"), (sq, sq)),
    'wq': pygame.transform.scale(pygame.image.load("/Users/pista/Desktop/GitHub/illegal-chess/pieces_img/white-queen.png"), (sq, sq)),
    'wr': pygame.transform.scale(pygame.image.load("/Users/pista/Desktop/GitHub/illegal-chess/pieces_img/white-rook.png"), (sq, sq)),
}

bitboards = {
    'wp': 0b0000000011111111000000000000000000000000000000000000000000000000,
    'bp': 0b0000000000000000000000000000000000000000000000001111111100000000,
    'wr': 0b1000000100000000000000000000000000000000000000000000000000000000,
    'br': 0b0000000000000000000000000000000000000000000000000000000010000001,
    'wn': 0b0100001000000000000000000000000000000000000000000000000000000000,
    'bn': 0b0000000000000000000000000000000000000000000000000000000001000010,
    'wb': 0b0010010000000000000000000000000000000000000000000000000000000000,
    'bb': 0b0000000000000000000000000000000000000000000000000000000000100100,
    'wq': 0b0000100000000000000000000000000000000000000000000000000000000000,
    'bq': 0b0000000000000000000000000000000000000000000000000000000000001000,
    'wk': 0b0001000000000000000000000000000000000000000000000000000000000000,
    'bk': 0b0000000000000000000000000000000000000000000000000000000000010000,
}

# pygame setup
pygame.init()
pygame.mixer.init()
board = chess.Board()
screen = pygame.display.set_mode((sq * 8, sq * 8))
clock = pygame.time.Clock()
running = True

from minimax import best_move

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
        if move.to_square == 2:
            # Move the white rook
            bitboards['wr'] &= ~(1 << 56) #0
            bitboards['wr'] |= (1 << 59) #3
        elif move.to_square == 6:
            # Move the white rook
            bitboards['wr'] &= ~(1 << 63) #7
            bitboards['wr'] |= (1 << 61) #5
        elif move.to_square == 58:
            # Move the black rook
            bitboards['br'] &= ~(1 << 0) 
            bitboards['br'] |= (1 << 3)
        elif move.to_square == 62:
            # Move the black rook
            bitboards['br'] &= ~(1 << 7)
            bitboards['br'] |= (1 << 5)

def handle_promotion(row, col):
    pos = row * 8 + col
    if turn == WHITE:
        bitboards['wp'] ^= (1 << pos)
        bitboards['wq'] |= (1 << pos)
    else:
        bitboards['bp'] ^= (1 << pos)
        bitboards['bq'] |= (1 << pos)

    print(board)

def update_board(piece, row, col, new_row, new_col):
    global turn
    move = chess.Move.from_uci(f"{chr(col + 97)}{8 - row}{chr(new_col + 97)}{8 - new_row}")
    if move in board.legal_moves:
        if board.is_en_passant(move):
            handle_en_passant(new_row, new_col)
        elif board.is_castling(move):
            handle_castle(move)
        handle_capture(dragged_piece, new_row, new_col)
        board.push(move)
        print(board)
        update_bitboard(piece, new_row, new_col)
        turn = WHITE if turn == BLACK else BLACK
        print("Turn is BLACK, calling handle_black")
        handle_black(board)
    else:
        promotion_move = chess.Move.from_uci(f"{chr(col + 97)}{8 - row}{chr(new_col + 97)}{8 - new_row}q")
        if promotion_move in board.legal_moves:
            handle_capture(dragged_piece, new_row, new_col)
            update_bitboard(piece, new_row, new_col)
            turn = WHITE if turn == BLACK else BLACK
            if turn == WHITE:
                board.push(promotion_move)
            else:
                board.push(promotion_move)
                handle_black(board)
            handle_promotion(new_row, new_col)
        else:
            # Return the piece to its original position
            update_bitboard(piece, row, col)
            dragged_piece_rect.x = col * sq
            dragged_piece_rect.y = row * sq
        if turn == BLACK:
            print("Turn is BLACK, illegal move")

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
        pygame.time.wait(5000)
        running = False
    elif board.is_stalemate():
        print("Stalemate!")
        pygame.time.wait(5000)
        running = False
    elif board.is_insufficient_material():
        print("Insufficient material!")
        pygame.time.wait(5000)
        running = False
    elif board.is_seventyfive_moves():
        print("Seventy-five moves rule!")
        pygame.time.wait(5000)
        running = False
    elif board.is_fivefold_repetition():
        print("Fivefold repetition!")
        pygame.time.wait(5000)
        running = False

def handle_black(board):
    global turn
    print("Inside handle_black")
    bestmove = best_move(board)
    if bestmove:
        print(f"Best move found: {bestmove}")
        move = chess.Move.from_uci(bestmove)
        
        # Filter out non-queen promotion moves
        if move.promotion and move.promotion != chess.QUEEN:
            print(f"Skipping non-queen promotion move: {move}")
            return
        
        if move in board.legal_moves:
            piece = board.piece_at(move.from_square)
            if piece is None:
                print(f"No piece found at {move.from_square}")
                return
            piece_type = piece.symbol()
            print(piece_type)
            piece_type = 'w' + piece_type.lower() if piece_type.isupper() else 'b' + piece_type
            print(piece_type)
            start_row = 7 - (move.from_square // 8)
            start_col = move.from_square % 8
            end_row = 7 - (move.to_square // 8)
            end_col = move.to_square % 8
            print(f"Moving piece {piece_type} from ({start_row}, {start_col}) to ({end_row}, {end_col})")

            # Handle en passant
            if board.is_en_passant(move):
                print("En passant move detected")
                handle_en_passant(piece_type, start_row, start_col, end_row, end_col)

            # Handle promotion
            if move.promotion:
                print("Promotion move detected")
                handle_promotion(end_row, end_col)
                remove_old_piece(piece_type, start_row, start_col)
                remove_old_piece(piece_type, end_row, end_col)
                board.push(move)
            else:
                board.push(move)
                remove_old_piece(piece_type, start_row, start_col)
                update_bitboard(piece_type, end_row, end_col)
                handle_capture(piece_type, end_row, end_col)

            # Handle castling
            if board.is_castling(move):
                print("Castling move detected")
                handle_castle(piece_type, start_row, start_col, end_row, end_col)

            turn = WHITE
            print(f"Turn after black move: {turn}")
        else:
            print("Illegal move")
    else:
        print("No move found")

def mouse_up():
    global dragging, dragged_piece, dragged_piece_rect, original_row, original_col, turn
    print("hello")
    if turn == WHITE:
        if dragging:
            mouse_pos = pygame.mouse.get_pos()
            new_col = mouse_pos[0] // sq
            new_row = mouse_pos[1] // sq
            if (new_row != original_row) or (new_col != original_col):
                dragged_piece_rect.x = new_col * sq
                dragged_piece_rect.y = new_row * sq
                update_board(dragged_piece, original_row, original_col, new_row, new_col)
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
            print(f"Turn after white move: {turn}")
            if turn == BLACK:
                print("Turn is BLACK, calling handle_black")
                handle_black(board)

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

'''def highlight_bitboard(screen, bitboard):
    for i in range(64):
        row = i // 8
        col = i % 8
        color = blue if not (bitboard & (1 << i)) else red
        highlight_surface = pygame.Surface((sq, sq), pygame.SRCALPHA)
        highlight_surface.fill(color)
        screen.blit(highlight_surface, (col * sq, row * sq))'''

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