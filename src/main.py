from src.clobber import Clobber
from src.general.enums import Piece
from src.general.move import Move
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich import box

console = Console()


def draw_board(game: Clobber):
    table = Table(title=f"Clobber - Current Player: {'⚫' if game.current_player == Piece.BLACK else '⚪'}",
                  box=box.SQUARE)

    for x in range(game.width):
        table.add_column(str(x), justify="center")

    for y, row in enumerate(game.board):
        row_display = []
        for piece in row:
            if piece == Piece.WHITE:
                row_display.append("⚪")
            elif piece == Piece.BLACK:
                row_display.append("⚫")
            else:
                row_display.append("·")
        table.add_row(*row_display, end_section=False)

    console.clear()
    console.print(table)


def main():
    game = Clobber(5, 5)

    while True:
        draw_board(game)

        if game.is_terminal():
            winner = "⚫" if game.current_player == Piece.WHITE else "⚪"
            console.print(f"[bold green]Gra zakończona! Zwycięzca: {winner}[/bold green]")
            break

        console.print("[cyan]Podaj ruch: najpierw skąd, potem dokąd (format: x y)[/cyan]")

        try:
            fx, fy = map(int, Prompt.ask("Z").split())
            tx, ty = map(int, Prompt.ask("Do").split())

            move = Move(from_pos=(fx, fy), to_pos=(tx, ty))
            print(game.get_legal_moves())
            print(move)
            if move in game.get_legal_moves():
                game.make_move(move)
            else:
                console.print("[red]Nieprawidłowy ruch![/red]")
        except Exception as e:
            console.print(f"[red]Błąd wejścia: {e}[/red]")


if __name__ == '__main__':
    main()
