from chess.move_generator import MoveGenerator
from general.game import GameState
from general.move import Move
from general.enums import Piece
from typing import List, Tuple, Optional
from chess.chess_piece import ChessPiece


class Chess(GameState):

    DEFAULT_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

    def __init__(self, fen_notation=DEFAULT_FEN):
        self.current_player = None
        self.white_castle_king_side = True
        self.white_castle_queen_side = False
        self.black_castle_king_side = False
        self.black_castle_queen_side = False
        self.enpassant_square = None
        self.halfmove = 0
        self.fullmove = 0
        self.board = []
        self.move_generator = None
        self.initialize(fen_notation)

    def initialize(self, fen_notation: str):
        board_str, player, castle, enpassant, halfmove, fullmove = fen_notation.split(' ')
        self.current_player = Piece.WHITE if player == 'w' else Piece.BLACK
        self.white_castle_king_side = 'K' in castle
        self.white_castle_queen_side = 'Q' in castle
        self.black_castle_king_side = 'k' in castle
        self.black_castle_queen_side = 'q' in castle
        self.enpassant_square = None if enpassant == '-' else self._algebraic_to_coords(enpassant)
        self.halfmove = int(halfmove)
        self.fullmove = int(fullmove)

        rows = board_str.split('/')
        board = []
        for row in rows:
            current_row = []
            for char in row:
                if char.isdigit():
                    current_row.extend([ChessPiece.EMPTY] * int(char))
                else:
                    current_row.append(ChessPiece.from_fen(char))
            board.append(current_row)
        self.board = board

        self._init_move_generator()

    def _init_move_generator(self):
        self.move_generator = MoveGenerator(
            self.board,
            self.current_player,
            self.white_castle_king_side,
            self.white_castle_queen_side,
            self.black_castle_king_side,
            self.black_castle_queen_side,
            self.enpassant_square
        )

    def get_legal_moves(self) -> List[Move]:
        self._init_move_generator()
        return self.move_generator.get_legal_moves()

    def make_move(self, move: Move):
        from_row, from_col = move.from_pos
        to_row, to_col = move.to_pos
        src_piece = self.board[from_row][from_col]

        if src_piece in [ChessPiece.WHITE_PAWN, ChessPiece.BLACK_PAWN] or self.board[to_row][
            to_col] != ChessPiece.EMPTY:
            self.halfmove = 0
        else:
            self.halfmove += 1

        if self.current_player == Piece.BLACK:
            self.fullmove += 1

        if src_piece in [ChessPiece.WHITE_PAWN, ChessPiece.BLACK_PAWN] and (from_col != to_col) and self.board[to_row][
            to_col] == ChessPiece.EMPTY:
            if self.enpassant_square == (to_row, to_col):
                self.board[from_row][to_col] = ChessPiece.EMPTY

        self.enpassant_square = None
        if src_piece in [ChessPiece.WHITE_PAWN, ChessPiece.BLACK_PAWN] and abs(from_row - to_row) == 2:
            middle_row = (from_row + to_row) // 2
            self.enpassant_square = (middle_row, from_col)

        if src_piece in [ChessPiece.WHITE_KING, ChessPiece.BLACK_KING] and abs(from_col - to_col) == 2:
            king_row = from_row
            if to_col > from_col:
                rook_src_col = 7
                rook_dest_col = 5
                self.board[king_row][rook_dest_col] = self.board[king_row][rook_src_col]
                self.board[king_row][rook_src_col] = ChessPiece.EMPTY
            else:
                rook_src_col = 0
                rook_dest_col = 3
                self.board[king_row][rook_dest_col] = self.board[king_row][rook_src_col]
                self.board[king_row][rook_src_col] = ChessPiece.EMPTY

        if src_piece == ChessPiece.WHITE_KING:
            self.white_castle_king_side = False
            self.white_castle_queen_side = False
        elif src_piece == ChessPiece.BLACK_KING:
            self.black_castle_king_side = False
            self.black_castle_queen_side = False
        elif src_piece == ChessPiece.WHITE_ROOK:
            if from_row == 7 and from_col == 0:
                self.white_castle_queen_side = False
            elif from_row == 7 and from_col == 7:
                self.white_castle_king_side = False
        elif src_piece == ChessPiece.BLACK_ROOK:
            if from_row == 0 and from_col == 0:
                self.black_castle_queen_side = False
            elif from_row == 0 and from_col == 7:
                self.black_castle_king_side = False

        if move.prom:
            promoted_piece = None
            if self.current_player == Piece.WHITE:
                if move.prom == 'Q':
                    promoted_piece = ChessPiece.WHITE_QUEEN
                elif move.prom == 'R':
                    promoted_piece = ChessPiece.WHITE_ROOK
                elif move.prom == 'B':
                    promoted_piece = ChessPiece.WHITE_BISHOP
                elif move.prom == 'N':
                    promoted_piece = ChessPiece.WHITE_KNIGHT
            else:
                if move.prom == 'Q':
                    promoted_piece = ChessPiece.BLACK_QUEEN
                elif move.prom == 'R':
                    promoted_piece = ChessPiece.BLACK_ROOK
                elif move.prom == 'B':
                    promoted_piece = ChessPiece.BLACK_BISHOP
                elif move.prom == 'N':
                    promoted_piece = ChessPiece.BLACK_KNIGHT

            self.board[to_row][to_col] = promoted_piece
        else:
            self.board[to_row][to_col] = src_piece

        self.board[from_row][from_col] = ChessPiece.EMPTY

        self.current_player = Piece.BLACK if self.current_player == Piece.WHITE else Piece.WHITE

        self._init_move_generator()

    def is_terminal(self) -> bool:
        if not self.get_legal_moves():
            return True

        if self._has_insufficient_material():
            return True

        if self.halfmove >= 100:
            return True

        return False

    def get_initial_state(self):
        return Chess()

    def get_board(self):
        return self.board

    def get_current_player(self):
        return self.current_player

    def is_check(self) -> bool:
        return self.move_generator.is_in_check(self.current_player)

    def is_checkmate(self) -> bool:
        if not self.move_generator.is_in_check(self.current_player):
            return False

        return len(self.get_legal_moves()) == 0

    def is_stalemate(self) -> bool:
        if self.move_generator.is_in_check(self.current_player):
            return False

        return len(self.get_legal_moves()) == 0

    def get_game_state(self) -> str:
        if self.is_checkmate():
            return "checkmate"
        elif self.is_check():
            return "check"
        elif self.is_stalemate():
            return "stalemate"
        else:
            return "ongoing"

    def _has_insufficient_material(self) -> bool:
        pieces = {
            Piece.WHITE: {'pawn': 0, 'knight': 0, 'bishop': 0, 'rook': 0, 'queen': 0, 'king': 0},
            Piece.BLACK: {'pawn': 0, 'knight': 0, 'bishop': 0, 'rook': 0, 'queen': 0, 'king': 0}
        }

        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece != ChessPiece.EMPTY:
                    if piece == ChessPiece.WHITE_PAWN:
                        pieces[Piece.WHITE]['pawn'] += 1
                    elif piece == ChessPiece.WHITE_KNIGHT:
                        pieces[Piece.WHITE]['knight'] += 1
                    elif piece == ChessPiece.WHITE_BISHOP:
                        pieces[Piece.WHITE]['bishop'] += 1
                    elif piece == ChessPiece.WHITE_ROOK:
                        pieces[Piece.WHITE]['rook'] += 1
                    elif piece == ChessPiece.WHITE_QUEEN:
                        pieces[Piece.WHITE]['queen'] += 1
                    elif piece == ChessPiece.WHITE_KING:
                        pieces[Piece.WHITE]['king'] += 1
                    elif piece == ChessPiece.BLACK_PAWN:
                        pieces[Piece.BLACK]['pawn'] += 1
                    elif piece == ChessPiece.BLACK_KNIGHT:
                        pieces[Piece.BLACK]['knight'] += 1
                    elif piece == ChessPiece.BLACK_BISHOP:
                        pieces[Piece.BLACK]['bishop'] += 1
                    elif piece == ChessPiece.BLACK_ROOK:
                        pieces[Piece.BLACK]['rook'] += 1
                    elif piece == ChessPiece.BLACK_QUEEN:
                        pieces[Piece.BLACK]['queen'] += 1
                    elif piece == ChessPiece.BLACK_KING:
                        pieces[Piece.BLACK]['king'] += 1

        white_material = sum(pieces[Piece.WHITE].values()) - pieces[Piece.WHITE]['king']
        black_material = sum(pieces[Piece.BLACK].values()) - pieces[Piece.BLACK]['king']

        if white_material == 0 and black_material == 0:
            return True

        if (white_material == 0 and black_material == 1 and
                (pieces[Piece.BLACK]['knight'] == 1 or pieces[Piece.BLACK]['bishop'] == 1)):
            return True

        if (black_material == 0 and white_material == 1 and
                (pieces[Piece.WHITE]['knight'] == 1 or pieces[Piece.WHITE]['bishop'] == 1)):
            return True

        if (pieces[Piece.WHITE]['bishop'] == 1 and pieces[Piece.BLACK]['bishop'] == 1 and
                white_material == 1 and black_material == 1):
            white_bishop_pos = None
            black_bishop_pos = None

            for row in range(8):
                for col in range(8):
                    if self.board[row][col] == ChessPiece.WHITE_BISHOP:
                        white_bishop_pos = (row, col)
                    elif self.board[row][col] == ChessPiece.BLACK_BISHOP:
                        black_bishop_pos = (row, col)

            if white_bishop_pos and black_bishop_pos:
                if (white_bishop_pos[0] + white_bishop_pos[1]) % 2 == (black_bishop_pos[0] + black_bishop_pos[1]) % 2:
                    return True

        return False

    def get_fen(self) -> str:
        board_str = ''
        for row in self.board:
            empty_count = 0
            for piece in row:
                if piece == ChessPiece.EMPTY:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        board_str += str(empty_count)
                        empty_count = 0
                    board_str += str(piece)
            if empty_count > 0:
                board_str += str(empty_count)
            board_str += '/'

        board_str = board_str[:-1]
        player = 'w' if self.current_player == Piece.WHITE else 'b'
        castle = ''
        if self.white_castle_king_side:
            castle += 'K'
        if self.white_castle_queen_side:
            castle += 'Q'
        if self.black_castle_king_side:
            castle += 'k'
        if self.black_castle_queen_side:
            castle += 'q'
        if not castle:
            castle = '-'
        enpassant = '-' if self.enpassant_square is None else chr(self.enpassant_square[1] + ord('a')) + str(8 - self.enpassant_square[0])
        return f"{board_str} {player} {castle} {enpassant} {self.halfmove} {self.fullmove}"

    def _algebraic_to_coords(self, algebraic: str) -> Tuple[int, int]:
        if len(algebraic) != 2:
            return None

        col = ord(algebraic[0]) - ord('a')
        row = 8 - int(algebraic[1])

        if 0 <= row < 8 and 0 <= col < 8:
            return (row, col)
        return None


if __name__ == '__main__':
    import random

    chess = Chess()
    done = False

    while not done:
        move = random.choice(chess.get_legal_moves())
        chess.make_move(move)
        done = chess.is_terminal()

        board = chess.get_board()
        print(chess.get_fen())
        print()
