"""Tests for Deck class."""

import pytest

from soltaire.card import Card
from soltaire.deck import Deck


@pytest.fixture
def empty_deck():
    """Create an empty deck for testing."""
    return Deck()


@pytest.fixture
def full_deck():
    """Create a complete deck of 52 cards."""
    deck = Deck()
    deck.create()
    return deck


def test_deck_creation(full_deck):
    """Test that deck is created with 52 cards."""
    assert len(full_deck.cards) == 52

    # Check that all combinations exist
    suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
    numbers = range(1, 14)

    for suit in suits:
        for number in numbers:
            # Find at least one card with this suit and number
            matching_cards = [
                card
                for card in full_deck.cards
                if card.suit == suit and card.number == number
            ]
            assert len(matching_cards) == 1


def test_deck_shuffling(full_deck):
    """Test that shuffling changes card order."""
    original_order = full_deck.cards.copy()
    full_deck.shuffle()

    # The shuffled deck should have the same cards but in different order
    assert len(full_deck.cards) == len(original_order)
    assert set(str(card) for card in full_deck.cards) == set(
        str(card) for card in original_order
    )

    # It's extremely unlikely that a shuffle would result in the same order
    # Note: This test could theoretically fail, but the probability is extremely low
    assert full_deck.cards != original_order


def test_deck_remove_card(full_deck):
    """Test removing a specific card from the deck."""
    card_to_remove = full_deck.cards[0]
    initial_count = len(full_deck.cards)

    full_deck.remove(card_to_remove)
    assert len(full_deck.cards) == initial_count - 1
    assert card_to_remove not in full_deck.cards


def test_remove_nonexistent_card(full_deck):
    """Test that removing a non-existent card raises an error."""
    # First remove an Ace of Hearts (assuming it exists)
    ace_hearts = Card(1, "Hearts")
    full_deck.remove(ace_hearts)

    # Try to remove it again - should raise error
    with pytest.raises(IndexError):
        full_deck.remove(ace_hearts)


def test_empty_deck_operations(empty_deck):
    """Test operations on an empty deck."""
    assert len(empty_deck.cards) == 0

    # Should be able to create a deck from empty
    empty_deck.create()
    assert len(empty_deck.cards) == 52

    # Should be able to shuffle an empty deck (no error)
    empty_deck.cards.clear()
    empty_deck.shuffle()
    assert len(empty_deck.cards) == 0


def test_unique_cards(full_deck):
    """Test that all cards in the deck are unique."""
    # Convert cards to strings for easier comparison
    card_strings = [str(card) for card in full_deck.cards]
    unique_cards = set(card_strings)

    assert len(card_strings) == len(unique_cards)
    assert len(unique_cards) == 52
