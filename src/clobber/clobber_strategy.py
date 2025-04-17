from general.strategy import Strategy
from general.game import GameState
import copy


class NaiveStrategy(Strategy):
    def evaluate(self, game: GameState):
        # Wykonaj kopię stanu gry
        game_copy = copy.deepcopy(game)
        current_player = game_copy.get_current_player()
        
        # Sprawdź, czy to stan końcowy
        if game_copy.is_terminal():
            return float('-inf')  # Przegrywająca pozycja dla bieżącego gracza
            
        # Sprawdź ruchy dostępne dla obu graczy
        my_moves = len(game_copy.get_legal_moves())
        
        # Przełącz gracza i sprawdź jego ruchy
        game_copy.current_player = ~current_player 
        opponent_moves = len(game_copy.get_legal_moves())
        
        # Weź pod uwagę mobilność i kontrolę
        board = game_copy.get_board()
        mobility_score = 0
        
        # Ocena pozycji pionków - premiuj te, które mogą się poruszać
        for y in range(game_copy.height):
            for x in range(game_copy.width):
                if board[y][x] == current_player:
                    # Sprawdź, czy pionek ma ruchy (ocena mobilności)
                    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                    piece_mobility = 0
                    
                    for dx, dy in directions:
                        nx, ny = x + dx, y + dy
                        if (0 <= nx < game_copy.width and 0 <= ny < game_copy.height and 
                            board[ny][nx] == ~current_player):
                            piece_mobility += 1
                            
                    mobility_score += piece_mobility
        
        # Waga dla poszczególnych komponentów oceny (można eksperymentować)
        move_diff_weight = 2.0
        mobility_weight = 1.0
        
        # Finalna funkcja oceny
        score = (move_diff_weight * (my_moves - opponent_moves) + 
                 mobility_weight * mobility_score)
                 
        return score