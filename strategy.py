import copy
import time
from pygame.locals import *
from clobber import Clobber, Piece, Position, Move
from abc import ABC, abstractmethod

class EvaluationStrategy(ABC):
    @abstractmethod
    def evaluate(self, node, game_state):
        """Metoda abstrakcyjna do oceny stanu gry"""
        pass

class MobilityStrategy(EvaluationStrategy):
    """Strategia oceniająca na podstawie mobilności (liczby możliwych ruchów)"""
    def evaluate(self, node, game_state):
        if game_state.game_over:
            current_player = game_state.current_turn
            return -1000 if current_player == Piece.WHITE else 1000
        
        original_turn = game_state.current_turn

        game_state.current_turn = Piece.WHITE
        white_moves = len(game_state.get_legal_moves())
        
        game_state.current_turn = Piece.BLACK
        black_moves = len(game_state.get_legal_moves())
        
        game_state.current_turn = original_turn

        return white_moves - black_moves

class PositionalStrategy(EvaluationStrategy):
    """Strategia oceniająca na podstawie pozycji pionków na planszy"""
    def evaluate(self, node, game_state):
        if game_state.game_over:
            current_player = game_state.current_turn
            return -1000 if current_player == Piece.WHITE else 1000
        
        board = game_state.board
        rows, cols = len(board), len(board[0])
        
        positional_values = []
        for r in range(rows):
            row_values = []
            for c in range(cols):
                center_r, center_c = rows / 2, cols / 2
                distance = abs(r - center_r) + abs(c - center_c)
                value = max(rows + cols - distance, 1)
                row_values.append(value)
            positional_values.append(row_values)
        
        white_score = 0
        black_score = 0
        
        for r in range(rows):
            for c in range(cols):
                piece = board[r][c]
                if piece == Piece.WHITE:
                    white_score += positional_values[r][c]
                elif piece == Piece.BLACK:
                    black_score += positional_values[r][c]
        
        return white_score - black_score

class ConnectivityStrategy(EvaluationStrategy):
    """Strategia oceniająca na podstawie połączeń między pionkami"""
    def evaluate(self, node, game_state):
        if game_state.game_over:
            current_player = game_state.current_turn
            return -1000 if current_player == Piece.WHITE else 1000
        
        board = game_state.board
        rows, cols = len(board), len(board[0])
        
        def count_neighbors(r, c, piece_type):
            count = 0
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)] 
            
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] == piece_type:
                    count += 1
            
            return count
        
        white_connectivity = 0
        black_connectivity = 0
        
        for r in range(rows):
            for c in range(cols):
                if board[r][c] == Piece.WHITE:
                    white_connectivity += count_neighbors(r, c, Piece.WHITE)
                elif board[r][c] == Piece.BLACK:
                    black_connectivity += count_neighbors(r, c, Piece.BLACK)
        
        white_connectivity //= 2
        black_connectivity //= 2
        
        return white_connectivity - black_connectivity

class CombinedStrategy(EvaluationStrategy):
    """Strategia łącząca różne podejścia z wagami"""
    def __init__(self, mobility_weight=1.0, positional_weight=1.0, connectivity_weight=1.0):
        self.mobility_strategy = MobilityStrategy()
        self.positional_strategy = PositionalStrategy()
        self.connectivity_strategy = ConnectivityStrategy()
        self.mobility_weight = mobility_weight
        self.positional_weight = positional_weight
        self.connectivity_weight = connectivity_weight
    
    def evaluate(self, node, game_state):
        if game_state.game_over:
            current_player = game_state.current_turn
            return -1000 if current_player == Piece.WHITE else 1000
        
        mobility_score = self.mobility_strategy.evaluate(node, game_state)
        positional_score = self.positional_strategy.evaluate(node, game_state)
        connectivity_score = self.connectivity_strategy.evaluate(node, game_state)
        
        combined_score = (
            self.mobility_weight * mobility_score +
            self.positional_weight * positional_score +
            self.connectivity_weight * connectivity_score
        )
        
        return combined_score

class AdaptiveStrategy(EvaluationStrategy):
    """Strategia adaptacyjna zmieniająca podejście w zależności od fazy gry"""
    def __init__(self):
        self.early_strategy = CombinedStrategy(mobility_weight=1.0, positional_weight=2.0, connectivity_weight=1.0)
        self.mid_strategy = CombinedStrategy(mobility_weight=1.5, positional_weight=1.0, connectivity_weight=1.5)
        self.late_strategy = CombinedStrategy(mobility_weight=2.0, positional_weight=0.5, connectivity_weight=1.0)
    
    def evaluate(self, node, game_state):
        if game_state.game_over:
            current_player = game_state.current_turn
            return -1000 if current_player == Piece.WHITE else 1000
        
        board = game_state.board
        rows, cols = len(board), len(board[0])
        total_pieces = sum(1 for r in range(rows) for c in range(cols) if board[r][c] != Piece.EMPTY)
        max_pieces = rows * cols
        
        game_phase = total_pieces / max_pieces if max_pieces > 0 else 0
        
        if game_phase > 0.7:  
            return self.early_strategy.evaluate(node, game_state)
        elif game_phase > 0.3:  
            return self.mid_strategy.evaluate(node, game_state)
        else:  
            return self.late_strategy.evaluate(node, game_state)

class StrategyContext:
    def __init__(self, strategy=None):
        self.strategy = strategy if strategy else MobilityStrategy()
    
    def set_strategy(self, strategy):
        self.strategy = strategy
    
    def evaluate(self, node, game_state):
        return self.strategy.evaluate(node, game_state)