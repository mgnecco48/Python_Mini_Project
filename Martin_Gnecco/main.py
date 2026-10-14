from random import randint
import numpy as np
from time import sleep
from rich.console import Console
from rich.table import Table
from rich.align import Align
from rich.live import Live
from rich.spinner import Spinner
from typing import Literal


class Board:
    def __init__(self, size: int = 3) -> None:
        self.size = size
        self.squares = np.full((self.size, self.size), "-", dtype=object)
        self.empty = []

    def show_possibilities(self) -> list[tuple[int, int]]:
        self.empty = []
        for row in range(self.size):
            for col in range(self.size):
                if self.squares[row, col] == "-":
                    self.empty.append((row, col))
        return self.empty

    def check_row(self, symbol) -> bool:
        for row in self.squares:
            if np.all(row == symbol):
                return True
        return False

    def check_col(self, symbol) -> bool:
        for col in range(self.size):
            if all(row[col] == symbol for row in self.squares):
                return True
        return False

    def check_diag(self, symbol) -> bool:
        diag1 = []
        for i, row in enumerate(self.squares):
            diag1.append(row[i])

        if all(square == symbol for square in diag1):
            return True

        diag2 = []
        for i, row in enumerate(self.squares):
            diag2.append(row[-(i + 1)])

        if all(square == symbol for square in diag2):
            return True

        return False

    def check_winner(self, symbol) -> bool:
        return (
            self.check_row(symbol) or self.check_col(symbol) or self.check_diag(symbol)
        )

    def reset(self) -> None:
        self.empty = []
        self.squares = np.full((self.size, self.size), "-", dtype=object)

    def __str__(self) -> str:
        def style(value):
            if value == "X":
                return "[bold yellow]X[/bold yellow]"
            if value == "O":
                return "[bold cyan]O[/bold cyan]"
            return " "

        rows = []

        for row in self.squares:
            values = [style(value) for value in row]
            rows.append(f"│  {values[0]}  │  {values[1]}  │  {values[2]}  │")

        return (
            "┌─────┬─────┬─────┐\n"
            f"{rows[0]}\n"
            "├─────┼─────┼─────┤\n"
            f"{rows[1]}\n"
            "├─────┼─────┼─────┤\n"
            f"{rows[2]}\n"
            "└─────┴─────┴─────┘"
        )


class Player:
    def __init__(self, symbol: str, name: str) -> None:
        self.symbol = symbol
        self.points = 0
        self.name = name

    def play_turn(self, board: Board) -> None:
        posibilities = board.show_possibilities()
        if not posibilities:
            return
        coord = posibilities[randint(0, len(posibilities) - 1)]
        x, y = coord
        board.squares[x][y] = self.symbol

    def add_point(self) -> None:
        self.points += 1


