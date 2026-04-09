"""Command Line Interface for Solitaire game."""

from rich.console import Console

from soltaire.core.game_logic import Game

SUIT_SYMBOLS = {"Hearts": "♥", "Diamonds": "♦", "Clubs": "♣", "Spades": "♠"}
NUM_LABELS = {1: "A", 11: "J", 12: "Q", 13: "K"}
SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]
SLOT_WIDTH = 4


class SolitaireCLI:
    """Command Line Interface for playing Solitaire."""

    def __init__(self, game: Game | None = None):
        self.game = game or Game()
        self.moves = 0
        self.console = Console()
        self._skip_redraw = False
        self._stuck_warned = False

    def _card_label(self, card) -> str:
        """Plain text label for a card, e.g. 'A♥', '10♠'."""
        num = NUM_LABELS.get(card.number, str(card.number))
        return f"{num}{SUIT_SYMBOLS[card.suit]}"

    def _card_markup(self, card) -> str:
        """Rich markup for a card, red for Hearts/Diamonds, blue for Clubs/Spades."""
        label = self._card_label(card)
        if card.suit in ("Hearts", "Diamonds"):
            return f"[red]{label}[/red]"
        return f"[blue]{label}[/blue]"

    def _pad(self, markup: str, visible_width: int) -> str:
        """Pad a rich markup string to SLOT_WIDTH visible characters."""
        return markup + " " * (SLOT_WIDTH - visible_width)

    def display_game_state(self):
        """Render the full board to the terminal."""
        c = self.console
        c.clear()

        # Header
        c.print(f"[bold]Soltaire[/bold]   Moves: {self.moves}")
        c.print()

        # Foundations: show top card of each suit pile or "♥--" placeholder
        found_parts = []
        for suit in SUITS:
            sym = SUIT_SYMBOLS[suit]
            pile = self.game.foundations.piles[suit]
            if pile:
                found_parts.append(self._card_markup(pile[-1]))
            else:
                placeholder = f"{sym}--"
                if suit in ("Hearts", "Diamonds"):
                    found_parts.append(f"[red]{placeholder}[/red]")
                else:
                    found_parts.append(f"[blue]{placeholder}[/blue]")
        c.print("Foundations:  " + "   ".join(found_parts))
        c.print()

        # Hand & Waste
        hand_count = len(self.game.hand.cards)
        visible = self.game.waste.get_visible_cards()
        if visible:
            parts = []
            for cd in visible[:-1]:
                parts.append(f"[dim][{self._card_markup(cd)}][/dim]")
            parts.append(f"[{self._card_markup(visible[-1])}]")
            waste_str = " ".join(parts)
        else:
            waste_str = "(empty)"
        c.print(f"Hand: {hand_count} cards   Waste: {waste_str}")
        c.print()

        # Tableau column headers (1-based)
        sep = "  "
        header = sep.join(f" {i + 1}  " for i in range(7))
        c.print(f"  {header}")

        # Build column data as list of (markup, visible_width) per row
        columns = []
        for i in range(7):
            pile = self.game.tableau.piles[i]
            col = []
            for _ in range(pile.get_hidden_count()):
                col.append(("[dim][?][/dim]", 3))
            for card in pile.get_visible_cards():
                col.append((self._card_markup(card), len(self._card_label(card))))
            columns.append(col)

        max_height = max((len(col) for col in columns), default=0)
        for row_idx in range(max_height):
            slots = []
            for col in columns:
                if row_idx < len(col):
                    markup, vis_w = col[row_idx]
                    slots.append(self._pad(markup, vis_w))
                else:
                    slots.append(" " * SLOT_WIDTH)
            c.print("  " + sep.join(slots))

        c.print()

        # Always-visible command reference
        c.print("[bold]Commands:[/bold]")
        c.print("  [cyan]d[/cyan]            Draw 3 cards from hand")
        c.print("  [cyan]wf[/cyan]           Waste → Foundation")
        c.print("  [cyan]wt N[/cyan]         Waste → Tableau pile N  (1–7)")
        c.print("  [cyan]tf N[/cyan]         Tableau pile N → Foundation")
        c.print("  [cyan]tt F T C[/cyan]     Tableau pile F → pile T, move C cards")
        c.print("  [cyan]h[/cyan]            Show valid moves")
        c.print("  [cyan]n[/cyan]            New game")
        c.print("  [cyan]q[/cyan]            Quit")
        c.print()


    def _format_action(self, action: tuple) -> str:
        """Format an action tuple as a human-readable CLI command string."""
        kind = action[0]
        if kind == "draw":
            return "d  — draw cards"
        if kind == "waste_to_foundation":
            card = self.game.waste.peek_top_card()
            return f"wf  — waste ({self._card_label(card)}) → foundation"
        if kind == "waste_to_tableau":
            pile = action[1] + 1
            card = self.game.waste.peek_top_card()
            return f"wt {pile}  — waste ({self._card_label(card)}) → tableau pile {pile}"
        if kind == "tableau_to_foundation":
            pile = action[1] + 1
            card = self.game.tableau.piles[action[1]].get_visible_cards()[-1]
            return f"tf {pile}  — tableau pile {pile} ({self._card_label(card)}) → foundation"
        if kind == "tableau_to_tableau":
            from_p, to_p, count = action[1] + 1, action[2] + 1, action[3]
            card = self.game.tableau.get_cards_from_pile(action[1], count)[0]
            return f"tt {from_p} {to_p} {count}  — move {count} card(s) from pile {from_p} ({self._card_label(card)}) → pile {to_p}"
        return str(action)

    def _error(self, msg: str) -> None:
        """Print a yellow error message and suppress the next redraw."""
        self.console.print(f"[yellow]{msg}[/yellow]")
        self._skip_redraw = True

    def parse_and_execute(self, line: str) -> bool:
        """Parse and execute a command line. Returns False when the game should exit."""
        parts = line.strip().lower().split()
        if not parts:
            return True

        cmd = parts[0]

        if cmd == "q":
            self.console.print("Thanks for playing!")
            return False

        elif cmd == "d":
            self.game.draw_cards()
            self.moves += 1

        elif cmd == "wf":
            if not self.game.move_waste_to_foundation():
                self._error(f"Invalid move: {line.strip()}")
            else:
                self.moves += 1

        elif cmd == "wt":
            if len(parts) < 2:
                self._error("Usage: wt N  (N = pile 1–7)")
                return True
            if not self._validate_pile(parts[1]):
                return True
            pile = int(parts[1])
            if not self.game.move_waste_to_tableau(pile - 1):
                self._error(f"Invalid move: {line.strip()}")
            else:
                self.moves += 1

        elif cmd == "tf":
            if len(parts) < 2:
                self._error("Usage: tf N  (N = pile 1–7)")
                return True
            if not self._validate_pile(parts[1]):
                return True
            pile = int(parts[1])
            if not self.game.move_tableau_to_foundation(pile - 1):
                self._error(f"Invalid move: {line.strip()}")
            else:
                self.moves += 1

        elif cmd == "tt":
            if len(parts) < 4:
                self._error("Usage: tt F T C  (F=from, T=to, C=count)")
                return True
            if not self._validate_pile(parts[1]) or not self._validate_pile(parts[2]):
                return True
            try:
                count = int(parts[3])
            except ValueError:
                self._error("Count must be a number.")
                return True
            if count < 1:
                self._error("Count must be at least 1.")
                return True
            from_pile, to_pile = int(parts[1]), int(parts[2])
            if not self.game.move_tableau_to_tableau(from_pile - 1, to_pile - 1, count):
                self._error(f"Invalid move: {line.strip()}")
            else:
                self.moves += 1

        elif cmd == "h":
            actions = self.game.get_valid_actions()
            if not actions:
                self.console.print("[yellow]No valid moves available.[/yellow]")
            else:
                self.console.print(f"[bold]{len(actions)} valid move(s):[/bold]")
                for action in actions:
                    self.console.print(f"  [cyan]{self._format_action(action)}[/cyan]")
            self._skip_redraw = True

        elif cmd == "n":
            self.game.initialize_game()
            self.moves = 0
            self._stuck_warned = False
            self.console.print("New game started.")

        else:
            self._error(f"Unknown command '{cmd}'.")

        return True

    def _validate_pile(self, token: str) -> bool:
        """Check token is an int in 1–7; print error and return False if not."""
        try:
            n = int(token)
        except ValueError:
            self._error("Pile must be a number 1–7.")
            return False
        if not 1 <= n <= 7:
            self._error("Pile must be between 1 and 7.")
            return False
        return True

    def run(self):
        """Main game loop."""
        while True:
            if self._skip_redraw:
                self._skip_redraw = False
            else:
                self.display_game_state()
            try:
                line = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                self.console.print("\nThanks for playing!")
                break
            if not self.parse_and_execute(line):
                break
            if self.game.foundations.is_complete():
                self.display_game_state()
                self.console.print(
                    f"[bold green]Congratulations! You beat the game in {self.moves} moves![/bold green]"
                )
                try:
                    response = input("Play again? (y/n): ").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    break
                if response == "y":
                    self.game.initialize_game()
                    self.moves = 0
                    self._stuck_warned = False
                else:
                    break
            elif not self.game.get_valid_actions():
                self.display_game_state()
                self.console.print("[bold red]No valid moves remain. Starting new game...[/bold red]")
                try:
                    input("Press Enter to continue.")
                except (EOFError, KeyboardInterrupt):
                    break
                self.game.initialize_game()
                self.moves = 0
                self._stuck_warned = False
                continue
            elif self.game.is_stuck():
                if not self._stuck_warned:
                    self._stuck_warned = True
                    self.console.print(
                        "[yellow]Game appears stuck — no progress is possible. "
                        "Type [cyan]n[/cyan] to start a new game.[/yellow]"
                    )
                    self._skip_redraw = True
            else:
                self._stuck_warned = False


def main():
    """Entry point for the CLI version."""
    SolitaireCLI().run()


if __name__ == "__main__":
    main()
