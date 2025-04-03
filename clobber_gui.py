from clobber import *
from min_max import *
import pygame
import sys
from strategy import *
import time
import random

SQUARE_SIZE = 80
MARGIN = 20
PIECE_RADIUS = 30
GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (0, 0, 139)

class AIPlayer:
    def __init__(self, piece, strategy, max_depth=3, name=None):
        self.piece = piece
        self.strategy = strategy
        self.max_depth = max_depth
        self.name = name if name else f"AI {strategy.__class__.__name__}"
        
    def get_move(self, game):
        ai = MinMax(game, strategy_context=StrategyContext(self.strategy))
        ai.set_max_depth(self.max_depth)
        return ai.get_best_move()

class ClobberAIvsAI:
    def __init__(self, board_size=6):
        self.board_size = board_size
        self.game = Clobber(board_size, board_size)
        window_width = board_size * SQUARE_SIZE + 2 * MARGIN + 200
        window_height = board_size * SQUARE_SIZE + 2 * MARGIN + 100
        self.window = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption("Clobber AI vs AI")
        self.game_over_displayed = False
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 24, bold=True)
        self.small_font = pygame.font.SysFont('Arial', 18)
        self.available_strategies = [
            AdaptiveStrategy(),
            ConnectivityStrategy(),
            PositionalStrategy(),
        ]
        self.white_ai = AIPlayer(Piece.WHITE, self.available_strategies[0], max_depth=6, name="AI White")
        self.black_ai = AIPlayer(Piece.BLACK, self.available_strategies[1], max_depth=1, name="AI Black")
        self.ai_thinking = False
        self.move_delay = 1.0
        self.last_move_time = 0
        self.running = True
        self.auto_play = False
        self.stats = {
            "white_wins": 0,
            "black_wins": 0,
            "draws": 0,
            "total_games": 0
        }
        self.current_game_moves = 0
        
    def draw_board(self):
        self.window.fill(GRAY)
        for y in range(self.board_size):
            for x in range(self.board_size):
                rect = pygame.Rect(
                    MARGIN + x * SQUARE_SIZE,
                    MARGIN + y * SQUARE_SIZE,
                    SQUARE_SIZE,
                    SQUARE_SIZE
                )
                if (x + y) % 2 == 0:
                    color = LIGHT_BLUE
                else:
                    color = DARK_BLUE
                pygame.draw.rect(self.window, color, rect)
                pygame.draw.rect(self.window, BLACK, rect, 1)
        for y in range(self.board_size):
            for x in range(self.board_size):
                pos = Position(x, y)
                piece = self.game.get_piece(pos)
                if piece != Piece.EMPTY:
                    center = (
                        MARGIN + x * SQUARE_SIZE + SQUARE_SIZE // 2,
                        MARGIN + y * SQUARE_SIZE + SQUARE_SIZE // 2
                    )
                    if piece == Piece.WHITE:
                        pygame.draw.circle(self.window, WHITE, center, PIECE_RADIUS)
                    else:
                        pygame.draw.circle(self.window, BLACK, center, PIECE_RADIUS)
                    pygame.draw.circle(self.window, GRAY, center, PIECE_RADIUS, 2)
        board_width = self.board_size * SQUARE_SIZE + MARGIN
        y_pos = MARGIN
        turn_text = "Current Turn: "
        if self.game.current_turn == Piece.WHITE:
            turn_text += "WHITE"
            turn_color = WHITE
        else:
            turn_text += "BLACK"
            turn_color = BLACK
        turn_render = self.font.render(turn_text, True, BLACK)
        self.window.blit(turn_render, (board_width + 20, y_pos))
        pygame.draw.circle(self.window, turn_color, (board_width + 180, y_pos + 12), 12)
        y_pos += 40
        white_text = f"White: {self.white_ai.name}"
        white_render = self.small_font.render(white_text, True, BLACK)
        self.window.blit(white_render, (board_width + 20, y_pos))
        y_pos += 25
        black_text = f"Black: {self.black_ai.name}"
        black_render = self.small_font.render(black_text, True, BLACK)
        self.window.blit(black_render, (board_width + 20, y_pos))
        y_pos += 40
        moves_text = f"Moves: {self.current_game_moves}"
        moves_render = self.small_font.render(moves_text, True, BLACK)
        self.window.blit(moves_render, (board_width + 20, y_pos))
        y_pos += 40
        stats_text = f"Stats (W/B/D): {self.stats['white_wins']}/{self.stats['black_wins']}/{self.stats['draws']}"
        stats_render = self.small_font.render(stats_text, True, BLACK)
        self.window.blit(stats_render, (board_width + 20, y_pos))
        y_pos += 40
        controls_text = "Controls:"
        controls_render = self.small_font.render(controls_text, True, BLACK)
        self.window.blit(controls_render, (board_width + 20, y_pos))
        y_pos += 25
        controls = [
            "R - Reset game",
            "Space - Single move",
            "A - Auto play ON/OFF",
            "S - Switch strategies",
            "+ / - - Change delay",
            "Esc - Quit"
        ]
        for control in controls:
            control_render = self.small_font.render(control, True, BLACK)
            self.window.blit(control_render, (board_width + 20, y_pos))
            y_pos += 20
        auto_text = f"Auto Play: {'ON' if self.auto_play else 'OFF'}"
        auto_render = self.small_font.render(auto_text, True, GREEN if self.auto_play else BLACK)
        self.window.blit(auto_render, (board_width + 20, y_pos))
        y_pos += 25
        delay_text = f"Move Delay: {self.move_delay:.1f}s"
        delay_render = self.small_font.render(delay_text, True, BLACK)
        self.window.blit(delay_render, (board_width + 20, y_pos))
        if self.ai_thinking:
            thinking_text = "AI is thinking..."
            thinking_render = self.small_font.render(thinking_text, True, BLACK)
            self.window.blit(thinking_render, (MARGIN, MARGIN + self.board_size * SQUARE_SIZE + 15))
        if self.game.game_over and not self.game_over_displayed:
            self.display_game_over()
        pygame.display.update()
        
    def display_game_over(self):
        winner_text = "DRAW!"
        if self.game.winner == Piece.BLACK:
            winner_text = "BLACK wins!"
            self.stats["black_wins"] += 1
        elif self.game.winner == Piece.WHITE:
            winner_text = "WHITE wins!"
            self.stats["white_wins"] += 1
        else:
            self.stats["draws"] += 1
        self.stats["total_games"] += 1
        self.game_over_displayed = True
        if not self.auto_play:
            dialog_width, dialog_height = 300, 150
            dialog_x = (self.window.get_width() - dialog_width) // 2
            dialog_y = (self.window.get_height() - dialog_height) // 2
            dialog = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
            pygame.draw.rect(self.window, WHITE, dialog)
            pygame.draw.rect(self.window, BLACK, dialog, 3)
            game_over_text = self.font.render("GAME OVER", True, BLACK)
            self.window.blit(game_over_text, (dialog_x + dialog_width // 2 - game_over_text.get_width() // 2, 
                                           dialog_y + 20))
            winner_render = self.font.render(winner_text, True, BLACK)
            self.window.blit(winner_render, (dialog_x + dialog_width // 2 - winner_render.get_width() // 2, 
                                          dialog_y + 60))
            new_game_button = pygame.Rect(dialog_x + 50, dialog_y + 100, 200, 30)
            pygame.draw.rect(self.window, LIGHT_BLUE, new_game_button)
            pygame.draw.rect(self.window, BLACK, new_game_button, 2)
            new_game_text = self.small_font.render("New Game", True, BLACK)
            self.window.blit(new_game_text, (dialog_x + dialog_width // 2 - new_game_text.get_width() // 2, 
                                          dialog_y + 105))
            pygame.display.update()
            pygame.time.delay(2000)
        else:
            print(f"Game over: {winner_text} (Total games: {self.stats['total_games']})")
            pygame.time.delay(1000)
            self.reset_game()
    
    def make_ai_move(self):
        if self.game.game_over:
            return False
        current_time = time.time()
        if current_time - self.last_move_time < self.move_delay:
            return False
        self.ai_thinking = True
        self.draw_board()
        ai_player = self.white_ai if self.game.current_turn == Piece.WHITE else self.black_ai
        best_move = ai_player.get_move(self.game)
        self.ai_thinking = False
        if best_move:
            self.game.make_move(best_move)
            self.current_game_moves += 1
            self.last_move_time = time.time()
            return True
        return False
    
    def reset_game(self):
        self.game = Clobber(self.board_size, self.board_size)
        self.game_over_displayed = False
        self.current_game_moves = 0
    
    def switch_strategies(self):
        white_strategy_index = self.available_strategies.index(self.white_ai.strategy)
        black_strategy_index = self.available_strategies.index(self.black_ai.strategy)
        white_strategy_index = (white_strategy_index + 1) % len(self.available_strategies)
        black_strategy_index = (black_strategy_index + 1) % len(self.available_strategies)
        self.white_ai.strategy = self.available_strategies[white_strategy_index]
        self.white_ai.name = f"AI White ({self.white_ai.strategy.__class__.__name__})"
        self.black_ai.strategy = self.available_strategies[black_strategy_index]
        self.black_ai.name = f"AI Black ({self.black_ai.strategy.__class__.__name__})"
    
    def handle_click(self, pos):
        if self.game.game_over:
            dialog_width, dialog_height = 300, 150
            dialog_x = (self.window.get_width() - dialog_width) // 2
            dialog_y = (self.window.get_height() - dialog_height) // 2
            new_game_button = pygame.Rect(dialog_x + 50, dialog_y + 100, 200, 30)
            if new_game_button.collidepoint(pos):
                self.reset_game()
    
    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_a:
                        self.auto_play = not self.auto_play
                    elif event.key == pygame.K_s:
                        self.switch_strategies()
                    elif event.key == pygame.K_SPACE:
                        if not self.game.game_over:
                            self.make_ai_move()
                    elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
                        self.move_delay = min(5.0, self.move_delay + 0.1)
                    elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                        self.move_delay = max(0.1, self.move_delay - 0.1)
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
            if self.auto_play and not self.game.game_over:
                self.make_ai_move()
            self.draw_board()
            clock.tick(30)
        pygame.quit()
        sys.exit()
        # Rotate strategies
        white_strategy_index = self.available_strategies.index(self.white_ai.strategy)
        black_strategy_index = self.available_strategies.index(self.black_ai.strategy)
        
        white_strategy_index = (white_strategy_index + 1) % len(self.available_strategies)
        black_strategy_index = (black_strategy_index + 1) % len(self.available_strategies)
        
        self.white_ai.strategy = self.available_strategies[white_strategy_index]
        self.white_ai.name = f"AI White ({self.white_ai.strategy.__class__.__name__})"
        
        self.black_ai.strategy = self.available_strategies[black_strategy_index]
        self.black_ai.name = f"AI Black ({self.black_ai.strategy.__class__.__name__})"
    
    def handle_click(self, pos):
        if self.game.game_over:
            dialog_width, dialog_height = 300, 150
            dialog_x = (self.window.get_width() - dialog_width) // 2
            dialog_y = (self.window.get_height() - dialog_height) // 2
            new_game_button = pygame.Rect(dialog_x + 50, dialog_y + 100, 200, 30)
            if new_game_button.collidepoint(pos):
                self.reset_game()
    
    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left button
                        self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_a:
                        self.auto_play = not self.auto_play
                    elif event.key == pygame.K_s:
                        self.switch_strategies()
                    elif event.key == pygame.K_SPACE:
                        if not self.game.game_over:
                            self.make_ai_move()
                    elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
                        self.move_delay = min(5.0, self.move_delay + 0.1)
                    elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                        self.move_delay = max(0.1, self.move_delay - 0.1)
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
            
            if self.auto_play and not self.game.game_over:
                self.make_ai_move()
                
            self.draw_board()
            clock.tick(30)
        
        pygame.quit()
        sys.exit()

