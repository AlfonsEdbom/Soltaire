"""Tests for Hand and Waste classes."""

import pytest

from soltaire.card import Card
from soltaire.hand import Hand
from soltaire.waste import Waste


@pytest.fixture
def sample_cards():
    """Create a sample set of cards for testing."""
    return [
        Card(1, "Hearts"),
        Card(2, "Diamonds"),
        Card(3, "Clubs"),
        Card(4, "Spades"),
        Card(5, "Hearts"),
    ]


def test_hand_initialization(sample_cards):
    """Test hand initialization with cards."""
    hand = Hand(sample_cards)
    assert len(hand.cards) == 5


def test_hand_draw_cards(sample_cards):
    """Test drawing cards from hand."""
    hand = Hand(sample_cards)

    # Draw 3 cards
    drawn = hand.draw_cards()
    assert len(drawn) == 3
    assert len(hand.cards) == 2

    # Draw remaining cards (should only get 2)
    drawn = hand.draw_cards()
    assert len(drawn) == 2
    assert len(hand.cards) == 0

    # Try to draw from empty hand
    drawn = hand.draw_cards()
    assert len(drawn) == 0


def test_hand_waste_integration(sample_cards):
    """Test interaction between hand and waste."""
    hand = Hand(sample_cards)
    waste = Waste()

    # Draw cards from hand to waste
    drawn = hand.draw_cards()
    waste.add_cards(drawn)
    assert len(waste.cards) == 3
    assert len(hand.cards) == 2

    # Recycle waste to hand
    recycled = waste.recycle_to_hand()
    hand.add_cards(recycled)
    assert len(hand.cards) == 5
    assert len(waste.cards) == 0
