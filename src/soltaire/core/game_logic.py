"""Core game logic for Solitaire."""

from .deck import Deck
from .foundations import Foundations
from .hand import Hand
from .tableau import Tableau
from .waste import Waste


class Game:
    """Core game logic, independent of any interface."""

    def __init__(self):
        self.initialize_game()

    def initialize_game(self):
        """Initialize or reset the game state."""
        self.deck = Deck()
        self.deck.create()
        self.deck.shuffle()

        self.hand = Hand(self.deck.cards.copy())
        self.waste = Waste()
        self.foundations = Foundations()
        self.tableau = Tableau()
        self.tableau.initialize_from_deck(self.deck)

    def draw_cards(self):
        """Draw cards from hand to waste."""
        cards = self.hand.draw_cards()
        if cards:
            self.waste.add_cards(cards)
            return True
        else:
            recycled = self.waste.recycle_to_hand()
            self.hand.add_cards(recycled)
            return False

    def can_move_to_foundation(self, card) -> bool:
        """Check if a card can be moved to its foundation."""
        return self.foundations.can_add_card(card)

    def move_waste_to_foundation(self) -> bool:
        """Try to move top waste card to foundation."""
        if not self.waste.cards:
            return False

        card = self.waste.peek_top_card()
        try:
            if self.foundations.can_add_card(card):
                self.foundations.add_card_to_foundation(card)
                self.waste.play_card()
                return True
        except Exception:
            pass
        return False

    def move_waste_to_tableau(self, tableau_pile: int) -> bool:
        """Try to move top waste card to tableau pile."""
        if not self.waste.cards:
            return False

        card = self.waste.peek_top_card()
        try:
            if self.tableau.can_add_card_to_pile(card, tableau_pile):
                self.tableau.add_card_to_pile(card, tableau_pile)
                self.waste.play_card()
                return True
        except Exception:
            pass
        return False

    def move_tableau_to_foundation(self, tableau_pile: int) -> bool:
        """Try to move top card from tableau to foundation."""
        try:
            card = self.tableau.get_top_card(tableau_pile)
            if self.foundations.can_add_card(card):
                self.foundations.add_card_to_foundation(card)
                self.tableau.remove_top_card(tableau_pile)
                return True
        except Exception:
            pass
        return False

    def move_tableau_to_tableau(self, from_pile: int, to_pile: int, count: int) -> bool:
        """Try to move cards between tableau piles."""
        try:
            cards = self.tableau.get_cards_from_pile(from_pile, count)
            if self.tableau.can_add_cards_to_pile(cards, to_pile):
                self.tableau.add_cards_to_pile(cards, to_pile)
                self.tableau.remove_cards_from_pile(from_pile, count)
                return True
        except Exception:
            pass
        return False
