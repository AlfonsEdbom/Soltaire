"""GUI Interface for Solitaire game using PyQt6."""

import sys
from pathlib import Path
from typing import Optional, Tuple, Union

from PyQt6.QtCore import QRect, QRectF, QSize, Qt
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
CARD_OVERLAP = 30  # Pixels of vertical overlap for stacked cards in tableau

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

    def __init__(
        self,
        card: Card,
        renderer: QSvgRenderer,
        face_down: bool = False,
        location: Optional[Tuple[str, ...]] = None,
        parent=None,
    ):
        """Initialize a card widget.

        Args:
            card: The Card object to display
            renderer: QSvgRenderer for the card deck SVG
            face_down: If True, show card back instead of face
            location: Tuple identifying card location (e.g., ("tableau", pile_idx, card_idx))
        """
        super().__init__(parent)
        self.card = card
        self.face_down = face_down
        self.location = location
        self._renderer = renderer
        self._selected = False
        self._valid_target = False
        self._hint_source = False
        self._hint_target = False
        self._render()
        self.setFixedSize(CARD_W, CARD_H)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def _element_id(self) -> str:
        if self.face_down:
            return "back"
        return f"{_SUIT_TO_SVG[self.card.suit]}_{_NUM_TO_SVG[self.card.number]}"

    def _render(self) -> None:
        pixmap = QPixmap(CARD_W, CARD_H)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        self._renderer.render(painter, self._element_id(), QRectF(0, 0, CARD_W, CARD_H))
        painter.end()
        self.setPixmap(pixmap)

    def set_selected(self, selected: bool) -> None:
        """Set the selection state and update visual feedback."""
        self._selected = selected
        self._update_style()

    def set_valid_target(self, valid: bool) -> None:
        """Mark card as a valid target for the selected card."""
        self._valid_target = valid
        self._update_style()

    def set_hint_source(self, hint: bool) -> None:
        """Mark card as a hint move source."""
        self._hint_source = hint
        self._update_style()

    def set_hint_target(self, hint: bool) -> None:
        """Mark card as a hint move target."""
        self._hint_target = hint
        self._update_style()

    def _update_style(self) -> None:
        """Update the visual style based on selection/hint state."""
        if self._selected:
            self.setStyleSheet(
                "QLabel { border: 4px solid lime; border-radius: 3px; }"
            )
        elif self._valid_target:
            self.setStyleSheet(
                "QLabel { border: 3px dotted yellow; border-radius: 3px; }"
            )
        elif self._hint_source:
            self.setStyleSheet(
                "QLabel { border: 3px solid #4488ff; border-radius: 3px; }"
            )
        elif self._hint_target:
            self.setStyleSheet(
                "QLabel { border: 3px dotted orange; border-radius: 3px; }"
            )
        else:
            self.setStyleSheet("")

    def is_selected(self) -> bool:
        """Return whether this card is currently selected."""
        return self._selected

    def mousePressEvent(self, event):
        """Handle mouse press for selection."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Get the parent GUI to handle selection
            parent_gui = self._find_gui_parent()
            if parent_gui and self.location:
                parent_gui.handle_card_click(self.location, self.card)
            event.accept()

    def mouseDoubleClickEvent(self, event):
        """Handle double-click to auto-move to foundation."""
        if event.button() == Qt.MouseButton.LeftButton:
            parent_gui = self._find_gui_parent()
            if parent_gui:
                self._try_auto_move_to_foundation(parent_gui)
            event.accept()

    def _find_gui_parent(self) -> Optional['SolitaireGUI']:
        """Find the parent SolitaireGUI window."""
        widget = self.parent()
        while widget:
            if isinstance(widget, QMainWindow) or (hasattr(widget, 'game') and hasattr(widget, 'handle_draw')):
                return widget
            widget = widget.parent()
        return None

    def _try_auto_move_to_foundation(self, parent_gui: 'SolitaireGUI') -> None:
        """Try to auto-move this card with priority: foundation first, then tableau.
        
        Priority:
        1. source -> foundation (if card can go there)
        2. source -> first available tableau pile (if card can go there)
        """
        try:
            if not self.location:
                return
            
            source_type = self.location[0]
            
            # Priority 1: Try to move to foundation
            if parent_gui.game.foundations.can_add_card(self.card):
                if source_type == "waste":
                    parent_gui.game.move_waste_to_foundation()
                elif source_type == "tableau":
                    pile_idx = int(self.location[1])
                    parent_gui.game.move_tableau_to_foundation(pile_idx)
                parent_gui.clear_selection()
                parent_gui.update_display()
                return
            
            # Priority 2: Try to move to first available tableau pile
            for tableau_idx, tableau_pile in enumerate(parent_gui.game.tableau.piles):
                # Skip if source is also tableau (don't move to same pile)
                if source_type == "tableau" and tableau_idx == int(self.location[1]):
                    continue

                if tableau_pile.can_add_card(self.card):
                    if source_type == "waste":
                        parent_gui.game.move_waste_to_tableau(tableau_idx)
                    elif source_type == "tableau":
                        source_pile_idx = int(self.location[1])
                        card_idx = int(self.location[2])
                        source_pile_obj = parent_gui.game.tableau.piles[source_pile_idx]
                        hidden_count = len(source_pile_obj.hidden_cards)
                        if card_idx < hidden_count:
                            continue  # Can't move hidden cards
                        visible_index = card_idx - hidden_count
                        num_cards = len(source_pile_obj.visible_cards) - visible_index
                        parent_gui.game.move_tableau_to_tableau(source_pile_idx, tableau_idx, num_cards)
                    elif source_type == "foundation":
                        suit = self.location[1]
                        parent_gui.game.move_foundation_to_tableau(suit, tableau_idx)
                    parent_gui.clear_selection()
                    parent_gui.update_display()
                    return
            
        except Exception:
            pass  # Move not possible, silently fail


class TableauPileWidget(QWidget):
    """Custom widget for tableau piles that handles overlapping card layout."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cards = []  # List of CardWidget objects
        self.setContentsMargins(0, 0, 0, 0)

    def add_card(self, card_widget: CardWidget) -> None:
        """Add a card widget to the pile and reposition all cards."""
        card_widget.setParent(self)
        self.cards.append(card_widget)
        self._reposition_cards()

    def clear_cards(self) -> None:
        """Remove all card widgets."""
        for card in self.cards:
            card.deleteLater()
        self.cards.clear()

    def _reposition_cards(self) -> None:
        """Calculate and set absolute positions for all cards with overlap."""
        if not self.cards:
            return
        
        # Calculate total height needed
        total_height = CARD_H + (len(self.cards) - 1) * CARD_OVERLAP
        self.setMinimumHeight(total_height)
        
        # Position each card with overlap
        for idx, card in enumerate(self.cards):
            y_pos = idx * CARD_OVERLAP
            card.move(0, y_pos)
            card.show()

    def sizeHint(self):
        """Return the ideal size for this widget."""
        if not self.cards:
            return QSize(CARD_W, CARD_H)
        
        total_height = CARD_H + max(0, (len(self.cards) - 1) * CARD_OVERLAP)
        return QSize(CARD_W, total_height)

    def mousePressEvent(self, event):
        """Pass click events to child cards."""
        # Find which card was clicked
        for card in reversed(self.cards):  # Check from top to bottom
            if card.geometry().contains(event.pos()):
                card.mousePressEvent(event)
                return
        event.accept()

    def mouseDoubleClickEvent(self, event):
        """Pass double-click events to child cards."""
        for card in reversed(self.cards):
            if isinstance(card, CardWidget) and card.geometry().contains(event.pos()):
                card.mouseDoubleClickEvent(event)
                return
        event.accept()


