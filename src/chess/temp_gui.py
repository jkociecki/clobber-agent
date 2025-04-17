import pygame
import sys
from typing import List, Tuple, Optional
from general.game import GameState
from general.move import Move
from general.enums import Piece
from chess_piece import ChessPiece
from chess_state import Chess

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE = 640
SQUARE_SIZE = WINDOW_SIZE // 8
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
HIGHLIGHT = (124, 252, 0, 128)  # Light green with some transparency
SELECTED = (255, 255, 0, 128)  # Yellow with some transparency

# Piece images dictionary
IMAGES = {}


def load_images():
    pieces = ['wp', 'wn', 'wb', 'wr', 'wq', 'wk', 'bp', 'bn', 'bb', 'br', 'bq', 'bk']
    for piece in pieces:

        IMAGES[piece] = pygame.transform.scale(
            pygame.image.load(f'images/{piece}.png'), (SQUARE_SIZE, SQUARE_SIZE))


def draw_board(screen):
    for row in range(8):
        for col in range(8):
            color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
            pygame.draw.rect(screen, color, pygame.Rect(
                col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def draw_pieces(screen, board):
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece != ChessPiece.EMPTY:
                piece_code = get_piece_code(piece)
                screen.blit(IMAGES[piece_code], pygame.Rect(
                    col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def get_piece_code(piece: ChessPiece) -> str:
    piece_dict = {
        ChessPiece.WHITE_PAWN: 'wp',
        ChessPiece.WHITE_KNIGHT: 'wn',
        ChessPiece.WHITE_BISHOP: 'wb',
        ChessPiece.WHITE_ROOK: 'wr',
        ChessPiece.WHITE_QUEEN: 'wq',
        ChessPiece.WHITE_KING: 'wk',
        ChessPiece.BLACK_PAWN: 'bp',
        ChessPiece.BLACK_KNIGHT: 'bn',
        ChessPiece.BLACK_BISHOP: 'bb',
        ChessPiece.BLACK_ROOK: 'br',
        ChessPiece.BLACK_QUEEN: 'bq',
        ChessPiece.BLACK_KING: 'bk'
    }
    return piece_dict.get(piece, '')


def highlight_squares(screen, selected_pos, legal_moves):
    if selected_pos:
        row, col = selected_pos
        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        s.fill(SELECTED)
        screen.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))

        # Highlight legal moves
        for move in legal_moves:
            if move.from_pos == selected_pos:
                dest_row, dest_col = move.to_pos
                s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                s.fill(HIGHLIGHT)
                screen.blit(s, (dest_col * SQUARE_SIZE, dest_row * SQUARE_SIZE))


def get_square_from_mouse(pos):
    x, y = pos
    col = x // SQUARE_SIZE
    row = y // SQUARE_SIZE
    if 0 <= row < 8 and 0 <= col < 8:
        return (row, col)
    return None


def handle_promotion(screen, chess_game, move, from_pos, to_pos):
    row, col = from_pos
    piece = chess_game.board[row][col]

    if (piece == ChessPiece.WHITE_PAWN and to_pos[0] == 0) or \
            (piece == ChessPiece.BLACK_PAWN and to_pos[0] == 7):

        promotion_options = ['Q', 'R', 'B', 'N']
        option_rects = []
        color = WHITE if piece.color == Piece.WHITE else BLACK

        pygame.draw.rect(screen, (200, 200, 200), (WINDOW_SIZE // 4, WINDOW_SIZE // 3,
                                                   WINDOW_SIZE // 2, WINDOW_SIZE // 3))
        font = pygame.font.SysFont('Arial', 24)
        text = font.render("Choose promotion piece:", True, BLACK)
        screen.blit(text, (WINDOW_SIZE // 4 + 10, WINDOW_SIZE // 3 + 10))

        for i, option in enumerate(promotion_options):
            option_rect = pygame.Rect(WINDOW_SIZE // 4 + (i * (WINDOW_SIZE // 8)),
                                      WINDOW_SIZE // 3 + 50,
                                      WINDOW_SIZE // 8,
                                      WINDOW_SIZE // 8)
            option_rects.append(option_rect)
            pygame.draw.rect(screen, LIGHT_SQUARE, option_rect)

            if option == 'Q':
                piece_code = 'wq' if piece.color == Piece.WHITE else 'bq'
            elif option == 'R':
                piece_code = 'wr' if piece.color == Piece.WHITE else 'br'
            elif option == 'B':
                piece_code = 'wb' if piece.color == Piece.WHITE else 'bb'
            elif option == 'N':
                piece_code = 'wn' if piece.color == Piece.WHITE else 'bn'

            screen.blit(IMAGES[piece_code], option_rect)

        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    for i, rect in enumerate(option_rects):
                        if rect.collidepoint(mouse_pos):
                            return Move(from_pos, to_pos, promotion_options[i])

            pygame.time.Clock().tick(FPS)

    return move


def main():

    chess_game = Chess()

    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption('Chess')
    clock = pygame.time.Clock()

    load_images()

    selected_pos = None
    legal_moves = chess_game.get_legal_moves()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                square = get_square_from_mouse(pos)

                if square:
                    row, col = square
                    piece = chess_game.board[row][col]

                    if selected_pos is None:
                        if piece != ChessPiece.EMPTY and piece.color == chess_game.current_player:
                            selected_pos = square

                    else:
                        from_row, from_col = selected_pos
                        move = next((m for m in legal_moves if m.from_pos == selected_pos and m.to_pos == square), None)

                        if move:
                            if chess_game.board[from_row][from_col] in [ChessPiece.WHITE_PAWN,
                                                                        ChessPiece.BLACK_PAWN] and \
                                    ((chess_game.board[from_row][from_col] == ChessPiece.WHITE_PAWN and square[
                                        0] == 0) or \
                                     (chess_game.board[from_row][from_col] == ChessPiece.BLACK_PAWN and square[
                                         0] == 7)):
                                move = handle_promotion(screen, chess_game, move, selected_pos, square)

                            chess_game.make_move(move)
                            legal_moves = chess_game.get_legal_moves()
                            selected_pos = None

                            if chess_game.is_terminal():
                                print("Game Over!")
                                if not legal_moves:
                                    opponent = Piece.BLACK if chess_game.current_player == Piece.WHITE else Piece.WHITE
                                    king_pos = None
                                    for r in range(8):
                                        for c in range(8):
                                            if chess_game.board[r][c] in [ChessPiece.WHITE_KING,
                                                                          ChessPiece.BLACK_KING] and \
                                                    chess_game.board[r][c].color == chess_game.current_player:
                                                king_pos = (r, c)
                                                break
                                        if king_pos:
                                            break

                                    if king_pos and chess_game._is_square_attacked(king_pos[0], king_pos[1], opponent):
                                        print("Checkmate! {} wins.".format(
                                            "White" if opponent == Piece.WHITE else "Black"))
                                    else:
                                        print("Stalemate! Draw.")
                                else:
                                    print("Draw due to insufficient material or 50-move rule.")

                        elif piece != ChessPiece.EMPTY and piece.color == chess_game.current_player:
                            selected_pos = square
                        else:
                            selected_pos = None

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    chess_game = Chess()
                    selected_pos = None
                    legal_moves = chess_game.get_legal_moves()

        draw_board(screen)
        highlight_squares(screen, selected_pos, legal_moves)
        draw_pieces(screen, chess_game.board)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()