"""GUI Interface for Solitaire game using PyQt6."""

import sys
from pathlib import Path

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QAction, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from soltaire.card import Card
from soltaire.core import Game


class CardWidget(QLabel):
    """Widget representing a playing card."""

    def __init__(self, card: Card, parent=None):
        super().__init__(parent)
        self.card = card
        self.load_image()

    def load_image(self):
        """Load the card's image."""
        # Assuming card images are named like "1_hearts.png", "13_spades.png" etc.
        image_path = (
            Path(__file__).parent.parent.parent
            / "cards"
            / f"{self.card.number}_{self.card.suit.lower()}.png"
        )
        pixmap = QPixmap(str(image_path))
        self.setPixmap(pixmap.scaled(QSize(71, 96), Qt.AspectRatioMode.KeepAspectRatio))

    def mousePressEvent(self, event):
        """Handle mouse press for drag and drop."""
        if event.button() == Qt.MouseButton.LeftButton:
            # TODO: Implement proper drag and drop
            pass


class SolitaireGUI(QMainWindow):
    """Main window for Solitaire game."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Solitaire")
        self.setMinimumSize(800, 600)

        # Initialize game logic (Model)
        self.game = Game()
        self.update_in_progress = (
            False  # Flag to prevent update loops        # Set up the UI
        )
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Top row: Foundations and Hand/Waste
        top_row = QHBoxLayout()

        # Foundation piles
        foundation_widget = QWidget()
        foundation_layout = QHBoxLayout(foundation_widget)
        for suit in ["Hearts", "Diamonds", "Clubs", "Spades"]:
            pile = QLabel("[ ]")  # Empty foundation pile
            foundation_layout.addWidget(pile)
        top_row.addWidget(foundation_widget)

        # Hand and Waste
        hand_waste = QWidget()
        hw_layout = QHBoxLayout(hand_waste)
        self.hand_widget = QPushButton("Hand")
        self.hand_widget.clicked.connect(self.handle_draw)
        self.waste_widget = QLabel("[ ]")
        hw_layout.addWidget(self.hand_widget)
        hw_layout.addWidget(self.waste_widget)
        top_row.addWidget(hand_waste)

        layout.addLayout(top_row)

        # Tableau
        tableau_widget = QWidget()
        tableau_layout = QHBoxLayout(tableau_widget)
        for i in range(7):
            pile = QLabel(f"Pile {i + 1}")
            tableau_layout.addWidget(pile)
        layout.addWidget(tableau_widget)

        # Menu bar
        self.setup_menu()

    def setup_menu(self):
        """Set up the menu bar."""
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        # Game menu
        game_menu = QMenu("&Game", self)
        menu_bar.addMenu(game_menu)

        # New game action
        new_game_action = QAction("&New Game", self)
        new_game_action.triggered.connect(self.new_game)
        game_menu.addAction(new_game_action)

        game_menu.addSeparator()

        # Quit action
        quit_action = QAction("&Quit", self)
        quit_action.triggered.connect(self.close)
        game_menu.addAction(quit_action)

    def handle_draw(self):
        """Handle drawing cards from hand to waste."""
        self.game.draw_cards()
        self.update_display()

    def new_game(self):
        """Start a new game."""
        self.game.initialize_game()
        self.update_display()

    def update_display(self):
        """Update all UI elements to match game state."""
        # Implementation needed
        pass


def main():
    """Entry point for the GUI version."""
    app = QApplication(sys.argv)
    window = SolitaireGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
