from clobber import *
from min_max import *
from strategy import *
from mcts import *





if __name__ == "__main__":
    clobber = Clobber(6, 6)
    clobber.print_board()

    white = MinMax(clobber, StrategyContext(AdaptiveStrategy()), Piece.WHITE)
    white.set_max_depth(3)
    
    black = MCTS(clobber, Piece.BLACK, simulations=500)

    while not clobber.game_over:
        if clobber.current_turn == Piece.WHITE:
            move = white.get_best_move()
        else:
            move = black.get_best_move()

        if move is None:
            print("Brak legalnych ruchów!")
            break

        clobber.make_move(move)
        clobber.print_board()
        print(f"Ruch: {move.start} -> {move.end}")

    winner = "BLACK" if clobber.current_turn == Piece.WHITE else "WHITE"
    print(f"The winner is: {winner}")

