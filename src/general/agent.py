from abc import ABC, abstractmethod
from general.game import GameState
from typing import Optional
from general.move import Move

class Agent(ABC):
    @abstractmethod
    def choose_move(self, state: GameState) -> Optional[Move]:
        pass
