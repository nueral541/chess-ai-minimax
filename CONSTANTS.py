import pygame

sq = 100

piece_values = {
    'p': 1,
    'n': 3,
    'b': 3.5,
    'r': 5,
    'q': 9,
    'k': 1000,
}

dark_green = (118, 150, 86)
light_green = (238, 238, 210)
transparent_black = (0, 0, 0, 0)
blue = (0, 0, 255, 100)
red = (255, 0, 0, 100)

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

pawn_table = [
    0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
    5,  5, 10, 25, 25, 10,  5,  5,
    0,  0,  0, 20, 20,  0,  0,  0,
    5, -5,-10,  0,  0,-10, -5,  5,
    5, 10, 10,-20,-20, 10, 10,  5,
    0,  0,  0,  0,  0,  0,  0,  0
]

knight_table = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50,
]

bishop_table = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20,
]

rook_table = [
    0,  0,  0,  0,  0,  0,  0,  0,
    5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    0,  0,  0,  5,  5,  0,  0,  0
]

queen_table = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
    -5,  0,  5,  5,  5,  5,  0, -5,
    0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20
]

king_table_middle = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
    20, 20,  0,  0,  0,  0, 20, 20,
    20, 30, 10,  0,  0, 10, 30, 20
]

king_table_endgame = [
    -50,-40,-30,-20,-20,-30,-40,-50,
    -30,-20,-10,  0,  0,-10,-20,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-30,  0,  0,  0,  0,-30,-30,
    -50,-30,-30,-30,-30,-30,-30,-50
]