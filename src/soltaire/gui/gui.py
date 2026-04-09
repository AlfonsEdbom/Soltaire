"""GUI Interface for Solitaire game using PyQt6."""

import sys
from pathlib import Path

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QAction, QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer
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

from soltaire.core.card import Card
from soltaire.core.game_logic import Game

CARD_W, CARD_H = 71, 96

_SUIT_TO_SVG = {
    "Hearts": "heart",
    "Diamonds": "diamond",
    "Clubs": "club",
    "Spades": "spade",
}
_NUM_TO_SVG = {
    1: "1", 2: "2", 3: "3", 4: "4", 5: "5",
    6: "6", 7: "7", 8: "8", 9: "9", 10: "10",
    11: "jack", 12: "queen", 13: "king",
}


class CardWidget(QLabel):
    """Widget representing a playing card, rendered from an SVG deck."""

    def __init__(self, card: Card, renderer: QSvgRenderer, parent=None):
        super().__init__(parent)
        self.card = card
        self._render(renderer)

    def _element_id(self) -> str:
        return f"{_SUIT_TO_SVG[self.card.suit]}_{_NUM_TO_SVG[self.card.number]}"

    def _render(self, renderer: QSvgRenderer) -> None:
        pixmap = QPixmap(CARD_W, CARD_H)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter, self._element_id(), QRectF(0, 0, CARD_W, CARD_H))
        painter.end()
        self.setPixmap(pixmap)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # TODO: Implement drag-and-drop.
            # Approach: create a QDrag with QMimeData encoding the source pile index
            # and card position. The drop target calls the appropriate game.move_*
            # method then triggers update_display().
            pass


class SolitaireGUI(QMainWindow):
    """Main window for Solitaire game."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Solitaire")
        self.setMinimumSize(800, 600)

        self.game = Game()
        self.update_in_progress = False

        svg_path = Path(__file__).parent / "cards.svg"
        self._renderer = QSvgRenderer(str(svg_path))

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
            pile = QLabel("[ ]")  # TODO: replace with CardWidget or empty-pile placeholder; populate in update_display()
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
            pile = QLabel(f"Pile {i + 1}")  # TODO: replace with stacked column of CardWidgets; populate in update_display()
            tableau_layout.addWidget(pile)
        layout.addWidget(tableau_widget)

        # Menu bar
        self.setup_menu()

    def setup_menu(self):
        """Set up the menu bar."""
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        game_menu = QMenu("&Game", self)
        menu_bar.addMenu(game_menu)

        new_game_action = QAction("&New Game", self)
        new_game_action.triggered.connect(self.new_game)
        game_menu.addAction(new_game_action)

        game_menu.addSeparator()

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
        # TODO: Implement full board refresh:
        #   1. Clear placeholder labels from foundation and tableau layouts.
        #   2. For each foundation suit, show top card or empty placeholder.
        #   3. For waste, show top 1–3 visible cards.
        #   4. For each tableau pile, render hidden_count face-down placeholders
        #      (use self._renderer.render(painter, "back", rect)) + one CardWidget
        #      per visible card (partially overlapping).
        #   5. Update hand button label with remaining card count.
        #   Game API (all readable, no side effects):
        #     self.game.foundations.piles, self.game.waste.cards,
        #     self.game.tableau.piles[i].visible_cards,
        #     self.game.tableau.piles[i].hidden_cards, self.game.hand.cards
        #   Create CardWidget instances as: CardWidget(card, self._renderer)
        pass


def main():
    """Entry point for the GUI version."""
    app = QApplication(sys.argv)
    window = SolitaireGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
