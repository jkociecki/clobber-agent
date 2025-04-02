import copy
import time
from pygame.locals import *
from clobber import Clobber, Piece, Position, Move

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

    def __init__(self, clobber_engine: Clobber):
        self.clobber_engine = clobber_engine
        self.max_depth = 5
        self.nodes_evaluated = 0
        
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
        """
        Funkcja oceny stanu gry. Implementacja zależy od specyfiki gry Clobber.
        Przykładowa implementacja może brać pod uwagę liczbę dostępnych ruchów
        dla każdego gracza, kontrolę nad planszą, lub inne metryki strategiczne.
        """

        if node.state.game_over:
            current_player = node.state.current_turn
            return -1000 if current_player == Piece.WHITE else 1000
        
        original_turn = node.state.current_turn

        node.state.current_turn = Piece.WHITE
        white_moves = len(node.state.get_legal_moves())
        
        node.state.current_turn = Piece.BLACK
        black_moves = len(node.state.get_legal_moves())
        
        node.state.current_turn = original_turn

        mobility_score = white_moves - black_moves
        
        return mobility_score