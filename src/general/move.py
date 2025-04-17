from typing import Optional, Tuple


class Move:

    def __init__(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], prom: Optional[str] = None):
        self.from_pos = from_pos
        self.to_pos = to_pos
        self.prom = prom

    def __eq__(self, other):
        if not isinstance(other, Move):
            return NotImplemented
        return (self.from_pos, self.to_pos, self.prom) == (other.from_pos, other.to_pos, other.prom)

    def __repr__(self):
        return f"Move {self.from_pos} -> {self.to_pos}"
