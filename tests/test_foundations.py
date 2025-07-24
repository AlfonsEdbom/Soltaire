"""Tests for Foundations class."""

import pytest

from soltaire.card import Card
from soltaire.foundations import Foundations, InvalidFoundationMoveError


@pytest.fixture
def empty_foundations():
    """Create empty foundation piles."""
    return Foundations()


@pytest.fixture
def hearts_sequence():
    """Create a sequence of hearts cards."""
    return [Card(i, "Hearts") for i in range(1, 5)]  # Ace through 4


def test_foundations_initialization(empty_foundations):
    """Test that foundations are properly initialized."""
    assert all(len(pile) == 0 for pile in empty_foundations.piles.values())


def test_add_ace_to_empty(empty_foundations):
    """Test adding an Ace to an empty foundation pile."""
    ace_hearts = Card(1, "Hearts")
    empty_foundations.add_card_to_foundation(ace_hearts)
    assert empty_foundations.get_pile_height("Hearts") == 1


def test_cannot_add_non_ace_to_empty(empty_foundations):
    """Test that only Aces can be added to empty piles."""
    two_hearts = Card(2, "Hearts")
    with pytest.raises(InvalidFoundationMoveError):
        empty_foundations.add_card_to_foundation(two_hearts)


def test_build_sequence(empty_foundations, hearts_sequence):
    """Test building a sequence in a foundation pile."""
    for card in hearts_sequence:
        empty_foundations.add_card_to_foundation(card)

    assert empty_foundations.get_pile_height("Hearts") == 4
    assert empty_foundations.peek_top_card("Hearts") == hearts_sequence[-1]


def test_cannot_add_wrong_sequence(empty_foundations):
    """Test that cards must be added in sequence."""
    ace_hearts = Card(1, "Hearts")
    three_hearts = Card(3, "Hearts")  # Skipping 2

    empty_foundations.add_card_to_foundation(ace_hearts)
    with pytest.raises(InvalidFoundationMoveError):
        empty_foundations.add_card_to_foundation(three_hearts)


def test_cannot_add_wrong_suit(empty_foundations):
    """Test that cards must be added to their own suit pile."""
    ace_hearts = Card(1, "Hearts")
    two_spades = Card(2, "Spades")

    empty_foundations.add_card_to_foundation(ace_hearts)
    # Try to build on hearts with a spade
    with pytest.raises(InvalidFoundationMoveError):
        empty_foundations.add_card_to_foundation(two_spades)


def test_play_card_from_foundation(empty_foundations, hearts_sequence):
    """Test playing a card from a foundation pile to a valid target."""
    # Build up hearts foundation
    for card in hearts_sequence:  # Ace through 4
        empty_foundations.add_card_to_foundation(card)

    # Try to play 4 of Hearts onto 5 of Clubs (valid)
    target_card = Card(5, "Clubs")
    played = empty_foundations.play_card_from_foundation("Hearts", target_card)
    assert played == hearts_sequence[-1]  # Should be 4 of Hearts
    assert empty_foundations.get_pile_height("Hearts") == 3


def test_cannot_play_to_invalid_target(empty_foundations):
    """Test that playing to invalid targets raises an error."""
    # Add Ace of Hearts to foundation
    ace_hearts = Card(1, "Hearts")
    empty_foundations.add_card_to_foundation(ace_hearts)

    # Try to play onto another red card (invalid)
    target_card = Card(2, "Diamonds")
    with pytest.raises(InvalidFoundationMoveError):
        empty_foundations.play_card_from_foundation("Hearts", target_card)

    # Try to play onto wrong number (invalid)
    target_card = Card(3, "Clubs")
    with pytest.raises(InvalidFoundationMoveError):
        empty_foundations.play_card_from_foundation("Hearts", target_card)


def test_is_complete(empty_foundations):
    """Test checking if foundations are complete."""
    # Add all hearts from Ace to King
    for i in range(1, 14):
        empty_foundations.add_card_to_foundation(Card(i, "Hearts"))

    # Only one suit complete
    assert not empty_foundations.is_complete()

    # Complete all suits
    for suit in ["Diamonds", "Clubs", "Spades"]:
        for i in range(1, 14):
            empty_foundations.add_card_to_foundation(Card(i, suit))

    assert empty_foundations.is_complete()
