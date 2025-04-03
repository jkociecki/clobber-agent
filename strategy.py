from clobber import *

class Strategy:
    def evaluate(self, node, state, player):
        raise NotImplementedError("Metoda evaluate musi być zaimplementowana przez podklasę")

class RandomStrategy(Strategy):
    def evaluate(self, node, state, player):
        player_pieces = 0
        opponent_pieces = 0
        
        for row in state.board:
            for piece in row:
                if piece == player:
                    player_pieces += 1
                elif piece != Piece.EMPTY:
                    opponent_pieces += 1
        
        return player_pieces - opponent_pieces

class AdaptiveStrategy(Strategy):
    def evaluate(self, node, state, player):
        player_pieces = 0
        opponent_pieces = 0
        player_mobility = 0
        opponent_mobility = 0
        
        opponent = Piece.WHITE if player == Piece.BLACK else Piece.BLACK
        
        for y in range(state.height):
            for x in range(state.width):
                pos = Position(x, y)
                piece = state.get_piece(pos)
                
                if piece == player:
                    player_pieces += 1
                    for adj_pos in state.get_adjacent_positions(pos):
                        if state.get_piece(adj_pos) == opponent:
                            player_mobility += 1
                
                elif piece == opponent:
                    opponent_pieces += 1
                    for adj_pos in state.get_adjacent_positions(pos):
                        if state.get_piece(adj_pos) == player:
                            opponent_mobility += 1
        
        if state.game_over:
            if state.winner == player:
                return 1000  
            elif state.winner == opponent:
                return -1000 
        
        piece_weight = 1
        mobility_weight = 2
        
        piece_score = player_pieces - opponent_pieces
        mobility_score = player_mobility - opponent_mobility
        
        return (piece_weight * piece_score) + (mobility_weight * mobility_score)

class StrategyContext:
    def __init__(self, strategy: Strategy):
        self.strategy = strategy
    
    def evaluate(self, node, state, player):
        return self.strategy.evaluate(node, state, player)