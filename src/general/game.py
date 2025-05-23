from abc import ABC, abstractmethod
from typing import List
from general.move import Move


class GameState(ABC):

    @abstractmethod
    def get_legal_moves(self) -> List[Move]:
        pass

    @abstractmethod
    def make_move(self, move: Move):
        pass

    @abstractmethod
    def is_terminal(self) -> bool:
        pass

    @abstractmethod
    def get_initial_state(self):
        pass

    @abstractmethod
    def get_board(self):
        pass

    @abstractmethod
    def get_current_player(self):
        pass