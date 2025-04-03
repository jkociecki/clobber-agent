import copy
import random
import math
from clobber import Clobber, Piece, Move

class MCTS:
    
    class Node:
        def __init__(self, state: Clobber, parent=None, move=None):
            self.state = state  
            self.parent = parent 
            self.children = [] 
            self.visits = 0  
            self.wins = 0  
            self.move = move 
            
        def is_fully_expanded(self):
            return len(self.children) == len(self.state.get_legal_moves())

        def best_child(self, exploration_weight=1.4):
            return max(
                self.children, 
                key=lambda child: (child.wins / (child.visits + 1e-6)) + 
                exploration_weight * math.sqrt(math.log(self.visits + 1) / (child.visits + 1e-6))
            )
    
    def __init__(self, clobber_engine: Clobber, player: Piece, simulations=1000):
        self.clobber_engine = clobber_engine 
        self.player = player 
        self.simulations = simulations 

    def get_best_move(self):
        root = self.Node(copy.deepcopy(self.clobber_engine))
        
        for _ in range(self.simulations):
            node = self.selection(root)
            child = self.expansion(node)
            result = self.simulation(child)
            self.backpropagation(child, result)
        
        best_child = root.best_child(exploration_weight=0) 
        return best_child.move if best_child else None
    
    def selection(self, node):
        while not node.state.game_over and node.is_fully_expanded():
            node = node.best_child()
        return node

    def expansion(self, node):
        if node.state.game_over:
            return node
        
        legal_moves = node.state.get_legal_moves()
        existing_moves = {child.move for child in node.children}
        possible_moves = [move for move in legal_moves if move not in existing_moves]
        
        if not possible_moves:
            return node  
        
        move = random.choice(possible_moves)
        new_state = copy.deepcopy(node.state)
        new_state.make_move(move)
        
        child = self.Node(new_state, parent=node, move=move)
        node.children.append(child)
        return child

    def simulation(self, node):
        state = copy.deepcopy(node.state)
        
        while not state.game_over:
            legal_moves = state.get_legal_moves()
            if not legal_moves:
                break
            random_move = random.choice(legal_moves)
            state.make_move(random_move)
        
        return 1 if state.winner == self.player else 0  
    
    def backpropagation(self, node, result):
        while node:
            node.visits += 1
            node.wins += result
            node = node.parent
