from enum import Enum
from general.enums import Piece


class ChessPiece(Enum):
    WHITE_PAWN = ('P', Piece.WHITE)
    WHITE_ROOK = ('R', Piece.WHITE)
    WHITE_KNIGHT = ('N', Piece.WHITE)
    WHITE_BISHOP = ('B', Piece.WHITE)
    WHITE_KING = ('K', Piece.WHITE)
    WHITE_QUEEN = ('Q', Piece.WHITE)

    BLACK_PAWN = ('p', Piece.BLACK)
    BLACK_ROOK = ('r', Piece.BLACK)
    BLACK_KNIGHT = ('n', Piece.BLACK)
    BLACK_BISHOP = ('b', Piece.BLACK)
    BLACK_KING = ('k', Piece.BLACK)
    BLACK_QUEEN = ('q', Piece.BLACK)

    EMPTY = ('.', Piece.EMPTY)

    def __str__(self):
        return self.value[0]  # litera FEN

    @property
    def color(self) -> Piece:
        return self.value[1]

    @staticmethod
    def from_fen(char: str):
        for piece in ChessPiece:
            if piece.value[0] == char:
                return piece
        return ChessPiece.EMPTY
