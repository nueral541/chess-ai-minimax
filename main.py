import pygame

# Define constants for players
WHITE = 1
BLACK = 0

dark_green = (118, 150, 86)
light_green = (238, 238, 210)
transparent_black = (0, 0, 0, 0)

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

def handle_mouse():
    global dragging, dragged_piece, dragged_piece_rect, original_row, original_col
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
                    print(find_legal_moves(dragged_piece, row, col))  # Move this inside the condition

def handle_mouse_motion():
    global dragged_piece_rect
    if dragging and dragged_piece_rect:
        mouse_pos = pygame.mouse.get_pos()
        dragged_piece_rect.x = mouse_pos[0] - sq // 2
        dragged_piece_rect.y = mouse_pos[1] - sq // 2

def mouse_up():
    global dragging, dragged_piece, dragged_piece_rect, original_row, original_col, turn
    if dragging:
        mouse_pos = pygame.mouse.get_pos()
        new_col = mouse_pos[0] // sq
        new_row = mouse_pos[1] // sq
        handle_capture(dragged_piece, new_row, new_col)
        dragged_piece_rect.x = new_col * sq
        dragged_piece_rect.y = new_row * sq
        update_bitboard(dragged_piece, new_row, new_col)
        dragging = False
        if (new_row != original_row) or (new_col != original_col):
            turn = WHITE if turn == BLACK else BLACK
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

# This is going to be the heart of the chess bot
def find_legal_moves(piece, row, col):
    legal_moves = []

# Main game loop
while running:
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