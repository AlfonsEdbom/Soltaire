"""Implementation of the Solitaire waste pile."""

from soltaire.card import Card


class EmptyWasteError(Exception):
    """Raised when trying to play a card from an empty waste pile."""

    def __init__(self, message: str = "Cannot play card from empty waste pile"):
        self.message = message
        super().__init__(self.message)


class Waste:
    """Represents the waste pile in Solitaire.

    The waste pile contains cards that have been drawn from the hand
    and are available for play.
    """

    def __init__(self):
        """Initialize an empty waste pile."""
        self.cards: list[Card] = []

    def add_cards(self, cards: list[Card]) -> None:
        """Add cards to the waste pile (from hand)."""
        # New cards go on top (end) of the waste pile
        self.cards.extend(cards)

    def play_card(self) -> Card:
        """Take and remove the top card from the waste pile.

        Returns:
            Card: The top card from the waste pile.

        Raises:
            EmptyWasteError: If trying to play from an empty waste pile.
        """
        if not self.cards:
            raise EmptyWasteError()
        return self.cards.pop()

    def peek_top_card(self) -> Card:
        """Look at the top card without removing it."""
        return self.cards[-1]

    def recycle_to_hand(self) -> list[Card]:
        """Remove all cards to be recycled back to the hand."""
        cards = self.cards
        self.cards = []
        # Cards should be reversed when going back to hand
        # so they come out in the same order
        return cards[::-1]

    def get_visible_cards(self) -> list[Card]:
        """Get the visible cards in the waste pile.

        In Solitaire, typically the top 3 cards are visible,
        or all cards if fewer than 3 are present.
        """
        visible_count = min(3, len(self.cards))
        return self.cards[-visible_count:]

    def __str__(self) -> str:
        visible = self.get_visible_cards()
        return f"Waste: {' '.join(str(card) for card in visible)}"
