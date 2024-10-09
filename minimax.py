import random
import chess

def best_move(board):
    moves = list(board.legal_moves)  # Convert LegalMoveGenerator to a list
    print(moves)
    if not moves:
        return None
    bestmove = random.choice(moves)
    return bestmove.uci()