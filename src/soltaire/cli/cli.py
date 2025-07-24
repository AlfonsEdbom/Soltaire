"""Command Line Interface for Solitaire game."""

from soltaire.core.game_logic import Game


class SolitaireCLI:
    """Command Line Interface for playing Solitaire."""

    def __init__(self):
        """Initialize a new game."""
        self.game = Game()

    def display_game_state(self):
        """Display the current state of the game."""
        # Clear screen (you might want to use os.system('clear') on Unix or os.system('cls') on Windows)
        print("\n" * 50)

        # Display foundations
        print("Foundations:")
        print(self.game.foundations)
        print()

        # Display hand and waste
        print(f"Hand: {len(self.game.hand.cards)} cards")
        print(f"Waste: {self.game.waste}")
        print()

        # Display tableau with 1-based indices
        print("Tableau:")
        tableau = str(self.game.tableau).split("\n")
        # Add pile numbers at the start of each line
        numbered_tableau = []
        for i, line in enumerate(tableau):
            i += 1
            line = line.replace("Pile ", "").split(": ")[
                -1
            ]  # Remove any existing pile prefix
            numbered_tableau.append(f"Pile {i}: {line}")
        print("\n".join(numbered_tableau))

    def get_command(self) -> str:
        """Get a command from the user."""
        print("\nCommands:")
        print("  d - Draw cards from hand")
        print("  m - Move cards")
        print("  n - New game")
        print("  q - Quit game")
        return input("Enter command: ").lower().strip()

    def handle_draw(self):
        """Handle drawing cards from hand to waste."""
        self.game.draw_cards()

    def handle_move(self):
        """Handle moving cards between piles."""
        print("\nMove types:")
        print("  1. Waste to Foundation")
        print("  2. Waste to Tableau")
        print("  3. Tableau to Foundation")
        print("  4. Tableau to Tableau")

        move_type = input("Select move type (1-4): ")

        if move_type == "1":
            # Waste to Foundation
            if not self.game.waste.cards:
                print("No cards in waste!")
                return
            if self.game.move_waste_to_foundation():
                print("Card moved to foundation")
            else:
                print("Invalid move!")
        elif move_type == "2":
            # Waste to Tableau
            if not self.game.waste.cards:
                print("No cards in waste!")
                return
            pile = int(input("Enter tableau pile number (1-7): ")) - 1
            if self.game.move_waste_to_tableau(pile):
                print("Card moved to tableau")
            else:
                print("Invalid move!")
        elif move_type == "3":
            # Tableau to Foundation
            pile = int(input("Enter tableau pile number (1-7): ")) - 1
            if self.game.move_tableau_to_foundation(pile):
                print("Card moved to foundation")
            else:
                print("Invalid move!")
        elif move_type == "4":
            # Tableau to Tableau
            from_pile = int(input("Enter source tableau pile (1-7): ")) - 1
            to_pile = int(input("Enter destination tableau pile (1-7): ")) - 1
            count = int(input("Enter number of cards to move: "))
            if self.game.move_tableau_to_tableau(from_pile, to_pile, count):
                print("Cards moved successfully")
            else:
                print("Invalid move!")

    def run(self):
        """Main game loop."""
        while True:
            self.display_game_state()
            command = self.get_command()

            if command == "q":
                print("Thanks for playing!")
                break
            elif command == "d":
                self.handle_draw()
            elif command == "m":
                self.handle_move()
            elif command == "n":
                self.game.initialize_game()
                print("Starting new game...")
            else:
                print("Invalid command!")


def main():
    """Entry point for the CLI version."""
    game = SolitaireCLI()
    game.run()


if __name__ == "__main__":
    main()