class StrategyTournament:
    def __init__(self, board_size=6, games_per_matchup=10):
        self.board_size = board_size
        self.games_per_matchup = games_per_matchup
        self.strategies = [
            AdaptiveStrategy(),
            PositionalStrategy(), 
            MobilityStrategy(),
            # Dodaj więcej strategii
        ]
        self.results = {}
        
    def run_tournament(self):
        print("Starting strategy tournament...")
        for i, strategy1 in enumerate(self.strategies):
            for j, strategy2 in enumerate(self.strategies):
                if i == j:  # Skip same strategy matches
                    continue
                    
                matchup = (strategy1.__class__.__name__, strategy2.__class__.__name__)
                self.results[matchup] = {"white_wins": 0, "black_wins": 0, "draws": 0}
                
                print(f"\nPlaying {matchup[0]} vs {matchup[1]} ({self.games_per_matchup} games)...")
                
                # Strategy1 as White, Strategy2 as Black
                for game_num in range(self.games_per_matchup):
                    game = Clobber(self.board_size, self.board_size)
                    white_ai = AIPlayer(Piece.WHITE, strategy1, max_depth=3)
                    black_ai = AIPlayer(Piece.BLACK, strategy2, max_depth=3)
                    
                    move_count = 0
                    while not game.game_over and move_count < 100:  # Prevent infinite games
                        if game.current_turn == Piece.WHITE:
                            move = white_ai.get_move(game)
                        else:
                            move = black_ai.get_move(game)
                            
                        if move:
                            game.make_move(move)
                            move_count += 1
                        else:
                            break
                    
                    if game.winner == Piece.WHITE:
                        self.results[matchup]["white_wins"] += 1
                    elif game.winner == Piece.BLACK:
                        self.results[matchup]["black_wins"] += 1
                    else:
                        self.results[matchup]["draws"] += 1
                        
                    print(f"Game {game_num+1}: {'WHITE' if game.winner == Piece.WHITE else 'BLACK' if game.winner == Piece.BLACK else 'DRAW'} in {move_count} moves")
                
        self.print_results()
                
    def print_results(self):
        print("\n===== TOURNAMENT RESULTS =====")
        print("Matchup".ljust(40) + " | " + "W/B/D")
        print("-" * 60)
        
        for matchup, stats in self.results.items():
            white_strat, black_strat = matchup
            results_str = f"{stats['white_wins']}/{stats['black_wins']}/{stats['draws']}"
            print(f"{white_strat} (W) vs {black_strat} (B)".ljust(40) + " | " + results_str)


