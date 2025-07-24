"""Common rules and validations for Solitaire card movements."""

from soltaire.card import Card


def is_red_suit(suit: str) -> bool:
    """Check if a suit is red (Hearts or Diamonds).

    Args:
        suit: The suit to check.

    Returns:
        True if the suit is Hearts or Diamonds, False otherwise.
    """
    return suit in ["Hearts", "Diamonds"]


def is_different_color(card1: Card, card2: Card) -> bool:
    """Check if two cards are of different colors.

    In Solitaire, red suits (Hearts, Diamonds) must alternate with
    black suits (Clubs, Spades).

    Args:
        card1: First card to compare.
        card2: Second card to compare.

    Returns:
        True if the cards are of different colors.
    """
    return is_red_suit(card1.suit) != is_red_suit(card2.suit)


def is_descending(bottom_card: Card, top_card: Card) -> bool:
    """Check if cards form a descending sequence.

    In Solitaire tableau, cards must be placed in descending order
    (e.g., 7 on 8, 6 on 7, etc.).

    Args:
        bottom_card: The card being placed.
        top_card: The card being placed on.

    Returns:
        True if bottom_card is one less than top_card.
    """
    return bottom_card.number == top_card.number - 1


def is_ascending(bottom_card: Card, top_card: Card) -> bool:
    """Check if cards form an ascending sequence.

    In Solitaire foundations, cards must be placed in ascending order
    within the same suit (e.g., 2 on Ace, 3 on 2, etc.).

    Args:
        bottom_card: The card currently on top of the pile.
        top_card: The card being placed.

    Returns:
        True if top_card is one more than bottom_card.
    """
    return top_card.number == bottom_card.number + 1


def is_valid_tableau_move(moving_card: Card, target_card: Card) -> bool:
    """Check if a card can be played on a target card in the tableau.

    Valid moves in the tableau require:
    - Descending sequence (e.g., 7 on 8)
    - Alternating colors (red/black)

    Args:
        moving_card: The card being moved.
        target_card: The card being moved onto.

    Returns:
        True if the move is valid according to Solitaire rules.
    """
    return is_different_color(moving_card, target_card) and is_descending(
        moving_card, target_card
    )


def is_valid_foundation_move(
    moving_card: Card, foundation_card: Card | None = None
) -> bool:
    """Check if a card can be played to a foundation pile.

    Valid moves to foundations require:
    - If foundation is empty, card must be an Ace
    - If foundation has cards, new card must be:
        - Same suit as foundation
        - One rank higher than top card

    Args:
        moving_card: The card being moved to the foundation.
        foundation_card: The current top card of the foundation pile, or None if empty.

    Returns:
        True if the move is valid according to Solitaire rules.
    """
    if foundation_card is None:
        return moving_card.number == 1  # Only Aces can start foundations

    return moving_card.suit == foundation_card.suit and is_ascending(
        foundation_card, moving_card
    )
