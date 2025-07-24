"""Tests for Tableau and TableauPile classes."""

import pytest

from soltaire.core.card import Card
from soltaire.core.deck import Deck
from soltaire.core.tableau import Tableau, TableauPile


@pytest.fixture
def sample_cards():
    """Create a sample set of cards for testing."""
    return [
        Card(7, "Hearts"),  # Red 7
        Card(6, "Spades"),  # Black 6
        Card(5, "Diamonds"),  # Red 5
        Card(4, "Clubs"),  # Black 4
    ]


def test_tableau_pile_initialization():
    """Test TableauPile initialization with cards."""
    cards = [Card(7, "Hearts"), Card(6, "Spades"), Card(5, "Diamonds")]
    pile = TableauPile(cards)

    # Check that last card is visible and others are hidden
    assert len(pile.visible_cards) == 1
    assert len(pile.hidden_cards) == 2
    assert pile.visible_cards[0] == cards[-1]
    assert pile.hidden_cards == cards[:-1]


def test_tableau_pile_can_add_king_to_empty():
    """Test that only Kings can be added to empty piles."""
    pile = TableauPile([])
    king = Card(13, "Hearts")
    queen = Card(12, "Spades")

    assert pile.can_add_card(king) is True
    assert pile.can_add_card(queen) is False


def test_tableau_pile_alternating_colors():
    """Test that cards must alternate colors."""
    pile = TableauPile([Card(7, "Hearts")])  # Red 7

    black_6 = Card(6, "Spades")
    red_6 = Card(6, "Diamonds")

    assert pile.can_add_card(black_6) is True  # Red -> Black is valid
    assert pile.can_add_card(red_6) is False  # Red -> Red is invalid


def test_tableau_pile_descending_order():
    """Test that cards must be placed in descending order."""
    pile = TableauPile([Card(7, "Hearts")])  # Red 7

    black_6 = Card(6, "Spades")  # Valid: 7 -> 6
    black_8 = Card(8, "Spades")  # Invalid: 7 -> 8
    black_5 = Card(5, "Spades")  # Invalid: 7 -> 5 (must be 6)

    assert pile.can_add_card(black_6) is True
    assert pile.can_add_card(black_8) is False
    assert pile.can_add_card(black_5) is False


def test_tableau_pile_add_multiple_cards(sample_cards):
    """Test adding multiple cards at once."""
    pile = TableauPile([Card(8, "Clubs")])  # Black 8

    # Try to add [Red 7, Black 6, Red 5, Black 4]
    assert pile.add_cards(sample_cards) is True
    assert len(pile.visible_cards) == 5  # Original + 4 new cards


def test_tableau_pile_remove_cards(sample_cards):
    """Test removing cards from pile."""
    pile = TableauPile([Card(8, "Clubs")])  # Start with Black 8
    pile.add_cards(sample_cards)

    # Remove 3 cards from top
    removed = pile.remove_cards(3)
    assert len(removed) == 3
    assert len(pile.visible_cards) == 2
    assert removed == sample_cards[-3:]


def test_tableau_pile_flip_hidden_card():
    """Test that hidden card is flipped when visible pile is emptied."""
    cards = [Card(7, "Hearts"), Card(6, "Spades")]  # 7♥ hidden, 6♠ visible
    pile = TableauPile(cards)

    pile.remove_cards(1)  # Remove the visible 6♠
    assert len(pile.visible_cards) == 1  # 7♥ should now be visible
    assert len(pile.hidden_cards) == 0  # No more hidden cards
    assert pile.visible_cards[0] == cards[0]  # 7♥


def test_tableau_initialization():
    """Test tableau initialization with a deck."""
    deck = Deck()
    deck.create()
    tableau = Tableau()
    tableau.initialize_from_deck(deck)

    # Check that piles have correct number of cards
    for i in range(7):
        pile = tableau.piles[i]
        assert len(pile.hidden_cards) + len(pile.visible_cards) == i + 1
        assert len(pile.visible_cards) == 1
