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

        self.waste = Waste()
        self.foundations = Foundations()
        self.tableau = Tableau()
        self.tableau.initialize_from_deck(self.deck)
        self.hand = Hand(self.deck.cards.copy())
        self._no_progress = False  # True after a full draw cycle with no productive move

    def _mark_productive(self) -> None:
        """Reset stuck state after any progress-making move."""
        self._no_progress = False

    def draw_cards(self):
        """Draw cards from hand to waste."""
        cards = self.hand.draw_cards()
        if cards:
            self.waste.add_cards(cards)
            return True
        else:
            self._no_progress = True  # full cycle just completed
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
                self._mark_productive()
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
                self._mark_productive()
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
                self._mark_productive()
                return True
        except Exception:
            pass
        return False

    def move_foundation_to_tableau(self, suit: str, tableau_pile: int) -> bool:
        """Try to move the top card of a foundation pile to a tableau pile."""
        try:
            card = self.foundations.peek_top_card(suit)
            if card is None:
                return False
            if self.tableau.can_add_card_to_pile(card, tableau_pile):
                self.foundations.piles[suit].pop()
                self.tableau.add_card_to_pile(card, tableau_pile)
                return True
        except Exception:
            pass
        return False

    def move_tableau_to_tableau(self, from_pile: int, to_pile: int, count: int) -> bool:
        """Try to move cards between tableau piles."""
        try:
            pile = self.tableau.piles[from_pile]
            visible = pile.visible_cards
            would_reveal_hidden = pile.get_hidden_count() > 0 and count == len(visible)
            would_expose_foundation = (
                count < len(visible)
                and self.foundations.can_add_card(visible[-(count + 1)])
            )
            cards = self.tableau.get_cards_from_pile(from_pile, count)
            if self.tableau.can_add_cards_to_pile(cards, to_pile):
                self.tableau.add_cards_to_pile(cards, to_pile)
                self.tableau.remove_cards_from_pile(from_pile, count)
                if would_reveal_hidden or would_expose_foundation:
                    self._mark_productive()
                return True
        except Exception:
            pass
        return False

    def is_stuck(self) -> bool:
        """Return True if no progress-making action is available.

        "Progress" means: placing a card on the foundation, revealing a hidden
        tableau card, exposing a buried visible card that can go to the foundation,
        or playing the current waste card somewhere.  Pure visible-stack shuffling
        and empty draw cycles do not count.
        """
        # Any immediate foundation move?
        for pile in self.tableau.piles:
            if pile.visible_cards and self.foundations.can_add_card(pile.visible_cards[-1]):
                return False
        if self.waste.cards and self.foundations.can_add_card(self.waste.peek_top_card()):
            return False

        # Any tableau move that reveals a hidden card?
        for i, pile in enumerate(self.tableau.piles):
            if pile.hidden_cards and pile.visible_cards:
                for j in range(7):
                    if j != i and self.tableau.can_add_cards_to_pile(pile.visible_cards, j):
                        return False

        # Any tableau move that exposes a buried foundationable card?
        for i, pile in enumerate(self.tableau.piles):
            visible = pile.visible_cards
            for count in range(1, len(visible)):  # partial stack moves only
                new_top = visible[-(count + 1)]
                if self.foundations.can_add_card(new_top):
                    cards_to_move = visible[-count:]
                    for j in range(7):
                        if j != i and self.tableau.can_add_cards_to_pile(cards_to_move, j):
                            return False

        # Any waste card playable to tableau?
        if self.waste.cards:
            card = self.waste.peek_top_card()
            for i in range(7):
                if self.tableau.can_add_card_to_pile(card, i):
                    return False

        # Hand + waste empty → definitely stuck
        if not self.hand.cards and not self.waste.cards:
            return True

        # Grace period: waste was just recycled back to hand.
        # The new cycle hasn't been drawn yet, so we can't judge it yet.
        if not self.waste.cards:
            return False

        return self._no_progress

    def get_valid_actions(self) -> list[tuple]:
        """Return all currently valid actions as tuples.

        Action tuple formats:
            ("draw",)
            ("waste_to_foundation",)
            ("waste_to_tableau", pile)           # pile: 0-6
            ("tableau_to_foundation", pile)      # pile: 0-6
            ("tableau_to_tableau", from, to, count)
        """
        actions = []

        if self.hand.cards or self.waste.cards:
            actions.append(("draw",))

        if self.waste.cards:
            card = self.waste.peek_top_card()
            if self.foundations.can_add_card(card):
                actions.append(("waste_to_foundation",))
            for i in range(7):
                if self.tableau.can_add_card_to_pile(card, i):
                    actions.append(("waste_to_tableau", i))

        for from_pile in range(7):
            pile = self.tableau.piles[from_pile]
            visible = pile.get_visible_cards()
            if not visible:
                continue

            if self.foundations.can_add_card(visible[-1]):
                actions.append(("tableau_to_foundation", from_pile))

            for count in range(1, len(visible) + 1):
                cards = self.tableau.get_cards_from_pile(from_pile, count)
                for to_pile in range(7):
                    if to_pile == from_pile:
                        continue
                    if self.tableau.can_add_cards_to_pile(cards, to_pile):
                        actions.append(("tableau_to_tableau", from_pile, to_pile, count))

        return actions
