import copy
import time
from pygame.locals import *
from clobber import Clobber, Piece, Position, Move
from strategy import *

class MinMax:

    class Node:
        def __init__(self, state: Clobber, parent=None, move=None):
            self.state = state
            self.parent = parent
            self.children = []
            self.value = None
            self.move = move

        def generate_children(self):
            legal_moves = self.state.get_legal_moves()
            for move in legal_moves:
                new_state = copy.deepcopy(self.state)
                new_state.make_move(move)
                child = MinMax.Node(new_state, parent=self, move=move)
                self.children.append(child)
            return self.children

        def __repr__(self):
            return f"Node(value={self.value}, move={self.move})"
        

    def __init__(self, clobber_engine: Clobber, strategy_context: StrategyContext):
        self.clobber_engine = clobber_engine
        self.max_depth = 3
        self.nodes_evaluated = 0
        self.strategy_context = strategy_context
        
    def set_max_depth(self, depth: int):
        self.max_depth = depth
        
    def get_best_move(self):
        self.nodes_evaluated = 0
        root = self.Node(copy.deepcopy(self.clobber_engine))
        
        root.generate_children()
        
        if not root.children:
            return None
            
        best_value = self.minimax(root, self.max_depth, float('-inf'), float('inf'), True)
        
        best_moves = []
        for child in root.children:
            if child.value == best_value:
                best_moves.append(child.move)
        
        best_move = best_moves[0] if best_moves else None
        return best_move
    
    
    def minimax(self, node: Node, depth: int, alpha: float, beta: float, maximizing_player: bool):
        if depth == 0 or node.state.game_over:
            node.value = self.evaluate(node)
            self.nodes_evaluated += 1
            return node.value
        
        if not node.children:
            node.generate_children()
            
        if not node.children:
            node.value = self.evaluate(node)
            self.nodes_evaluated += 1
            return node.value
        
        if maximizing_player:
            value = float('-inf')
            
            for child in node.children:
                child_value = self.minimax(child, depth-1, alpha, beta, False)
                value = max(value, child_value)
                alpha = max(alpha, value)
                
                if beta <= alpha:
                    break
                    
            node.value = value
            return value
        
        else: 
            value = float('inf')
            
            for child in node.children:
                child_value = self.minimax(child, depth-1, alpha, beta, True)
                value = min(value, child_value)
                beta = min(beta, value)
                
                # Przycinanie alfa-beta
                if beta <= alpha:
                    break
                    
            node.value = value
            return value
            
    def evaluate(self, node: Node):
        return self.strategy_context.evaluate(node, node.state)