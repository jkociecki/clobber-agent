from clobber import *
from strategy import *
import copy
from typing import List, Optional, Tuple


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
        

    def __init__(self, clobber_engine: Clobber, strategy_context: StrategyContext, player: Piece):
        self.clobber_engine = clobber_engine
        self.max_depth = 3
        self.nodes_evaluated = 0
        self.strategy_context = strategy_context
        self.player = player
        
    def set_max_depth(self, depth: int):
        self.max_depth = depth
        
    def get_best_move(self):
        self.nodes_evaluated = 0
        root = self.Node(copy.deepcopy(self.clobber_engine))
        
        best_value = float('-inf')
        best_move = None
        
        for child in root.generate_children():
            value = self.minimax(child, self.max_depth - 1, float('-inf'), float('inf'), False)
            child.value = value
            
            if value > best_value:
                best_value = value
                best_move = child.move
        
        return best_move

    
    def minimax(self, node: Node, depth: int, alpha: float, beta: float, maximizing_player: bool):
        if depth == 0 or node.state.game_over:
            value = self.evaluate(node)
            self.nodes_evaluated += 1
            return value

        if not node.children:
            node.generate_children()

        if not node.children:
            value = self.evaluate(node)
            self.nodes_evaluated += 1
            return value

        if maximizing_player:
            value = float('-inf')
            for child in node.children:
                child_value = self.minimax(child, depth - 1, alpha, beta, False)
                value = max(value, child_value)
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
        else:
            value = float('inf')
            for child in node.children:
                child_value = self.minimax(child, depth - 1, alpha, beta, True)
                value = min(value, child_value)
                beta = min(beta, value)
                if beta <= alpha:
                    break

        return value

    def evaluate(self, node: Node):
        return self.strategy_context.evaluate(node, node.state, self.player)