
import copy
import time
from pygame.locals import *
from clobber import *

from clobber import Clobber, Piece, Position, Move

class MinMax:
    class Node:
        def __init__(self, state: Clobber, parent=None, move=None):
            self.state = state
            self.parent = parent
            self.children = []
            self.value = None
            self.move = move

        def __repr__(self):
            return f"Node(value={self.value}, move={self.move})"

    def __init__(self, clobber_engine: Clobber):
        self.clobber_engine = clobber_engine
        self.max_depth = 5
        self.nodes_evaluated = 0
        
    def set_max_depth(self, depth: int):
        self.max_depth = depth
        
    def get_best_move(self):
        start_time = time.time()
        self.nodes_evaluated = 0
        root = self.Node(copy.deepcopy(self.clobber_engine))
        best_value = self.minimax(root, self.max_depth, float('-inf'), float('inf'), True)
        best_moves = []
        for child in root.children:
            if child.value == best_value:
                best_moves.append(child.move)
        best_move = best_moves[0] if best_moves else None
        end_time = time.time()
        print(f"Evaluated {self.nodes_evaluated} nodes")
        print(f"Calculation time: {end_time - start_time:.3f} s")
        print(f"Best move: {best_move} (value: {best_value})")
        return best_move
    
    def minimax(self, node: Node, depth: int, alpha: float, beta: float, maximizing_player: bool):
        self.nodes_evaluated += 1
        if depth == 0 or node.state.game_over:
            node.value = self.evaluate(node.state)
            return node.value
        legal_moves = node.state.get_legal_moves()
        if not legal_moves:
            node.value = self.evaluate(node.state)
            return node.value
        if maximizing_player:
            best_value = float('-inf')
            for move in legal_moves:
                child_state = copy.deepcopy(node.state)
                child_state.make_move(move)
                child_node = self.Node(child_state, node, move)
                node.children.append(child_node)
                value = self.minimax(child_node, depth - 1, alpha, beta, False)
                best_value = max(best_value, value)
                alpha = max(alpha, best_value)
                if beta <= alpha:
                    break
            node.value = best_value
            return best_value
        else:
            best_value = float('inf')
            for move in legal_moves:
                child_state = copy.deepcopy(node.state)
                child_state.make_move(move)
                child_node = self.Node(child_state, node, move)
                node.children.append(child_node)
                value = self.minimax(child_node, depth - 1, alpha, beta, True)
                best_value = min(best_value, value)
                beta = min(beta, best_value)
                if beta <= alpha:
                    break
            node.value = best_value
            return best_value
    
    def evaluate(self, state: Clobber):
        if state.game_over:
            if state.winner == Piece.BLACK:
                return 1000
            elif state.winner == Piece.WHITE:
                return -1000
            else:
                return 0
        original_turn = state.current_turn
        state.current_turn = Piece.BLACK
        black_moves = len(state.get_legal_moves())
        state.current_turn = Piece.WHITE
        white_moves = len(state.get_legal_moves())
        state.current_turn = original_turn
        black_pieces = 0
        white_pieces = 0
        for row in state.board:
            for piece in row:
                if piece == Piece.BLACK:
                    black_pieces += 1
                elif piece == Piece.WHITE:
                    white_pieces += 1
        mobility_score = black_moves - white_moves
        piece_score = black_pieces - white_pieces
        return mobility_score * 3 + piece_score