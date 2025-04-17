from typing import List, Tuple
from general.enums import Piece
from general.game import GameState
from general.move import Move


class Clobber(GameState):

    def __init__(self, height: int, width: int):
        self.height = height
        self.width = width
        self.board, self.current_player = self.initialize_board()

    @classmethod
    def from_canonical(cls, canonical_form: str) -> 'Clobber':
        obj = cls.__new__(cls)
        obj.board, obj.current_player = obj.get_initial_state_canonical(canonical_form)
        obj.height = len(obj.board)
        obj.width = len(obj.board[0]) if obj.board else 0
        return obj

    @staticmethod
    def get_initial_state_canonical(canonical_form: str) -> Tuple[List[List[Piece]], Piece]:
        board = []
        canonical_form = canonical_form.split(' ')
        rows = canonical_form[0].strip().split('/')
        player = Piece.BLACK if canonical_form[1] == 'B' else Piece.WHITE

        for row_str in rows:
            bord_row = []
            for char in row_str:
                if char == 'W':
                    bord_row.append(Piece.WHITE)
                elif char == 'B':
                    bord_row.append(Piece.BLACK)
                else:
                    bord_row.append(Piece.EMPTY)
            board.append(bord_row)
        return board, player

    def initialize_board(self) -> Tuple[List[List[Piece]], Piece]:
        board = []
        for x in range(self.height):
            board_row = []
            for y in range(self.width):
                board_row.append(Piece.WHITE if (x + y) % 2 == 0 else Piece.BLACK)
            board.append(board_row)
        return board, Piece.BLACK

    def get_legal_moves(self) -> List[Move]:
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        legal_moves = []

        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] == self.current_player:
                    for dx, dy in directions:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            target_piece = self.board[ny][nx]
                            if target_piece == ~self.board[y][x]:
                                legal_moves.append(Move(from_pos=(x, y), to_pos=(nx, ny)))

        return legal_moves

    def make_move(self, move: Move):

        fx, fy = move.from_pos
        tx, ty = move.to_pos

        self.board[ty][tx] = self.board[fy][fx]
        self.board[fy][fx] = Piece.EMPTY
        self.current_player = ~self.current_player

    def is_terminal(self) -> bool:

        return len(self.get_legal_moves()) == 0

    def get_board(self):
        return self.board
    
    def get_current_player(self):
        return self.current_player
    
    def get_initial_state(self):
        pass



if __name__ == '__main__':
    game1 = Clobber(5, 5)

    print(game1.get_legal_moves())
    print(~Piece.WHITE)
