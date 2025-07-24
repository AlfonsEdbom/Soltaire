"""Implementation of the Solitaire foundations (the four suit piles)."""

from typing import Dict, Optional

from soltaire.card import Card
from soltaire.game_rules import (
    is_descending,
    is_different_color,
    is_valid_foundation_move,
)


class InvalidFoundationMoveError(Exception):
    """Raised when attempting an invalid move to a foundation pile."""

    def __init__(self, message: str = "Invalid move to foundation pile"):
        self.message = message
        super().__init__(self.message)


class Foundations:
    """Represents the four foundation piles in Solitaire.

    Each foundation starts empty, then builds up from Ace (1) to King (13)
    in the same suit.
    """

    def __init__(self):
        """Initialize empty foundation piles for each suit."""
        self.piles: Dict[str, list[Card]] = {
            "Hearts": [],
            "Diamonds": [],
            "Clubs": [],
            "Spades": [],
        }

    def can_add_card(self, card: Card) -> bool:
        """Check if a card can be added to its foundation pile.

        Rules:
        - If pile is empty, only an Ace can be played
        - Otherwise, card must be same suit and one number higher
        than the current top card
        """
        pile = self.piles[card.suit]
        top_card = pile[-1] if pile else None
        return is_valid_foundation_move(card, top_card)

    def add_card_to_foundation(self, card: Card) -> None:
        """Add a card to its foundation pile.

        Args:
            card: The card to add to its foundation pile.

        Raises:
            InvalidFoundationMoveError: If the move is not valid according to Solitaire rules.
        """
        if not self.can_add_card(card):
            raise InvalidFoundationMoveError(
                f"Cannot add {card} to {card.suit} foundation pile"
            )

        self.piles[card.suit].append(card)

    def peek_top_card(self, suit: str) -> Optional[Card]:
        """Look at the top card of a foundation pile without removing it.

        Args:
            suit: The suit of the foundation pile to check.

        Returns:
            The top card of the specified foundation pile, or None if empty.
        """
        pile = self.piles[suit]
        return pile[-1] if pile else None

    def get_pile_height(self, suit: str) -> int:
        """Get the number of cards in a foundation pile.

        Args:
            suit: The suit of the foundation pile to check.

        Returns:
            The number of cards in the specified foundation pile.
        """
        return len(self.piles[suit])

    def is_complete(self) -> bool:
        """Check if all foundation piles are complete (King on top).

        Returns:
            True if all piles have 13 cards (Ace through King).
        """
        return all(len(pile) == 13 for pile in self.piles.values())

    def can_play_from_foundation(self, suit: str, target_card: Card) -> bool:
        """Check if a card can be played from a foundation pile to a target card.

        In Solitaire, you can move cards back from foundations if:
        - The foundation pile is not empty
        - The target card is one rank higher
        - The target card is of the opposite color

        Args:
            suit: The suit of the foundation pile to check.
            target_card: The card you want to play onto.

        Returns:
            True if the move is legal.
        """
        if not self.piles[suit]:
            return False

        foundation_card = self.piles[suit][-1]
        return is_different_color(foundation_card, target_card) and is_descending(
            foundation_card, target_card
        )

    def play_card_from_foundation(self, suit: str, target_card: Card) -> Card:
        """Remove the top card from a foundation pile to play on a target card.

        Args:
            suit: The suit of the foundation pile to play from.
            target_card: The card you want to play onto.

        Returns:
            The played card.

        Raises:
            InvalidFoundationMoveError: If the pile is empty or the move is illegal.
        """
        if not self.piles[suit]:
            raise InvalidFoundationMoveError(
                f"Cannot play card from empty {suit} foundation pile"
            )

        if not self.can_play_from_foundation(suit, target_card):
            top_card = self.piles[suit][-1]
            raise InvalidFoundationMoveError(
                f"Cannot play {top_card} onto {target_card}"
            )

        return self.piles[suit].pop()

    def __str__(self) -> str:
        """Return a string representation of all foundation piles."""
        result = []
        for suit, pile in self.piles.items():
            if pile:
                result.append(f"{suit}: {str(pile[-1])}")
            else:
                result.append(f"{suit}: empty")
        return "\n".join(result)
