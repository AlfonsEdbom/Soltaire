"""Implementation of the Solitaire hand (draw pile)."""

from soltaire.card import Card


class Hand:
    """Represents the hand (draw pile) in Solitaire.

    The hand is where cards are drawn from. When the hand is empty,
    cards from the waste can be recycled back into the hand.
    """

    def __init__(self, cards: list[Card]):
        """Initialize the hand with a list of cards."""
        self.cards = cards

    def draw_cards(self, count: int = 3) -> list[Card]:
        """Draw up to count cards from the hand.

        Returns fewer than count cards if there aren't enough cards left.
        Returns an empty list if the hand is empty.
        """
        if not self.cards:
            return []

        # Draw up to count cards or all remaining cards
        num_cards = min(count, len(self.cards))
        drawn_cards = self.cards[-num_cards:]
        self.cards = self.cards[:-num_cards]

        return drawn_cards

    def add_cards(self, cards: list[Card]) -> None:
        """Add cards to the hand (used when recycling from waste)."""
        # In Solitaire, when recycling cards they go to the bottom of the hand
        self.cards = cards + self.cards

    def is_empty(self) -> bool:
        """Check if the hand is empty."""
        return len(self.cards) == 0

    def __str__(self) -> str:
        return f"Hand: {len(self.cards)} cards"
