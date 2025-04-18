from general.game import GameState
from general.move import Move
from general.enums import Piece
from typing import List, Tuple, Optional
from chess.chess_piece import ChessPiece


class MoveGenerator:
    def __init__(self, board, current_player, white_castle_king_side, white_castle_queen_side,
                 black_castle_king_side, black_castle_queen_side, enpassant_square):
        self.board = board
        self.current_player = current_player
        self.white_castle_king_side = white_castle_king_side
        self.white_castle_queen_side = white_castle_queen_side
        self.black_castle_king_side = black_castle_king_side
        self.black_castle_queen_side = black_castle_queen_side
        self.enpassant_square = enpassant_square

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

    def is_in_check(self, color: Piece) -> bool:
        king_position = None
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece == (ChessPiece.WHITE_KING if color == Piece.WHITE else ChessPiece.BLACK_KING):
                    king_position = (r, c)
                    break
            if king_position:
                break

        if not king_position:
            return False

        opponent_color = Piece.BLACK if color == Piece.WHITE else Piece.WHITE
        return self._is_square_attacked(king_position[0], king_position[1], opponent_color)