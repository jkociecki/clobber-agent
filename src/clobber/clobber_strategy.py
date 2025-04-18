from general.strategy import Strategy
from general.game import GameState
import copy


class NaiveStrategy(Strategy):
    def evaluate(self, game: GameState):
        game_copy = copy.deepcopy(game)
        current_player = game_copy.get_current_player()
        
        if game_copy.is_terminal():
            return float('-inf')
            
        my_moves = len(game_copy.get_legal_moves())
        
        game_copy.current_player = ~current_player
        opponent_moves = len(game_copy.get_legal_moves())
        
        board = game_copy.get_board()
        mobility_score = 0
        
        for y in range(game_copy.height):
            for x in range(game_copy.width):
                if board[y][x] == current_player:
                    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                    piece_mobility = 0
                    
                    for dx, dy in directions:
                        nx, ny = x + dx, y + dy
                        if (0 <= nx < game_copy.width and 0 <= ny < game_copy.height and 
                            board[ny][nx] == ~current_player):
                            piece_mobility += 1
                            
                    mobility_score += piece_mobility
        
        move_diff_weight = 2.0
        mobility_weight = 1.0
        
        score = (move_diff_weight * (my_moves - opponent_moves) +
                 mobility_weight * mobility_score)
                 
        return score