def create_strategy_class(strategy_name):
    """Dynamiczna funkcja do tworzenia nowej strategii przez dziedziczenie"""
    class NewStrategy(Strategy):
        def __init__(self):
            super().__init__()
            self.name = strategy_name
            
        def evaluate(self, clobber_engine, perspective_piece):
            # Tu można dodać własną logikę oceny pozycji
            # Przykładowa implementacja:
            board_value = 0
            for y in range(clobber_engine.rows):
                for x in range(clobber_engine.cols):
                    pos = Position(x, y)
                    piece = clobber_engine.get_piece(pos)
                    if piece == perspective_piece:  # Własna figura
                        board_value += 1  # Wartość bazowa za figurę
                        # Dodatkowa wartość za mobilność (ile ruchów może wykonać)
                        moves = clobber_engine.get_piece_legal_moves(pos)
                        board_value += len(moves) * 0.5
            
            return board_value
    
    # Dynamicznie ustawiamy nazwę klasy
    NewStrategy.__name__ = strategy_name
    return NewStrategy


# Dodatkowa funkcja do tworzenia i uruchamiania eksperymentów
def run_strategy_experiment(experiment_name, num_games=100):
    print(f"Starting experiment: {experiment_name}")
    # Tu można uruchomić serię gier z wybranym zestawem parametrów
    # i zbierać statystyki
    
    # Przykład: porównanie różnych głębokości przeszukiwania dla tej samej strategii
    game = Clobber(6, 6)
    results = {}
    
    for depth1 in range(1, 5):
        for depth2 in range(1, 5):
            if depth1 == depth2:
                continue
                
            matchup = f"MinMax(depth={depth1}) vs MinMax(depth={depth2})"
            results[matchup] = {"white_wins": 0, "black_wins": 0, "draws": 0, "avg_moves": 0}
            total_moves = 0
            
            print(f"Playing {matchup}...")
            
            for game_num in range(num_games):
                game = Clobber(6, 6)
                white_ai = AIPlayer(Piece.WHITE, AdaptiveStrategy(), max_depth=depth1)
                black_ai = AIPlayer(Piece.BLACK, AdaptiveStrategy(), max_depth=depth2)
                
                move_count = 0
                while not game.game_over and move_count < 100:
                    if game.current_turn == Piece.WHITE:
                        move = white_ai.get_move(game)
                    else:
                        move = black_ai.get_move(game)
                        
                    if move:
                        game.make_move(move)
                        move_count += 1
                    else:
                        break
                
                if game.winner == Piece.WHITE:
                    results[matchup]["white_wins"] += 1
                elif game.winner == Piece.BLACK:
                    results[matchup]["black_wins"] += 1
                else:
                    results[matchup]["draws"] += 1
                    
                total_moves += move_count
                
            results[matchup]["avg_moves"] = total_moves / num_games
    
    # Wypisz wyniki
    print("\n===== EXPERIMENT RESULTS =====")
    print("Matchup".ljust(30) + " | " + "W/B/D".ljust(10) + " | " + "Avg Moves")
    print("-" * 60)
    
    for matchup, stats in results.items():
        results_str = f"{stats['white_wins']}/{stats['black_wins']}/{stats['draws']}"
        avg_moves = f"{stats['avg_moves']:.1f}"
        print(f"{matchup}".ljust(30) + " | " + results_str.ljust(10) + " | " + avg_moves)
    
    return results


if __name__ == "__main__":
    # Możesz wybrać jeden z trybów uruchomienia:
    
    # 1. Tryb interaktywny z wizualizacją
    game_ui = ClobberAIvsAI(6)
    game_ui.run()
    
    # 2. Turniej strategii (bez wizualizacji)
    # tournament = StrategyTournament(board_size=6, games_per_matchup=10)
    # tournament.run_tournament()
    
    # 3. Eksperyment z parametrami
    # run_strategy_experiment("Depth comparison", num_games=20)