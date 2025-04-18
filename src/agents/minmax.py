import logging
from general.strategy import Strategy
from general.game import GameState
from general.move import Move
from general.agent import Agent
from typing import Optional, Tuple
from general.enums import Piece
import copy

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    filename='minmax.log',
                    format='[%(levelname)s] %(message)s')


class MinMax(Agent):
    def __init__(self, player: Piece, depth: int, strategy: Strategy):
        self.player = player
        self.max_depth = depth
        self.strategy = strategy

        self.nodes_visited = 0
        self.alpha_beta_cuts = 0

    def choose_move(self, state: GameState) -> Optional[Move]:
        self.nodes_visited = 0
        self.alpha_beta_cuts = 0

        maximizing = (state.current_player == self.player)
        score, best_move = self.minmax(state, self.max_depth, float('-inf'), float('inf'), maximizing)

        logger.info(f"Liczba odwiedzonych węzłów: {self.nodes_visited}")
        logger.info(f"Liczba cięć alfa-beta: {self.alpha_beta_cuts}")
        logger.info(f"Ostateczna ocena pozycji: {score}")

        return best_move

    def minmax(
        self,
        state: GameState,
        depth: int,
        alpha: float,
        beta: float,
        maximizing: bool
    ) -> Tuple[float, Optional[Move]]:

        self.nodes_visited += 1

        if depth == 0 or state.is_terminal():
            value = self.strategy.evaluate(state)
            return value, None

        legal_moves = state.get_legal_moves()
        best_move = None

        if maximizing:
            max_eval = float('-inf')
            for move in legal_moves:
                new_state = copy.deepcopy(state)
                new_state.make_move(move)
                eval_score, _ = self.minmax(new_state, depth - 1, alpha, beta, False)

                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move

                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    self.alpha_beta_cuts += 1
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in legal_moves:
                new_state = copy.deepcopy(state)
                new_state.make_move(move)
                eval_score, _ = self.minmax(new_state, depth - 1, alpha, beta, True)

                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move

                beta = min(beta, eval_score)
                if beta <= alpha:
                    self.alpha_beta_cuts += 1
                    break
            return min_eval, best_move
