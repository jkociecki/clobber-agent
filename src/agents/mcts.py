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
        self.move = move  # ruch, który doprowadził do tego stanu
        self.children = []
        self.visits = 0
        self.wins = 0
        self.untried_moves = state.get_legal_moves()
        self.player = state.get_current_player()  # gracz, który ma teraz ruch

    def select_child(self, exploration_weight=1.4):
        """Wybiera dziecko używając UCB1 formula."""
        return max(self.children, key=lambda child: 
                   (child.wins / child.visits) + 
                   exploration_weight * math.sqrt(math.log(self.visits) / child.visits))

    def expand(self):
        """Rozszerza węzeł o jeden nowy ruch."""
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
        """Aktualizuje statystyki węzła po symulacji."""
        self.visits += 1
        self.wins += result

    def is_fully_expanded(self):
        """Sprawdza, czy wszystkie możliwe ruchy zostały wypróbowane."""
        return len(self.untried_moves) == 0

    def is_terminal(self):
        """Sprawdza, czy węzeł reprezentuje stan końcowy gry."""
        return self.state.is_terminal()


class MCTS(Agent):
    def __init__(self, player: Piece, simulation_time: float = 1.0, exploration_weight: float = 1.4):
        self.player = player
        self.simulation_time = simulation_time  # czas symulacji w sekundach
        self.exploration_weight = exploration_weight

    def choose_move(self, state: GameState) -> Optional[Move]:
        """Wybiera najlepszy ruch używając MCTS."""
        root = Node(copy.deepcopy(state))
        end_time = time.time() + self.simulation_time
        
        # Wykonuj MCTS dopóki nie skończy się czas
        while time.time() < end_time:
            # 1. Selekcja
            node = self._select(root)
            
            # 2. Ekspansja
            if not node.is_terminal() and node.untried_moves:
                node = node.expand()
            
            # 3. Symulacja
            result = self._simulate(node)
            
            # 4. Backpropagation
            self._backpropagate(node, result)
        
        # Wybierz najlepszy ruch na podstawie liczby wizyt
        if not root.children:
            return None

        best_child = max(root.children, key=lambda child: child.visits)
        return best_child.move

    def _select(self, node):
        """Wybiera węzeł do ekspansji używając UCB1."""
        while not node.is_terminal() and node.is_fully_expanded():
            node = node.select_child(self.exploration_weight)
        return node

    def _simulate(self, node):
        """Symuluje losową grę od bieżącego stanu i zwraca wynik."""
        state = copy.deepcopy(node.state)
        current_player = state.get_current_player()
        
        # Symuluj losową grę aż do stanu końcowego
        while not state.is_terminal():
            legal_moves = state.get_legal_moves()
            if not legal_moves:
                break
            
            move = random.choice(legal_moves)
            state.make_move(move)
        
        # Wynik: 1 jeśli wygrał gracz przypisany do agenta, 0 w przeciwnym przypadku
        # W Clobber przegrywa ten, kto nie może wykonać ruchu
        winner = ~state.get_current_player()  # Poprzedni gracz wygrywa
        return 1 if winner == self.player else 0

    def _backpropagate(self, node, result):
        """Propaguje wynik symulacji w górę drzewa."""
        while node is not None:
            node.update(result)
            node = node.parent