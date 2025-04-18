from general.enums import Piece
from general.strategy import Strategy
from general.game import GameState
from chess.chess_piece import ChessPiece
from chess.chess_state import Chess
from chess.constants import *
import copy
import random


class NaiveChessStrategy(Strategy):

    def evaluate(self, game: GameState):
        game_copy = copy.deepcopy(game)
        current_player = game_copy.get_current_player()
        board = game_copy.get_board()

        return random.uniform(-1, 1)


class AdaptiveChessStrategy(Strategy):


    def __init__(self):
        self.game_phase = 'opening'

    def evaluate(self, game: Chess) -> float:

        state = game.get_game_state()
        if state == 'checkmate':
            return float('-inf') if game.current_player == Piece.WHITE else float('inf')
        elif state == 'stalemate':
            return 0

        self._update_game_phase(game)

        material_score = self.calculate_material_score(game)

        positional_score = self.calculate_positional_score(game)

        mobility_score = self.calculate_mobility(game)

        king_safety_score = self.calculate_king_safety(game)

        pawn_structure_score = self.calculate_pawn_structure(game)

        development_score = 0
        if self.game_phase == 'opening':
            development_score = self.calculate_development(game)

        center_control_score = self.calculate_center_control(game)

        total_score = (
                material_score +
                positional_score +
                mobility_score * 0.1 +
                king_safety_score +
                pawn_structure_score +
                development_score +
                center_control_score
        )

        return total_score if game.current_player == Piece.WHITE else -total_score

    def calculate_material_score(self, game: GameState) -> float:
        material_score = 0
        board = game.get_board()

        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece in self.piece_values:
                    material_score += self.piece_values[piece]

        return material_score

    def calculate_positional_score(self, game: GameState) -> float:
        score = 0
        board = game.get_board()

        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece == ChessPiece.EMPTY:
                    continue

                if piece == ChessPiece.WHITE_PAWN:
                    score += self.pawn_table[row][col]
                elif piece == ChessPiece.BLACK_PAWN:
                    score -= self.pawn_table[7 - row][col]  
                elif piece == ChessPiece.WHITE_KNIGHT:
                    score += self.knight_table[row][col]
                elif piece == ChessPiece.BLACK_KNIGHT:
                    score -= self.knight_table[7 - row][col]
                elif piece == ChessPiece.WHITE_BISHOP:
                    score += self.bishop_table[row][col]
                elif piece == ChessPiece.BLACK_BISHOP:
                    score -= self.bishop_table[7 - row][col]
                elif piece == ChessPiece.WHITE_ROOK:
                    score += self.rook_table[row][col]
                elif piece == ChessPiece.BLACK_ROOK:
                    score -= self.rook_table[7 - row][col]
                elif piece == ChessPiece.WHITE_QUEEN:
                    score += self.queen_table[row][col]
                elif piece == ChessPiece.BLACK_QUEEN:
                    score -= self.queen_table[7 - row][col]
                elif piece == ChessPiece.WHITE_KING:
                    if self.game_phase == 'endgame':
                        score += self.king_endgame_table[row][col]
                    else:
                        score += self.king_middle_table[row][col]
                elif piece == ChessPiece.BLACK_KING:
                    if self.game_phase == 'endgame':
                        score -= self.king_endgame_table[7 - row][col]
                    else:
                        score -= self.king_middle_table[7 - row][col]

        return score

    def calculate_mobility(self, game: GameState) -> float:
        current_player = game.current_player

        game.current_player = Piece.WHITE
        white_mobility = len(game.get_legal_moves())

        game.current_player = Piece.BLACK
        black_mobility = len(game.get_legal_moves())

        game.current_player = current_player

        return white_mobility - black_mobility

    def calculate_king_safety(self, game: GameState) -> float:
        score = 0
        board = game.get_board()

        white_king_pos = None
        black_king_pos = None

        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece == ChessPiece.WHITE_KING:
                    white_king_pos = (row, col)
                elif piece == ChessPiece.BLACK_KING:
                    black_king_pos = (row, col)

        if white_king_pos and self.game_phase != 'endgame':
            w_row, w_col = white_king_pos
            if w_col >= 5: 
                for c in range(max(w_col - 1, 0), min(w_col + 2, 8)):
                    if w_row > 0 and board[w_row - 1][c] == ChessPiece.WHITE_PAWN:
                        score += 10 
            elif w_col <= 3:  
                for c in range(max(w_col - 1, 0), min(w_col + 2, 8)):
                    if w_row > 0 and board[w_row - 1][c] == ChessPiece.WHITE_PAWN:
                        score += 10

            for r in range(max(w_row - 2, 0), min(w_row + 3, 8)):
                for c in range(max(w_col - 2, 0), min(w_col + 3, 8)):
                    piece = board[r][c]
                    if piece in [ChessPiece.BLACK_QUEEN, ChessPiece.BLACK_ROOK, ChessPiece.BLACK_BISHOP,
                                 ChessPiece.BLACK_KNIGHT]:
                        score -= 15

        if black_king_pos and self.game_phase != 'endgame':
            b_row, b_col = black_king_pos
            if b_col >= 5:  
                for c in range(max(b_col - 1, 0), min(b_col + 2, 8)):
                    if b_row < 7 and board[b_row + 1][c] == ChessPiece.BLACK_PAWN:
                        score -= 10  
            elif b_col <= 3:  
                for c in range(max(b_col - 1, 0), min(b_col + 2, 8)):
                    if b_row < 7 and board[b_row + 1][c] == ChessPiece.BLACK_PAWN:
                        score -= 10

            for r in range(max(b_row - 2, 0), min(b_row + 3, 8)):
                for c in range(max(b_col - 2, 0), min(b_col + 3, 8)):
                    piece = board[r][c]
                    if piece in [ChessPiece.WHITE_QUEEN, ChessPiece.WHITE_ROOK, ChessPiece.WHITE_BISHOP,
                                 ChessPiece.WHITE_KNIGHT]:
                        score += 15  

        return score

    def calculate_pawn_structure(self, game: GameState) -> float:
        score = 0
        board = game.get_board()

        white_pawn_files = [0] * 8
        black_pawn_files = [0] * 8

        for col in range(8):
            for row in range(8):
                if board[row][col] == ChessPiece.WHITE_PAWN:
                    white_pawn_files[col] += 1
                elif board[row][col] == ChessPiece.BLACK_PAWN:
                    black_pawn_files[col] += 1

        for col in range(8):
            if white_pawn_files[col] > 1:
                score -= 10 * (white_pawn_files[col] - 1)
            if black_pawn_files[col] > 1:
                score += 10 * (black_pawn_files[col] - 1)

        for col in range(8):
            if white_pawn_files[col] > 0:
                isolated = True
                if (col > 0 and white_pawn_files[col - 1] > 0) or (col < 7 and white_pawn_files[col + 1] > 0):
                    isolated = False
                if isolated:
                    score -= 15

            if black_pawn_files[col] > 0:
                isolated = True
                if (col > 0 and black_pawn_files[col - 1] > 0) or (col < 7 and black_pawn_files[col + 1] > 0):
                    isolated = False
                if isolated:
                    score += 15

        for col in range(8):
            white_most_advanced = -1
            for row in range(7, -1, -1):
                if board[row][col] == ChessPiece.WHITE_PAWN:
                    white_most_advanced = row
                    break

            if white_most_advanced != -1:
                is_passed = True
                for check_col in range(max(0, col - 1), min(8, col + 2)):
                    for row in range(white_most_advanced - 1, -1, -1):
                        if board[row][check_col] == ChessPiece.BLACK_PAWN:
                            is_passed = False
                            break
                if is_passed:
                    score += 20 + (7 - white_most_advanced) * 10

            black_most_advanced = -1
            for row in range(8):
                if board[row][col] == ChessPiece.BLACK_PAWN:
                    black_most_advanced = row
                    break

            if black_most_advanced != -1:
                is_passed = True
                for check_col in range(max(0, col - 1), min(8, col + 2)):
                    for row in range(black_most_advanced + 1, 8):
                        if board[row][check_col] == ChessPiece.WHITE_PAWN:
                            is_passed = False
                            break
                if is_passed:
                    score -= 20 + black_most_advanced * 10

        return score

    def calculate_development(self, game: GameState) -> float:
        score = 0
        board = game.get_board()

        if board[7][1] != ChessPiece.WHITE_KNIGHT:
            score += 10  
        if board[7][6] != ChessPiece.WHITE_KNIGHT:
            score += 10
        if board[7][2] != ChessPiece.WHITE_BISHOP:
            score += 10
        if board[7][5] != ChessPiece.WHITE_BISHOP:
            score += 10

        if board[0][1] != ChessPiece.BLACK_KNIGHT:
            score -= 10
        if board[0][6] != ChessPiece.BLACK_KNIGHT:
            score -= 10
        if board[0][2] != ChessPiece.BLACK_BISHOP:
            score -= 10
        if board[0][5] != ChessPiece.BLACK_BISHOP:
            score -= 10

        for row in range(6):
            for col in range(8):
                if board[row][col] == ChessPiece.WHITE_QUEEN:
                    score -= 20
                if board[row + 2][col] == ChessPiece.BLACK_QUEEN:
                    score += 20

        if game.white_castle_king_side is False and board[7][6] == ChessPiece.WHITE_KING:
            score += 30
        if game.black_castle_king_side is False and board[0][6] == ChessPiece.BLACK_KING:
            score -= 30

        if game.white_castle_queen_side is False and board[7][2] == ChessPiece.WHITE_KING:
            score += 25 
        if game.black_castle_queen_side is False and board[0][2] == ChessPiece.BLACK_KING:
            score -= 25

        return score

    def calculate_center_control(self, game: GameState) -> float:
        score = 0
        board = game.get_board()

        center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
        extended_center = [(2, 2), (2, 3), (2, 4), (2, 5),
                           (3, 2), (3, 5), (4, 2), (4, 5),
                           (5, 2), (5, 3), (5, 4), (5, 5)]

        for row, col in center_squares:
            piece = board[row][col]
            if piece == ChessPiece.WHITE_PAWN:
                score += 20
            elif piece == ChessPiece.BLACK_PAWN:
                score -= 20
            elif piece in [ChessPiece.WHITE_KNIGHT, ChessPiece.WHITE_BISHOP]:
                score += 15
            elif piece in [ChessPiece.BLACK_KNIGHT, ChessPiece.BLACK_BISHOP]:
                score -= 15

        for row, col in extended_center:
            piece = board[row][col]
            if piece == ChessPiece.WHITE_PAWN:
                score += 10
            elif piece == ChessPiece.BLACK_PAWN:
                score -= 10
            elif piece in [ChessPiece.WHITE_KNIGHT, ChessPiece.WHITE_BISHOP]:
                score += 5
            elif piece in [ChessPiece.BLACK_KNIGHT, ChessPiece.BLACK_BISHOP]:
                score -= 5

        return score

    def _update_game_phase(self, game: GameState):
        board = game.get_board()

        white_material = black_material = 0
        queens = 0

        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece == ChessPiece.WHITE_QUEEN:
                    queens += 1
                    white_material += 9
                elif piece == ChessPiece.BLACK_QUEEN:
                    queens += 1
                    black_material += 9
                elif piece == ChessPiece.WHITE_ROOK:
                    white_material += 5
                elif piece == ChessPiece.BLACK_ROOK:
                    black_material += 5
                elif piece in [ChessPiece.WHITE_BISHOP, ChessPiece.WHITE_KNIGHT]:
                    white_material += 3
                elif piece in [ChessPiece.BLACK_BISHOP, ChessPiece.BLACK_KNIGHT]:
                    black_material += 3

        total_material = white_material + black_material

        if total_material >= 30:
            self.game_phase = 'opening'
        elif queens == 0 or total_material <= 12:
            self.game_phase = 'endgame'
        else:
            self.game_phase = 'middlegame'
