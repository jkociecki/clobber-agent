from enum import Enum


class Piece(Enum):
    WHITE = 0
    BLACK = 1
    EMPTY = 2

    def __str__(self):
        if self == Piece.EMPTY:
            return '_'
        elif self == Piece.BLACK:
            return 'B'
        elif self == Piece.WHITE:
            return 'W'


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def __eq__(self, other):
        if isinstance(other, Position):
            return self.x == other.x and self.y == other.y
        return False
    
    def __str__(self):
        return f"{chr(65 + self.x)}{self.y + 1}"
    
    @classmethod
    def from_string(cls, position_str):
        """Konwertuje notację (np. 'A1') na obiekt Position."""
        if len(position_str) < 2:
            raise ValueError("Niepoprawna notacja pozycji")
        
        x = ord(position_str[0].upper()) - 65 
        y = int(position_str[1:]) - 1 
        
        return cls(x, y)


class Move:
    def __init__(self, start, end):
        self.start = start
        self.end = end
    
    def __str__(self):
        return f"{self.start}->{self.end}"


class Clobber:
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.board = self.initialize_board(height=self.height, width=self.width)
        self.current_turn = Piece.BLACK
        self.moves_history = []
        self.game_over = False
        self.winner = None
    
    def initialize_board(self, height, width):
        """inicjalizacja planszy do gry"""
        board = []

        for y in range(height):
            row = []
            for x in range(width):
                if (x + y) % 2 == 0:
                    row.append(Piece.WHITE)
                else:
                    row.append(Piece.BLACK)
            board.append(row)

        return board
    
    def get_piece(self, position):
        """Pobiera pionek na danej pozycji."""
        if 0 <= position.x < self.width and 0 <= position.y < self.height:
            return self.board[position.y][position.x]
        return None
    
    def set_piece(self, position, piece):
        """Ustawia pionek na danej pozycji."""
        if 0 <= position.x < self.width and 0 <= position.y < self.height:
            self.board[position.y][position.x] = piece
    
    def get_adjacent_positions(self, position):
        """Zwraca listę sąsiednich pozycji."""
        adjacent = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # góra, prawo, dół, lewo
        
        for dx, dy in directions:
            new_x, new_y = position.x + dx, position.y + dy
            if 0 <= new_x < self.width and 0 <= new_y < self.height:
                adjacent.append(Position(new_x, new_y))
        
        return adjacent
    
    def is_legal_move(self, move):
        """Sprawdza, czy ruch jest legalny."""
        if self.game_over:
            return False
        
        if not (0 <= move.start.x < self.width and 0 <= move.start.y < self.height and
                0 <= move.end.x < self.width and 0 <= move.end.y < self.height):
            return False
        
        start_piece = self.get_piece(move.start)
        if start_piece != self.current_turn:
            return False
        
        adjacent_positions = self.get_adjacent_positions(move.start)
        if move.end not in adjacent_positions:
            return False
        
        end_piece = self.get_piece(move.end)
        opponent = Piece.WHITE if self.current_turn == Piece.BLACK else Piece.BLACK
        if end_piece != opponent:
            return False
        
        return True
    
    def make_move(self, move):
        """Wykonuje ruch na planszy."""
        if not self.is_legal_move(move):
            return False
        
        self.set_piece(move.end, self.current_turn)  
        self.set_piece(move.start, Piece.EMPTY)
        
        self.moves_history.append(move)
        
        self.current_turn = Piece.WHITE if self.current_turn == Piece.BLACK else Piece.BLACK
        
        if not self.has_legal_moves():
            self.game_over = True
            self.winner = Piece.WHITE if self.current_turn == Piece.BLACK else Piece.BLACK
        
        return True
    
    def has_legal_moves(self):
        """Sprawdza, czy aktualny gracz ma jakiekolwiek legalne ruchy."""
        for y in range(self.height):
            for x in range(self.width):
                pos = Position(x, y)
                if self.get_piece(pos) == self.current_turn:
                    for adj_pos in self.get_adjacent_positions(pos):
                        move = Move(pos, adj_pos)
                        if self.is_legal_move(move):
                            return True
        return False
    
    def get_legal_moves(self):
        """Zwraca listę wszystkich legalnych ruchów dla aktualnego gracza."""
        legal_moves = []
        for y in range(self.height):
            for x in range(self.width):
                pos = Position(x, y)
                if self.get_piece(pos) == self.current_turn:
                    for adj_pos in self.get_adjacent_positions(pos):
                        move = Move(pos, adj_pos)
                        if self.is_legal_move(move):
                            legal_moves.append(move)
        return legal_moves
    
    def parse_move(self, move_str):
        """Konwertuje notację ruchu (np. 'A1-B1') na obiekt Move."""
        parts = move_str.split('-')
        if len(parts) != 2:
            raise ValueError("Niepoprawna notacja ruchu. Użyj formatu: 'A1-B1'")
        
        start = Position.from_string(parts[0])
        end = Position.from_string(parts[1])
        
        return Move(start, end)
    
    def print_board(self):
        print("   ", end="")
        for col in range(self.width):
            print(chr(65 + col), end=" ") 
        print()

        for row_index, row in enumerate(self.board):
            print(f"{row_index + 1:2} ", end="") 
            print(" ".join(str(piece) for piece in row))
    
    def get_game_state(self):
        """Zwraca aktualny stan gry."""
        return {
            'board': self.board,
            'current_turn': self.current_turn,
            'game_over': self.game_over,
            'winner': self.winner,
            'moves_history': self.moves_history
        }
    
    def undo_move(self):
        """Cofa ostatni ruch."""
        if not self.moves_history:
            return False
        
        last_move = self.moves_history.pop()
        
        self.current_turn = Piece.WHITE if self.current_turn == Piece.BLACK else Piece.BLACK
        
        self.set_piece(last_move.start, self.current_turn)
        
        opponent = Piece.WHITE if self.current_turn == Piece.BLACK else Piece.BLACK
        self.set_piece(last_move.end, opponent)
        
        self.game_over = False
        self.winner = None
        
        return True


if __name__ == '__main__':
    game = Clobber(6, 6)  # Standardowa plansza 6x6
    
    print("Witaj w grze Clobber!")
    game.print_board()
    
    moves = game.get_legal_moves()
    for move in moves:
        print(f"Możliwe ruchy: {move}")