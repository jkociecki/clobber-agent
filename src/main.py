from clobber.clobber import Clobber
from clobber.clobber_strategy import NaiveStrategy
from agents.mcts import MCTS
from agents.minmax import MinMax
from general.enums import Piece
import os

def print_board(board, current_player):
    os.system("clear")  # dla Linux/macOS (czyści terminal)

    print(f"Current Player: {'BLACK' if current_player == Piece.BLACK else 'WHITE'}")
    print("    " + "  ".join(str(i) for i in range(len(board[0]))))  # kolumny
    print("   " + "---" * len(board[0]))

    for y, row in enumerate(board):
        line = f"{y} | "
        for piece in row:
            if piece == Piece.BLACK:
                line += f"\033[1;30mB\033[0m  "  # bold black
            elif piece == Piece.WHITE:
                line += f"\033[1;37mW\033[0m  "  # bold white
            else:
                line += ".  "
        print(line)
    print()

def main():
    game = Clobber(5, 5)

    # Utwórz agentów różnych typów
    black_agent = MinMax(depth=3, strategy=NaiveStrategy(), player=Piece.WHITE)
    white_agent = MCTS(player=Piece.BLACK, simulation_time=1.0)

    agents = {
        Piece.WHITE: black_agent,
        Piece.BLACK: white_agent
    }

    turn = 1
    print_board(game.board, game.current_player)

    while not game.is_terminal():
        agent = agents[game.current_player]
        move = agent.choose_move(game)

        if move is None:
            print("No legal moves left.")
            break

        # Dodaj informację o typie agenta
        agent_type = "MinMax" if isinstance(agent, MinMax) else "MCTS"
        print(f"Turn {turn}: Player {'BLACK' if game.current_player == Piece.BLACK else 'WHITE'} ({agent_type}) moves from {move.from_pos} to {move.to_pos}")
        
        game.make_move(move)

        print_board(game.board, game.current_player)
        input("Press Enter for next move...")
        turn += 1

    # Po zakończeniu gry – przeciwnik aktualnego gracza wygrywa
    winner = ~game.current_player
    winner_agent = "MinMax" if winner == Piece.WHITE else "MCTS"
    print(f"\n\033[1;32mGame Over! Winner: {'BLACK' if winner == Piece.BLACK else 'WHITE'} ({winner_agent}) 🎉\033[0m\n")





if __name__ == '__main__':
    main()
