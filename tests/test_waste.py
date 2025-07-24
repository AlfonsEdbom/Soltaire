"""Tests for Waste class."""

import pytest

from soltaire.card import Card
from soltaire.waste import EmptyWasteError, Waste


@pytest.fixture
def sample_cards():
    """Create a sample set of cards for testing."""
    return [
        Card(1, "Hearts"),
        Card(2, "Diamonds"),
        Card(3, "Clubs"),
        Card(4, "Spades"),
    ]


def test_waste_add_and_play():
    """Test adding and playing cards from waste."""
    waste = Waste()
    cards = [Card(1, "Hearts"), Card(2, "Diamonds"), Card(3, "Clubs")]

    # Add cards
    waste.add_cards(cards)
    assert len(waste.cards) == 3

    # Play top card
    played_card = waste.play_card()
    assert str(played_card) == str(cards[2])
    assert len(waste.cards) == 2

    # Peek at next card
    next_card = waste.peek_top_card()
    assert str(next_card) == str(cards[1])
    assert len(waste.cards) == 2  # Length shouldn't change


def test_waste_recycle():
    """Test recycling cards from waste to hand."""
    waste = Waste()
    cards = [Card(1, "Hearts"), Card(2, "Diamonds"), Card(3, "Clubs")]
    waste.add_cards(cards)

    # Recycle cards
    recycled = waste.recycle_to_hand()
    assert len(recycled) == 3
    assert len(waste.cards) == 0
    # Cards should be in reverse order
    assert str(recycled[0]) == str(cards[2])


def test_waste_visible_cards():
    """Test getting visible cards from waste."""
    waste = Waste()
    cards = [
        Card(1, "Hearts"),
        Card(2, "Diamonds"),
        Card(3, "Clubs"),
        Card(4, "Spades"),
    ]

    # Add 4 cards but only 3 should be visible
    waste.add_cards(cards)
    visible = waste.get_visible_cards()
    assert len(visible) == 3
    assert visible[0] == cards[1]  # Second card should be first visible
    assert visible[-1] == cards[-1]  # Last card should be last visible


def test_play_from_empty_waste():
    """Test playing card from empty waste pile raises an error."""
    waste = Waste()
    with pytest.raises(EmptyWasteError):
        waste.play_card()
