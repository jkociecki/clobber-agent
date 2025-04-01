from clobber import *
from min_max import *   
import pygame
import sys


SQUARE_SIZE = 80
MARGIN = 20
PIECE_RADIUS = 30
GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (0, 0, 139)

class ClobberGUI:
    def __init__(self, board_size=6):
        self.board_size = board_size
        self.game = Clobber(board_size, board_size)
        window_width = board_size * SQUARE_SIZE + 2 * MARGIN
        window_height = board_size * SQUARE_SIZE + 2 * MARGIN + 50
        self.window = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption("Clobber")
        self.selected_piece = None
        self.legal_moves = []
        self.game_over_displayed = False
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 24, bold=True)
        self.small_font = pygame.font.SysFont('Arial', 18)
        self.ai_enabled = True
        self.ai_plays_white = True
        self.ai = MinMax(self.game)
        self.ai.set_max_depth(3)
        self.ai_thinking = False
        
    def get_square_from_pos(self, pos):
        x, y = pos
        if (MARGIN <= x < MARGIN + self.board_size * SQUARE_SIZE and 
            MARGIN <= y < MARGIN + self.board_size * SQUARE_SIZE):
            col = (x - MARGIN) // SQUARE_SIZE
            row = (y - MARGIN) // SQUARE_SIZE
            return Position(col, row)
        return None
    
    def get_pos_from_square(self, position):
        x = MARGIN + position.x * SQUARE_SIZE + SQUARE_SIZE // 2
        y = MARGIN + position.y * SQUARE_SIZE + SQUARE_SIZE // 2
        return (x, y)
    
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
        if self.selected_piece:
            center = self.get_pos_from_square(self.selected_piece)
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            s.fill((255, 255, 0, 128))
            self.window.blit(s, (MARGIN + self.selected_piece.x * SQUARE_SIZE, 
                                MARGIN + self.selected_piece.y * SQUARE_SIZE))
        for move in self.legal_moves:
            center = self.get_pos_from_square(move.end)
            pygame.draw.circle(self.window, GREEN, center, 10)
        if self.ai_thinking:
            thinking_text = "AI is thinking..."
            thinking_render = self.small_font.render(thinking_text, True, BLACK)
            self.window.blit(thinking_render, (MARGIN + 400, MARGIN + self.board_size * SQUARE_SIZE + 15))
        if self.game.game_over:
            if not self.game_over_displayed:
                self.display_game_over()
                pygame.time.delay(2000)
                self.game_over_displayed = True
        pygame.display.update()
        
    def display_game_over(self):
        winner_text = "DRAW!"
        if self.game.winner == Piece.BLACK:
            winner_text = "BLACK wins!"
        elif self.game.winner == Piece.WHITE:
            winner_text = "WHITE wins!"
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
        
    def handle_click(self, pos):
        if self.game.game_over:
            dialog_width, dialog_height = 300, 150
            dialog_x = (self.window.get_width() - dialog_width) // 2
            dialog_y = (self.window.get_height() - dialog_height) // 2
            new_game_button = pygame.Rect(dialog_x + 50, dialog_y + 100, 200, 30)
            if new_game_button.collidepoint(pos):
                self.reset_game()
            return
        if (self.ai_enabled and 
            ((self.ai_plays_white and self.game.current_turn == Piece.WHITE) or
             (not self.ai_plays_white and self.game.current_turn == Piece.BLACK))):
            return
        square = self.get_square_from_pos(pos)
        if not square:
            return
        piece = self.game.get_piece(square)
        if not self.selected_piece:
            if piece == self.game.current_turn:
                self.selected_piece = square
                self.update_legal_moves()
        else:
            for move in self.legal_moves:
                if move.end.x == square.x and move.end.y == square.y:
                    self.game.make_move(move)
                    self.selected_piece = None
                    self.legal_moves = []
                    break
            else:
                if piece == self.game.current_turn:
                    self.selected_piece = square
                    self.update_legal_moves()
                else:
                    self.selected_piece = None
                    self.legal_moves = []
    
    def update_legal_moves(self):
        self.legal_moves = []
        if self.selected_piece:
            all_legal_moves = self.game.get_legal_moves()
            for move in all_legal_moves:
                if move.start.x == self.selected_piece.x and move.start.y == self.selected_piece.y:
                    self.legal_moves.append(move)
    
    def make_ai_move(self):
        if self.game.game_over:
            return False
        if (self.ai_enabled and 
            ((self.ai_plays_white and self.game.current_turn == Piece.WHITE) or
             (not self.ai_plays_white and self.game.current_turn == Piece.BLACK))):
            self.ai_thinking = True
            self.draw_board()
            self.ai.clobber_engine = self.game
            best_move = self.ai.get_best_move()
            self.ai_thinking = False
            if best_move:
                self.game.make_move(best_move)
                return True
        return False
    
    def reset_game(self):
        self.game = Clobber(self.board_size, self.board_size)
        self.selected_piece = None
        self.legal_moves = []
        self.game_over_displayed = False
        self.ai.clobber_engine = self.game
    
    def toggle_ai(self):
        self.ai_enabled = not self.ai_enabled
        
    def toggle_ai_side(self):
        self.ai_plays_white = not self.ai_plays_white
    
    def run(self):
        running = True
        clock = pygame.time.Clock()
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.handle_click(event.pos)
                elif event.type == KEYDOWN:
                    if event.key == K_r:
                        self.reset_game()
                    elif event.key == K_u and not self.game.game_over:
                        self.game.undo_move()
                        if self.ai_enabled:
                            self.game.undo_move()
                        self.selected_piece = None
                        self.legal_moves = []
                        self.game_over_displayed = False
                    elif event.key == K_a:
                        self.toggle_ai()
                    elif event.key == K_s:
                        self.toggle_ai_side()
                    elif event.key == K_ESCAPE:
                        running = False
            self.make_ai_move()
            self.draw_board()
            clock.tick(30)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game_ui = ClobberGUI(6)
    game_ui.run()
