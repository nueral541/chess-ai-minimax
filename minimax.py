import chess
import math

# Define piece values
piece_values = {
    'p': 1,
    'n': 3,
    'b': 3,
    'r': 5,
    'q': 9,
    'k': 0  # King value is not used in material evaluation
}

def best_move(board):
    moves = list(board.legal_moves)  # Convert LegalMoveGenerator to a list
    print(moves)
    if not moves:
        return None
    bestmove = minimax(board, 5, -math.inf, math.inf, True, root=True)
    return bestmove.uci()

def eval(board):
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            return -math.inf  # Black wins
        else:
            return math.inf  # White wins
    elif board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves() or board.is_fivefold_repetition():
        return 0  # Draw

    total_value = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = piece_values[piece.symbol().lower()]
            if piece.color == chess.WHITE:
                total_value -= value
            else:
                total_value += value
    return total_value

def minimax(gamestate, depth, alpha, beta, maxplayer, root=True):
    if depth == 0 or gamestate.is_game_over():
        return eval(gamestate)
    
    if maxplayer:
        max_eval = -math.inf
        best_move = None
        for move in gamestate.legal_moves:
            gamestate.push(move)
            current_eval = minimax(gamestate, depth-1, alpha, beta, False, root=False)
            gamestate.pop()
            if current_eval > max_eval:
                max_eval = current_eval
                best_move = move
            alpha = max(alpha, current_eval)
            if beta <= alpha:
                break
        if root:  # Return the best move at the root level
            return best_move
        return max_eval
    
    else:
        min_eval = math.inf
        for move in gamestate.legal_moves:
            gamestate.push(move)
            current_eval = minimax(gamestate, depth-1, alpha, beta, True, root=False)
            gamestate.pop()
            min_eval = min(min_eval, current_eval)
            beta = min(beta, current_eval)
            if beta <= alpha:
                break
        return min_eval

# Example usage
if __name__ == "__main__":
    board = chess.Board()
    print("Best move:", best_move(board))