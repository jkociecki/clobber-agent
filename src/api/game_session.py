from src.general.game import GameState


class GameSession:
    game_id: str
    state: GameState
    ai_oponent: bool = False