class SolitaireGUI(QMainWindow):
    """Main window for Solitaire game."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Solitaire")
        self.setMinimumSize(900, 700)

        self.game = Game()

        svg_path = Path(__file__).parent / "cards.svg"
        self._renderer = QSvgRenderer(str(svg_path))

        # Store references to key layout containers for easy refresh
        self.foundation_layout = None
        self.waste_layout = None
        self.hand_button = None
        self.hand_label = None
        self.status_label = None
        self.tableau_piles = []  # List of widgets, one per tableau pile
        self.central_widget = None
        
        # Selection state tracking
        self.selected_card_location = None  # Which card is currently selected
        self.card_widgets = {}  # Map from location tuple to CardWidget
        self.valid_target_locations = set()  # Locations where selected card can move to

        # Hint state tracking
        self._hint_source_locations: set = set()
        self._hint_target_locations: set = set()
        self._hint_draw: bool = False
        self.help_button = None

        self.setup_ui()
        self.update_display()

    def setup_ui(self):
        """Set up the user interface."""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout(self.central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(10, 10, 10, 10)

        # **Status/Win message area**
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: green; font-weight: bold; font-size: 14px;")
        layout.addWidget(self.status_label)

        # Top row: Foundations and Hand/Waste
        top_row = QHBoxLayout()
        top_row.setSpacing(15)

        # Foundation piles (4 columns: Hearts, Diamonds, Clubs, Spades)
        foundation_widget = QWidget()
        self.foundation_layout = QHBoxLayout(foundation_widget)
        self.foundation_layout.setSpacing(10)
        # Placeholders will be filled in update_display()
        for _ in range(4):
            placeholder = QLabel()
            self.foundation_layout.addWidget(placeholder)
        top_row.addWidget(foundation_widget)

        # Hand and Waste
        hand_waste = QWidget()
        hw_layout = QHBoxLayout(hand_waste)
        hw_layout.setSpacing(5)

        self.hand_button = QPushButton("Draw")
        self.hand_button.clicked.connect(self.handle_draw)
        self.hand_label = QLabel("Hand: 0")
        self.waste_layout = QHBoxLayout()
        self.waste_layout.setSpacing(3)

        self.help_button = QPushButton("Help")
        self.help_button.clicked.connect(self.handle_help)

        hw_layout.addWidget(self.help_button)
        hw_layout.addWidget(self.hand_button)
        hw_layout.addWidget(self.hand_label)
        hw_layout.addSpacing(20)
        hw_layout.addLayout(self.waste_layout)
        hw_layout.addStretch()

        top_row.addWidget(hand_waste)

        layout.addLayout(top_row)

        # Tableau: 7 piles
        tableau_widget = QWidget()
        tableau_layout = QHBoxLayout(tableau_widget)
        tableau_layout.setSpacing(10)
        tableau_layout.setContentsMargins(0, 0, 0, 0)

        for i in range(7):
            pile_widget = TableauPileWidget()
            self.tableau_piles.append(pile_widget)
            tableau_layout.addWidget(pile_widget)

        layout.addWidget(tableau_widget, 1)

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
        """Handle drawing cards from hand to waste.
        
        If hand is empty, automatically recycle waste back to hand.
        """
        if self.game.hand.is_empty():
            # Auto-recycle waste when hand is empty
            recycled = self.game.waste.recycle_to_hand()
            self.game.hand.add_cards(recycled)
        
        # Draw 3 cards from hand to waste
        self.game.draw_cards()
        self.update_display()

    def new_game(self):
        """Start a new game."""
        self.game.initialize_game()
        self.update_display()

    def update_display(self):
        """Update all UI elements to match game state."""
        # Clear card widget cache and hint state for fresh build
        self.card_widgets.clear()
        self._hint_source_locations.clear()
        self._hint_target_locations.clear()
        self._hint_draw = False
        if self.hand_button:
            self.hand_button.setStyleSheet("")

        # Update foundations
        self._update_foundations()

        # Update waste and hand
        self._update_waste_and_hand()

        # Update tableau
        self._update_tableau()

        # Update draw button state
        self._update_draw_button()

        # Check game state (win / stuck)
        self._check_game_state()
    
    def _update_draw_button(self) -> None:
        """Update the draw button label and state."""
        if self.game.hand.is_empty():
            self.hand_button.setText("Recycle")
            self.hand_button.setToolTip("Click to recycle waste cards back to hand")
        else:
            self.hand_button.setText("Draw")
            self.hand_button.setToolTip(f"Click to draw {min(3, len(self.game.hand.cards))} cards")

    def _check_game_state(self) -> None:
        """Check win/stuck state and update the status label."""
        total_foundation_cards = sum(len(pile) for pile in self.game.foundations.piles.values())

        if total_foundation_cards == 52:
            self.status_label.setText("🎉 You Win! 🎉")
            self.status_label.setStyleSheet("color: green; font-weight: bold; font-size: 16px;")
        elif self.game.is_stuck():
            self.status_label.setText("No more productive moves available")
            self.status_label.setStyleSheet("color: orange; font-weight: bold; font-size: 14px;")
        else:
            self.status_label.setText("")

    def _clear_layout(self, layout: Union[QHBoxLayout, QVBoxLayout]) -> None:
        """Remove all widgets from a layout."""
        while layout.count() > 0:
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def _update_foundations(self) -> None:
        """Update the display of foundation piles."""
        self._clear_layout(self.foundation_layout)

        for suit in ["Hearts", "Diamonds", "Clubs", "Spades"]:
            pile = self.game.foundations.piles[suit]
            if pile:
                # Show the top card
                card_widget = CardWidget(
                    pile[-1], self._renderer, face_down=False, location=("foundation", suit)
                )
                self.card_widgets[("foundation", suit)] = card_widget
                self.foundation_layout.addWidget(card_widget)
            else:
                # Show empty placeholder, track it for highlighting
                empty = QLabel("[ ]")
                empty.setFixedSize(CARD_W, CARD_H)
                empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
                # Make it clickable to accept moves
                empty.mousePressEvent = lambda event, target_suit=suit: self.handle_card_click(("foundation", target_suit), None)
                empty.setCursor(Qt.CursorShape.PointingHandCursor)
                # Track this as a potential target location for foundation
                self.card_widgets[("foundation", suit)] = empty
                self.foundation_layout.addWidget(empty)

    def _update_waste_and_hand(self) -> None:
        """Update the display of waste pile and hand."""
        # Update hand count label
        hand_count = len(self.game.hand.cards)
        self.hand_label.setText(f"Hand: {hand_count}")

        # Update waste display
        self._clear_layout(self.waste_layout)

        visible_waste = self.game.waste.get_visible_cards()
        if visible_waste:
            for i, card in enumerate(visible_waste):
                card_widget = CardWidget(
                    card, self._renderer, face_down=False, location=("waste",)
                )
                self.card_widgets[("waste",)] = card_widget
                self.waste_layout.addWidget(card_widget)
        else:
            empty = QLabel("[ ]")
            empty.setFixedSize(CARD_W, CARD_H)
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.waste_layout.addWidget(empty)

    def _update_tableau(self) -> None:
        """Update the display of tableau piles."""
        for i, pile in enumerate(self.game.tableau.piles):
            pile_widget = self.tableau_piles[i]
            pile_widget.clear_cards()

            # Add hidden cards (face-down)
            for j, card in enumerate(pile.hidden_cards):
                card_widget = CardWidget(
                    card, self._renderer, face_down=True, location=("tableau", i, j)
                )
                self.card_widgets[("tableau", i, j)] = card_widget
                pile_widget.add_card(card_widget)

            # Add visible cards (face-up)
            for j, card in enumerate(pile.visible_cards):
                card_widget = CardWidget(
                    card, self._renderer, face_down=False, location=("tableau", i, len(pile.hidden_cards) + j)
                )
                self.card_widgets[("tableau", i, len(pile.hidden_cards) + j)] = card_widget
                pile_widget.add_card(card_widget)
            
            # If pile is empty, add a placeholder clickable widget
            if not pile.hidden_cards and not pile.visible_cards:
                empty = QLabel("[ ]")
                empty.setFixedSize(CARD_W, CARD_H)
                empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
                # Make it clickable - create a closure to capture i
                empty.mousePressEvent = lambda event, pile_idx=i: self.handle_card_click(("tableau", pile_idx, -1), None)
                empty.setCursor(Qt.CursorShape.PointingHandCursor)
                # Track this as a valid target location
                self.card_widgets[("tableau", i, -1)] = empty
                pile_widget.add_card(empty)

    def dragEnterEvent(self, event):
        """Not used in click-based model."""
        pass

    def dragMoveEvent(self, event):
        """Not used in click-based model."""
        pass

    def dragLeaveEvent(self, event):
        """Not used in click-based model."""
        pass

    def dropEvent(self, event):
        """Not used in click-based model."""
        pass

    def handle_card_click(self, card_location: Tuple, card) -> None:
        """Handle a card being clicked.

        If no card is selected, select this one.
        If a card is selected and this is a valid target, try to move.
        If a card is selected and this is the same card, deselect it.
        """
        # Any click clears hint highlights
        self._hint_source_locations.clear()
        self._hint_target_locations.clear()
        self._hint_draw = False

        # If clicking the same card, deselect it
        if self.selected_card_location == card_location:
            self.clear_selection()
            return
        
        # If no card is selected yet, select this one
        if self.selected_card_location is None:
            self.selected_card_location = card_location
            self._update_visual_feedback()
            return
        
        # A card is already selected - try to move it to target
        if self._try_move_selected_to_target(card_location):
            self.clear_selection()
            return
        
        # Move failed, but click on a different card - select the new one
        self.selected_card_location = card_location
        self._update_visual_feedback()

    def clear_selection(self) -> None:
        """Clear the current selection and update visuals."""
        self.selected_card_location = None
        self._update_visual_feedback()

    def _update_visual_feedback(self) -> None:
        """Update visual feedback for selected card, valid targets, and hints."""
        # Clear all previous highlights
        self.valid_target_locations.clear()
        if self.hand_button:
            self.hand_button.setStyleSheet("")
        for card_widget in self.card_widgets.values():
            if isinstance(card_widget, CardWidget):
                card_widget.set_selected(False)
                card_widget.set_valid_target(False)
                card_widget.set_hint_source(False)
                card_widget.set_hint_target(False)
            elif isinstance(card_widget, QLabel):
                card_widget.setStyleSheet("")
                card_widget.update()

        if self.selected_card_location:
            # Selection mode: highlight selected card and valid targets
            if self.selected_card_location in self.card_widgets:
                widget = self.card_widgets[self.selected_card_location]
                if isinstance(widget, CardWidget):
                    widget.set_selected(True)

            self._calculate_valid_targets()
            for target_loc in self.valid_target_locations:
                if target_loc in self.card_widgets:
                    widget = self.card_widgets[target_loc]
                    if isinstance(widget, CardWidget):
                        widget.set_valid_target(True)
                    elif isinstance(widget, QLabel):
                        widget.setStyleSheet(
                            "QLabel { border: 3px dotted yellow; border-radius: 3px; background-color: rgba(255, 255, 0, 50); }"
                        )
                        widget.update()
        else:
            # Hint mode: show all valid move sources (blue) and targets (orange)
            if self._hint_draw and self.hand_button:
                self.hand_button.setStyleSheet("QPushButton { border: 3px solid #4488ff; }")
            for loc in self._hint_source_locations:
                if loc not in self.card_widgets:
                    continue
                widget = self.card_widgets[loc]
                if isinstance(widget, CardWidget):
                    widget.set_hint_source(True)
                elif isinstance(widget, QLabel):
                    widget.setStyleSheet(
                        "QLabel { border: 3px solid #4488ff; border-radius: 3px; }"
                    )
                    widget.update()
            for loc in self._hint_target_locations:
                if loc not in self.card_widgets:
                    continue
                widget = self.card_widgets[loc]
                if isinstance(widget, CardWidget):
                    widget.set_hint_target(True)
                elif isinstance(widget, QLabel):
                    widget.setStyleSheet(
                        "QLabel { border: 3px dotted orange; border-radius: 3px; }"
                    )
                    widget.update()

    def _calculate_valid_targets(self) -> None:
        """Calculate which locations are valid targets for the selected card."""
        if not self.selected_card_location:
            return
        
        source = self.selected_card_location
        source_type = source[0]
        
        # Get the card(s) being moved
        try:
            if source_type == "foundation":
                suit = source[1]
                card = self.game.foundations.peek_top_card(suit)
                if card is None:
                    return
                for i, tableau_pile in enumerate(self.game.tableau.piles):
                    if tableau_pile.can_add_card(card):
                        if tableau_pile.visible_cards:
                            top_idx = len(tableau_pile.hidden_cards) + len(tableau_pile.visible_cards) - 1
                            self.valid_target_locations.add(("tableau", i, top_idx))
                        else:
                            self.valid_target_locations.add(("tableau", i, -1))
                return
            elif source_type == "waste":
                # Get the top card from waste
                try:
                    card = self.game.waste.peek_top_card()
                except IndexError:
                    return  # No cards in waste
            elif source_type == "tableau":
                source_pile = int(source[1])
                card_index = int(source[2])
                source_pile_obj = self.game.tableau.piles[source_pile]
                
                # Check if card is in hidden cards (can't move)
                if card_index < len(source_pile_obj.hidden_cards):
                    return
                
                # Get the actual card
                visible_index = card_index - len(source_pile_obj.hidden_cards)
                if visible_index >= len(source_pile_obj.visible_cards):
                    return
                card = source_pile_obj.visible_cards[visible_index]
            else:
                return
            
            if not card:
                return
            
            # Check tableau piles for valid targets
            for i, tableau_pile in enumerate(self.game.tableau.piles):
                # Skip if source is also tableau (don't show same pile as target)
                if source_type == "tableau" and int(source[1]) == i:
                    continue
                
                # Check if we can add this card to this pile
                if tableau_pile.can_add_card(card):
                    if tableau_pile.visible_cards:
                        # Target the top visible card
                        top_card_index = len(tableau_pile.hidden_cards) + len(tableau_pile.visible_cards) - 1
                        self.valid_target_locations.add(("tableau", i, top_card_index))
                    else:
                        # Empty tableau pile - use -1 as placeholder index
                        self.valid_target_locations.add(("tableau", i, -1))
            
            # Check foundation piles - if card can go to foundation, highlight only matching suit
            if self.game.foundations.can_add_card(card):
                # Only highlight the foundation with matching suit
                target_suit = card.suit
                self.valid_target_locations.add(("foundation", target_suit))
            
        except (IndexError, ValueError, AttributeError):
            # Invalid card location, no valid targets
            pass

    def _try_move_selected_to_target(self, target_location: Tuple) -> bool:
        """Try to move selected card to target location. Returns True if successful."""
        if not self.selected_card_location:
            return False
        
        source = self.selected_card_location
        source_type = source[0]
        target_type = target_location[0]
        
        try:
            # Waste to Tableau
            if source_type == "waste" and target_type == "tableau":
                target_pile = int(target_location[1])
                success = self.game.move_waste_to_tableau(target_pile)
            # Waste to Foundation (clicking foundation area)
            elif source_type == "waste" and target_type == "foundation":
                success = self.game.move_waste_to_foundation()
            # Tableau to Tableau - calculate how many cards to move
            elif source_type == "tableau" and target_type == "tableau":
                source_pile = int(source[1])
                target_pile = int(target_location[1])
                if source_pile != target_pile:
                    # Calculate how many cards to move from selected position to bottom
                    source_pile_obj = self.game.tableau.piles[source_pile]
                    selected_card_index = int(source[2])
                    hidden_count = len(source_pile_obj.hidden_cards)
                    
                    # If card index is in visible cards, calculate from there
                    if selected_card_index >= hidden_count:
                        visible_index = selected_card_index - hidden_count
                        num_cards_to_move = len(source_pile_obj.visible_cards) - visible_index
                    else:
                        # Can't move hidden cards individually
                        return False
                    
                    if num_cards_to_move > 0:
                        success = self.game.move_tableau_to_tableau(source_pile, target_pile, num_cards_to_move)
                    else:
                        return False
                else:
                    return False
            # Tableau to Foundation
            elif source_type == "tableau" and target_type == "foundation":
                source_pile = int(source[1])
                success = self.game.move_tableau_to_foundation(source_pile)
            # Foundation to Tableau
            elif source_type == "foundation" and target_type == "tableau":
                suit = source[1]
                target_pile = int(target_location[1])
                success = self.game.move_foundation_to_tableau(suit, target_pile)
            else:
                return False
            
            if success:
                self.update_display()
                return True
            return False
            
        except Exception as e:
            print(f"Move failed: {e}")
            return False

    def handle_help(self) -> None:
        """Highlight all valid moves: sources in blue, targets in orange."""
        self.clear_selection()
        self._hint_source_locations.clear()
        self._hint_target_locations.clear()
        self._hint_draw = False
        actions = self.game.get_valid_actions()
        self._translate_actions_to_hints(actions)
        self._update_visual_feedback()

    def _translate_actions_to_hints(self, actions: list) -> None:
        """Populate hint location sets from a list of valid action tuples."""
        for action in actions:
            kind = action[0]

            if kind == "draw":
                self._hint_draw = True

            elif kind == "waste_to_foundation":
                card = self.game.waste.peek_top_card()
                self._hint_source_locations.add(("waste",))
                self._hint_target_locations.add(("foundation", card.suit))

            elif kind == "waste_to_tableau":
                pile_idx = action[1]
                self._hint_source_locations.add(("waste",))
                pile = self.game.tableau.piles[pile_idx]
                if pile.visible_cards:
                    top_idx = len(pile.hidden_cards) + len(pile.visible_cards) - 1
                    self._hint_target_locations.add(("tableau", pile_idx, top_idx))
                else:
                    self._hint_target_locations.add(("tableau", pile_idx, -1))

            elif kind == "tableau_to_foundation":
                pile_idx = action[1]
                pile = self.game.tableau.piles[pile_idx]
                if pile.visible_cards:
                    src_idx = len(pile.hidden_cards) + len(pile.visible_cards) - 1
                    self._hint_source_locations.add(("tableau", pile_idx, src_idx))
                    self._hint_target_locations.add(("foundation", pile.visible_cards[-1].suit))

            elif kind == "tableau_to_tableau":
                from_pile, to_pile, count = action[1], action[2], action[3]
                src_pile = self.game.tableau.piles[from_pile]
                src_idx = len(src_pile.hidden_cards) + len(src_pile.visible_cards) - count
                self._hint_source_locations.add(("tableau", from_pile, src_idx))
                tgt_pile = self.game.tableau.piles[to_pile]
                if tgt_pile.visible_cards:
                    top_idx = len(tgt_pile.hidden_cards) + len(tgt_pile.visible_cards) - 1
                    self._hint_target_locations.add(("tableau", to_pile, top_idx))
                else:
                    self._hint_target_locations.add(("tableau", to_pile, -1))

    def _execute_card_move(self, source: Tuple, target: Tuple) -> bool:
        """Not used in click-based model."""
        pass


def main():
    """Entry point for the GUI version."""
    app = QApplication(sys.argv)
    window = SolitaireGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
