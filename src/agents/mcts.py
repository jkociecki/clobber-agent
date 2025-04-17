from general.agent import Agent
from general.game import GameState
from general.move import Move
from general.enums import Piece
from typing import Optional, Dict, List
import random
import math
import copy
import time

class Node:
    def __init__(self, state: GameState, parent=None, move=None):
        self.state = state
        self.parent = parent
        self.move = move  
        self.children = []
        self.visits = 0
        self.wins = 0
        self.untried_moves = state.get_legal_moves()
        self.player = state.get_current_player() 

    def select_child(self, exploration_weight=1.4):
        return max(self.children, key=lambda child: 
                   (child.wins / child.visits) + 
                   exploration_weight * math.sqrt(math.log(self.visits) / child.visits))

    def expand(self):
        if not self.untried_moves:
            return None
            
        move = random.choice(self.untried_moves)
        self.untried_moves.remove(move)
        
        new_state = copy.deepcopy(self.state)
        new_state.make_move(move)
        
        child = Node(new_state, parent=self, move=move)
        self.children.append(child)
        return child

    def update(self, result):
        self.visits += 1
        self.wins += result

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def is_terminal(self):
        return self.state.is_terminal()


class MCTS(Agent):
    def __init__(self, player: Piece, simulation_time: float = 1.0, exploration_weight: float = 1.4):
        self.player = player
        self.simulation_time = simulation_time 
        self.exploration_weight = exploration_weight

    def choose_move(self, state: GameState) -> Optional[Move]:
        root = Node(copy.deepcopy(state))
        end_time = time.time() + self.simulation_time
        
        while time.time() < end_time:
            node = self._select(root)
            
            if not node.is_terminal() and node.untried_moves:
                node = node.expand()
            
            result = self._simulate(node)
            
            self._backpropagate(node, result)
        
        if not root.children:
            return None

        best_child = max(root.children, key=lambda child: child.visits)
        return best_child.move

    def _select(self, node):
        while not node.is_terminal() and node.is_fully_expanded():
            node = node.select_child(self.exploration_weight)
        return node

    def _simulate(self, node):
        state = copy.deepcopy(node.state)
        current_player = state.get_current_player()
        
        while not state.is_terminal():
            legal_moves = state.get_legal_moves()
            if not legal_moves:
                break
            
            move = random.choice(legal_moves)
            state.make_move(move)

        winner = ~state.get_current_player()
        return 1 if winner == self.player else 0

    def _backpropagate(self, node, result):
        while node is not None:
            node.update(result)
            node = node.parent