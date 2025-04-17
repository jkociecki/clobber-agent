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

    def get_legal_moves(self) -> List[Move]:
        legal_moves = []

        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece != ChessPiece.EMPTY and piece.color == self.current_player:
                    piece_moves = self._get_piece_moves(row, col, piece)
                    legal_moves.extend(piece_moves)

        return legal_moves

    def _get_piece_moves(self, row: int, col: int, piece: ChessPiece) -> List[Move]:
        moves = []

        if piece in [ChessPiece.WHITE_PAWN, ChessPiece.BLACK_PAWN]:
            moves.extend(self._get_pawn_moves(row, col, piece))
        elif piece in [ChessPiece.WHITE_KNIGHT, ChessPiece.BLACK_KNIGHT]:
            moves.extend(self._get_knight_moves(row, col, piece))
        elif piece in [ChessPiece.WHITE_BISHOP, ChessPiece.BLACK_BISHOP]:
            moves.extend(self._get_bishop_moves(row, col, piece))
        elif piece in [ChessPiece.WHITE_ROOK, ChessPiece.BLACK_ROOK]:
            moves.extend(self._get_rook_moves(row, col, piece))
        elif piece in [ChessPiece.WHITE_QUEEN, ChessPiece.BLACK_QUEEN]:
            moves.extend(self._get_queen_moves(row, col, piece))
        elif piece in [ChessPiece.WHITE_KING, ChessPiece.BLACK_KING]:
            moves.extend(self._get_king_moves(row, col, piece))

        filtered_moves = []
        for move in moves:
            if not self._would_be_in_check_after_move(move):
                filtered_moves.append(move)

        return filtered_moves

    def _get_pawn_moves(self, row: int, col: int, piece: ChessPiece) -> List[Move]:

        moves = []
        color = piece.color
        direction = -1 if color == Piece.WHITE else 1
        start_row = 6 if color == Piece.WHITE else 1

        if 0 <= row + direction < 8 and self.board[row + direction][col] == ChessPiece.EMPTY:
            if (color == Piece.WHITE and row + direction == 0) or (color == Piece.BLACK and row + direction == 7):
                for prom in ['Q', 'R', 'B', 'N']:
                    moves.append(Move((row, col), (row + direction, col), prom))
            else:
                moves.append(Move((row, col), (row + direction, col)))

            if row == start_row and self.board[row + 2 * direction][col] == ChessPiece.EMPTY:
                moves.append(Move((row, col), (row + 2 * direction, col)))

        for col_offset in [-1, 1]:
            if 0 <= row + direction < 8 and 0 <= col + col_offset < 8:
                target = self.board[row + direction][col + col_offset]
                if target != ChessPiece.EMPTY and target.color != color:
                    if (color == Piece.WHITE and row + direction == 0) or (
                            color == Piece.BLACK and row + direction == 7):
                        for prom in ['Q', 'R', 'B', 'N']:
                            moves.append(Move((row, col), (row + direction, col + col_offset), prom))
                    else:
                        moves.append(Move((row, col), (row + direction, col + col_offset)))

                elif self.enpassant_square == (row + direction, col + col_offset):
                    moves.append(Move((row, col), (row + direction, col + col_offset)))

        return moves

    def _get_knight_moves(self, row: int, col: int, piece: ChessPiece) -> List[Move]:

        moves = []
        color = piece.color
        offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]

        for row_offset, col_offset in offsets:
            new_row, new_col = row + row_offset, col + col_offset
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = self.board[new_row][new_col]
                if target == ChessPiece.EMPTY or target.color != color:
                    moves.append(Move((row, col), (new_row, new_col)))

        return moves

    def _get_bishop_moves(self, row: int, col: int, piece: ChessPiece) -> List[Move]:

        moves = []
        color = piece.color
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for row_dir, col_dir in directions:
            for distance in range(1, 8):
                new_row, new_col = row + row_dir * distance, col + col_dir * distance
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    target = self.board[new_row][new_col]
                    if target == ChessPiece.EMPTY:
                        moves.append(Move((row, col), (new_row, new_col)))
                    elif target.color != color:
                        moves.append(Move((row, col), (new_row, new_col)))
                        break
                    else:
                        break
                else:
                    break

        return moves

    def _get_rook_moves(self, row: int, col: int, piece: ChessPiece) -> List[Move]:

        moves = []
        color = piece.color
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for row_dir, col_dir in directions:
            for distance in range(1, 8):
                new_row, new_col = row + row_dir * distance, col + col_dir * distance
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    target = self.board[new_row][new_col]
                    if target == ChessPiece.EMPTY:
                        moves.append(Move((row, col), (new_row, new_col)))
                    elif target.color != color:
                        moves.append(Move((row, col), (new_row, new_col)))
                        break
                    else:
                        break
                else:
                    break

        return moves

    def _get_queen_moves(self, row: int, col: int, piece: ChessPiece) -> List[Move]:

        bishop_moves = self._get_bishop_moves(row, col, piece)
        rook_moves = self._get_rook_moves(row, col, piece)
        return bishop_moves + rook_moves

    def _get_king_moves(self, row: int, col: int, piece: ChessPiece) -> List[Move]:
        moves = []
        color = piece.color

        for row_offset in [-1, 0, 1]:
            for col_offset in [-1, 0, 1]:
                if row_offset == 0 and col_offset == 0:
                    continue

                new_row = row + row_offset
                new_col = col + col_offset

                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    target = self.board[new_row][new_col]
                    if target == ChessPiece.EMPTY or target.color != color:
                        moves.append(Move((row, col), (new_row, new_col)))

        if color == Piece.WHITE and row == 7 and col == 4:
            if self.white_castle_king_side and \
                    self.board[7][5] == ChessPiece.EMPTY and \
                    self.board[7][6] == ChessPiece.EMPTY and \
                    not self._is_square_attacked(7, 4, Piece.BLACK) and \
                    not self._is_square_attacked(7, 5, Piece.BLACK) and \
                    not self._is_square_attacked(7, 6, Piece.BLACK):
                moves.append(Move((7, 4), (7, 6)))

            if self.white_castle_queen_side and \
                    all(self.board[7][i] == ChessPiece.EMPTY for i in range(1, 4)) and \
                    not self._is_square_attacked(7, 4, Piece.BLACK) and \
                    not self._is_square_attacked(7, 3, Piece.BLACK) and \
                    not self._is_square_attacked(7, 2, Piece.BLACK):
                moves.append(Move((7, 4), (7, 2)))

        elif color == Piece.BLACK and row == 0 and col == 4:
            if self.black_castle_king_side and \
                    self.board[0][5] == ChessPiece.EMPTY and \
                    self.board[0][6] == ChessPiece.EMPTY and \
                    not self._is_square_attacked(0, 4, Piece.WHITE) and \
                    not self._is_square_attacked(0, 5, Piece.WHITE) and \
                    not self._is_square_attacked(0, 6, Piece.WHITE):
                moves.append(Move((0, 4), (0, 6)))

            if self.black_castle_queen_side and \
                    all(self.board[0][i] == ChessPiece.EMPTY for i in range(1, 4)) and \
                    not self._is_square_attacked(0, 4, Piece.WHITE) and \
                    not self._is_square_attacked(0, 3, Piece.WHITE) and \
                    not self._is_square_attacked(0, 2, Piece.WHITE):
                moves.append(Move((0, 4), (0, 2)))

        return moves

    def _is_square_attacked(self, row: int, col: int, attacker_color: Piece) -> bool:

        pawn_directions = [[-1, -1], [-1, 1]] if attacker_color == Piece.BLACK else [[1, -1], [1, 1]]
        for d_row, d_col in pawn_directions:
            r, c = row + d_row, col + d_col
            if 0 <= r < 8 and 0 <= c < 8:
                piece = self.board[r][c]
                if (attacker_color == Piece.WHITE and piece == ChessPiece.WHITE_PAWN) or \
                        (attacker_color == Piece.BLACK and piece == ChessPiece.BLACK_PAWN):
                    return True

        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for d_row, d_col in knight_moves:
            r, c = row + d_row, col + d_col
            if 0 <= r < 8 and 0 <= c < 8:
                piece = self.board[r][c]
                if (attacker_color == Piece.WHITE and piece == ChessPiece.WHITE_KNIGHT) or \
                        (attacker_color == Piece.BLACK and piece == ChessPiece.BLACK_KNIGHT):
                    return True

        rook_directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for d_row, d_col in rook_directions:
            for dist in range(1, 8):
                r, c = row + d_row * dist, col + d_col * dist
                if not (0 <= r < 8 and 0 <= c < 8):
                    break
                piece = self.board[r][c]
                if piece != ChessPiece.EMPTY:
                    if (attacker_color == Piece.WHITE and (
                            piece == ChessPiece.WHITE_ROOK or piece == ChessPiece.WHITE_QUEEN)) or \
                            (attacker_color == Piece.BLACK and (
                                    piece == ChessPiece.BLACK_ROOK or piece == ChessPiece.BLACK_QUEEN)):
                        return True
                    break

        bishop_directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for d_row, d_col in bishop_directions:
            for dist in range(1, 8):
                r, c = row + d_row * dist, col + d_col * dist
                if not (0 <= r < 8 and 0 <= c < 8):
                    break
                piece = self.board[r][c]
                if piece != ChessPiece.EMPTY:
                    if (attacker_color == Piece.WHITE and (
                            piece == ChessPiece.WHITE_BISHOP or piece == ChessPiece.WHITE_QUEEN)) or \
                            (attacker_color == Piece.BLACK and (
                                    piece == ChessPiece.BLACK_BISHOP or piece == ChessPiece.BLACK_QUEEN)):
                        return True
                    break

        king_moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for d_row, d_col in king_moves:
            r, c = row + d_row, col + d_col
            if 0 <= r < 8 and 0 <= c < 8:
                piece = self.board[r][c]
                if (attacker_color == Piece.WHITE and piece == ChessPiece.WHITE_KING) or \
                        (attacker_color == Piece.BLACK and piece == ChessPiece.BLACK_KING):
                    return True

        return False

    def _would_be_in_check_after_move(self, move: Move) -> bool:

        from_row, from_col = move.from_pos
        to_row, to_col = move.to_pos
        src_piece = self.board[from_row][from_col]
        dest_piece = self.board[to_row][to_col]

        self.board[to_row][to_col] = src_piece
        self.board[from_row][from_col] = ChessPiece.EMPTY

        is_castling = False
        rook_src_pos = None
        rook_dest_pos = None

        if src_piece in [ChessPiece.WHITE_KING, ChessPiece.BLACK_KING] and abs(from_col - to_col) == 2:
            is_castling = True
            king_row = from_row
            if to_col > from_col:
                rook_src_pos = (king_row, 7)
                rook_dest_pos = (king_row, 5)
            else:
                rook_src_pos = (king_row, 0)
                rook_dest_pos = (king_row, 3)

            if is_castling:
                rook_piece = self.board[rook_src_pos[0]][rook_src_pos[1]]
                self.board[rook_dest_pos[0]][rook_dest_pos[1]] = rook_piece
                self.board[rook_src_pos[0]][rook_src_pos[1]] = ChessPiece.EMPTY

        captured_en_passant = None
        if src_piece in [ChessPiece.WHITE_PAWN, ChessPiece.BLACK_PAWN] and (
                from_col != to_col) and dest_piece == ChessPiece.EMPTY:
            if self.enpassant_square == (to_row, to_col):
                captured_en_passant = (from_row, to_col)
                self.board[captured_en_passant[0]][captured_en_passant[1]] = ChessPiece.EMPTY

        king_position = None
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece != ChessPiece.EMPTY and piece.color == self.current_player:
                    if piece == ChessPiece.WHITE_KING and self.current_player == Piece.WHITE:
                        king_position = (r, c)
                        break
                    elif piece == ChessPiece.BLACK_KING and self.current_player == Piece.BLACK:
                        king_position = (r, c)
                        break
            if king_position:
                break

        is_in_check = False
        if king_position:
            opponent = Piece.BLACK if self.current_player == Piece.WHITE else Piece.WHITE
            is_in_check = self._is_square_attacked(king_position[0], king_position[1], opponent)

        self.board[from_row][from_col] = src_piece
        self.board[to_row][to_col] = dest_piece

        if is_castling and rook_src_pos and rook_dest_pos:
            rook_piece = self.board[rook_dest_pos[0]][rook_dest_pos[1]]
            self.board[rook_src_pos[0]][rook_src_pos[1]] = rook_piece
            self.board[rook_dest_pos[0]][rook_dest_pos[1]] = ChessPiece.EMPTY

        if captured_en_passant:
            opponent_color = Piece.BLACK if self.current_player == Piece.WHITE else Piece.WHITE
            pawn_piece = ChessPiece.BLACK_PAWN if opponent_color == Piece.BLACK else ChessPiece.WHITE_PAWN
            self.board[captured_en_passant[0]][captured_en_passant[1]] = pawn_piece

        return is_in_check

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

    def is_terminal(self) -> bool:

        if not self.get_legal_moves():
            print('mat lub pat')
            return True

        if self._has_insufficient_material():
            print('brak materialu')
            return True

        if self.halfmove >= 100:
            print('50 bez bicia')
            return True

        return False

    def get_initial_state(self):
        return Chess()

    def get_board(self):
        return self.board

    def get_current_player(self):
        return self.current_player

    # Fix the bug in _has_insufficient_material method
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

        for row in board:
            print(' '.join(str(piece) for piece in row))
        print()
