from enum import Enum


class Piece(Enum):
    WHITE = 0
    BLACK = 1
    EMPTY = 2

    def __str__(self):

        if self == Piece.WHITE:
            return 'w'
        elif self == Piece.BLACK:
            return 'b'
        else:
            return '_'

    def __invert__(self):

        if self == Piece.WHITE:
            return Piece.BLACK

        elif self == Piece.BLACK:
            return Piece.WHITE

        return self