class Game:
    def __init__(
        self,
        board: Board,
        player1: Player,
        player2: Player,
        console: Console,
        max_points: int = 5,
        max_rounds: int = 10,
        game_mode: Literal["interactive", "auto"] = "auto",
    ) -> None:
        self.board = board
        self.players = [player1, player2]
        self.console = console
        self.max_points = max_points
        self.max_rounds = max_rounds
        self.rounds_played = 0
        self.game_mode = "auto"

    # Helpers to manage the rendering:
    def enter_full_screen(self):
        print("\033[?1049h\033[H", end="", flush=True)

    def leave_full_screen(self):
        print("\033[?1049l", end="", flush=True)

    def printc(self, text: str | Board = ""):
        self.console.print(str(text), justify="center", markup=True)

    def line(self, color="default"):
        self.console.print("─" * 40, justify="center", style=color)

    def top_padding(self, panel_height):
        terminal_height = self.console.size.height
        padding = (terminal_height - panel_height) // 2
        print("\n" * padding)

    # -----

    def play_round(self) -> None:
        while self.board.show_possibilities():
            for player in self.players:
                self.console.clear()
                round_header = f"Round {self.rounds_played + 1}/{self.max_rounds}"
                self.top_padding(21)
                self.line()
                self.printc(f"[bold]{round_header}[/bold]")
                self.printc(f"{player.name}")
                self.line()
                player.play_turn(self.board)
                self.console.print()
                self.printc(self.board)
                self.console.print()

                if self.board.check_winner(player.symbol):
                    message = f"ROUND WINNER: {player.name}"
                    self.line("green bold")
                    self.console.print("\n")
                    self.printc(f"[bold]{message}[/bold]")
                    self.console.print("\n")
                    self.line("green bold")
                    player.add_point()
                    sleep(2.5)
                    return

                if not self.board.show_possibilities():
                    self.line("yellow bold")
                    self.console.print("\n")
                    self.printc("[bold]WE HAVE A TIE !!![/bold]")
                    self.console.print("\n")
                    self.line("yellow bold")
                    sleep(2.5)
                    return

                self.line()
                self.console.print(self.leaderboard(), justify="center")
                self.line()

                sleep(1)

    def check_player_points(self) -> int:
        return max(player.points for player in self.players)

    def leaderboard(self) -> Table:
        player1 = self.players[0]
        player2 = self.players[1]
        leaderboard = Table(title="Score")
        leaderboard.add_column(player1.name, style="bold yellow", justify="center")
        leaderboard.add_column(player2.name, style="bold cyan", justify="center")
        leaderboard.add_row(
            str(player1.points),
            str(player2.points),
        )

        return leaderboard

    def game_over_reason(self) -> str:
        if self.rounds_played == self.max_rounds:
            message = f"[bold]{'You reached the max rounds limit!'}[/bold]\n"
        elif self.check_player_points() == self.max_points:
            message = f"[bold]{'Maximum number of points reached!!'}[/bold]\n"
        else:
            return "Something weird happened"

        return message

    def get_winner(self) -> int:
        player1 = self.players[0]
        player2 = self.players[1]
        if player1.points > player2.points:
            return 0
        elif player2.points > player1.points:
            return 1
        else:
            return 2

    def winner_message(self) -> str:
        winner = self.get_winner()
        if winner != 2:
            message = f"{self.players[winner].name} won!!"
        else:
            message = "There was no winner!!"
        return f"{message}"

    def play_game(self) -> None:
        self.enter_full_screen()
        self.console.clear()
        self.top_padding(1)
        spinner = Spinner("dots", text="[bold]Starting game...[/bold]")
        with Live(
            Align.center(spinner),
            console=self.console,
            refresh_per_second=12.5,
            transient=True,
        ):
            sleep(2.5)

        self.console.clear()
        self.top_padding(3)
        self.line()
        self.printc(f"[bold]{'Welcome!!!'}[/bold]")
        self.console.print(":rocket:", justify="center", emoji=True)
        self.line()
        sleep(2)

        self.console.clear()
        self.top_padding(21)
        self.line()
        self.printc(f"[bold]{'Ready??'}[/bold]")
        self.console.print(":question:", justify="center", emoji=True)
        self.line()
        self.console.print()
        self.line()
        self.console.print()
        self.printc(self.board)
        self.console.print()
        self.line()
        self.console.print("Have Fun !!!", justify="center", style="bold magenta")
        self.line()
        sleep(2)

        while (
            self.rounds_played < self.max_rounds
            and self.check_player_points() < self.max_points
        ):
            self.play_round()
            self.rounds_played += 1
            self.board.reset()

        self.console.clear()
        self.top_padding(17)
        self.line()
        self.printc(f"{'End of the game'}")
        self.line()
        self.printc()
        self.printc()
        self.printc(self.game_over_reason())
        self.printc()
        self.console.print(self.leaderboard(), justify="center")
        self.printc()
        self.line()
        self.printc(self.winner_message())
        self.line()
        sleep(5)
        self.leave_full_screen()


def main():
    board = Board()
    console = Console()
    player1 = Player("X", "[yellow bold]Martin[/yellow bold]")
    player2 = Player("O", "[cyan bold]Lucas[/cyan bold]")
    game = Game(board, player1, player2, console)
    game.play_game()


if __name__ == "__main__":
    main()
