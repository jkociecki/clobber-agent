from abc import ABC, abstractmethod
from general.game import GameState

class Strategy(ABC):

    @abstractmethod
    def evaluate(self, game: GameState):
        pass