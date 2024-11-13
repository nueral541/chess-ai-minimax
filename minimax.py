import chess
import math

from CONSTANTS import *

REPETITION_PENALTY = 10
total_value = 0

def best_move(board):
    moves = list(board.legal_moves)  # Convert LegalMoveGenerator to a list
    if not moves:
        return None
    position_history = {board.fen(): 1}
    bestmove = minimax(board, 4, -math.inf, math.inf, True, position_history, root=True)
    return bestmove.uci()

def eval(board, position_history):
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            return 1000  # Black wins
        else:
            return -1000  # White wins
    elif board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves() or board.is_fivefold_repetition():
        return 0  # Draw

    total_value = 0
    positional_bonus = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = piece_values[piece.symbol().lower()]
            if piece.color == chess.WHITE:
                total_value -= value
                positional_bonus -= get_positional_bonus(board, piece, square)
            else:
                total_value += value
                positional_bonus += get_positional_bonus(board, piece, square)

    # Apply penalty for repeated positions
    fen = board.fen()
    repetition_count = position_history.get(fen, 0)
    if repetition_count > 1:
        total_value -= REPETITION_PENALTY * (repetition_count - 1)

    total_value += positional_bonus / 100

    return total_value

def get_positional_bonus(board, piece, square):

    piece_type = piece.symbol().lower()
    if piece_type == 'p':
        return pawn_table[square]
    elif piece_type == 'n':
        return knight_table[square]
    elif piece_type == 'b':
        return bishop_table[square]
    elif piece_type == 'r':
        return rook_table[square]
    elif piece_type == 'q':
        return queen_table[square]
    elif piece_type == 'k':
        total_pieces = len(board.piece_map())
        if total_pieces <= 10:
            return king_table_endgame[square]
        else:
            return king_table_middle[square]
    else:
        return 0

def minimax(gamestate, depth, alpha, beta, maxplayer, position_history, root=True):
    if depth == 0 or gamestate.is_game_over():
        return eval(gamestate, position_history)
    
    if maxplayer:
        max_eval = -math.inf
        best_move = None
        for move in gamestate.legal_moves:
            gamestate.push(move)
            fen = gamestate.fen()
            position_history[fen] = position_history.get(fen, 0) + 1
            current_eval = minimax(gamestate, depth-1, alpha, beta, False, position_history, root=False)
            position_history[fen] -= 1
            gamestate.pop()
            
            # Prioritize checkmate with fewer moves
            if gamestate.is_checkmate():
                current_eval += depth  # Reward faster checkmate

            if current_eval > max_eval:
                max_eval = current_eval
                best_move = move
            alpha = max(alpha, current_eval)
            if beta <= alpha:
                break
        if root:
            return best_move
        return max_eval
    
    else:
        min_eval = math.inf
        for move in gamestate.legal_moves:
            gamestate.push(move)
            fen = gamestate.fen()
            position_history[fen] = position_history.get(fen, 0) + 1
            current_eval = minimax(gamestate, depth-1, alpha, beta, True, position_history, root=False)
            position_history[fen] -= 1
            gamestate.pop()

            # Prioritize checkmate with fewer moves
            if gamestate.is_checkmate():
                current_eval -= depth  # Penalize checkmate if delayed

            min_eval = min(min_eval, current_eval)
            beta = min(beta, current_eval)
            if beta <= alpha:
                break
        return min_eval


# Example usage
if __name__ == "__main__":
    board = chess.Board()
    print("Best move:", best_move(board))