"""Tests for game rules module."""

from soltaire.card import Card
from soltaire.game_rules import (
    is_ascending,
    is_descending,
    is_different_color,
    is_red_suit,
    is_valid_foundation_move,
    is_valid_tableau_move,
)


def test_is_red_suit():
    """Test red suit detection."""
    assert is_red_suit("Hearts") is True
    assert is_red_suit("Diamonds") is True
    assert is_red_suit("Clubs") is False
    assert is_red_suit("Spades") is False


def test_is_different_color():
    """Test color alternation between cards."""
    red_card = Card(5, "Hearts")
    black_card = Card(6, "Spades")
    another_red = Card(7, "Diamonds")

    # Different colors
    assert is_different_color(red_card, black_card) is True
    assert is_different_color(black_card, red_card) is True

    # Same color
    assert is_different_color(red_card, another_red) is False


def test_is_descending():
    """Test descending sequence validation."""
    card_8 = Card(8, "Hearts")
    card_7 = Card(7, "Spades")
    card_6 = Card(6, "Diamonds")

    # Valid descending
    assert is_descending(card_7, card_8) is True  # 7 on 8

    # Invalid descending
    assert is_descending(card_6, card_8) is False  # 6 on 8 (skips 7)
    assert is_descending(card_8, card_7) is False  # 8 on 7 (ascending)


def test_is_ascending():
    """Test ascending sequence validation."""
    ace = Card(1, "Hearts")
    two = Card(2, "Hearts")
    three = Card(3, "Hearts")

    # Valid ascending
    assert is_ascending(ace, two) is True  # 2 on Ace
    assert is_ascending(two, three) is True  # 3 on 2

    # Invalid ascending
    assert is_ascending(ace, three) is False  # 3 on Ace (skips 2)
    assert is_ascending(three, two) is False  # 2 on 3 (descending)


def test_is_valid_tableau_move():
    """Test complete tableau move validation."""
    black_8 = Card(8, "Spades")
    red_7 = Card(7, "Hearts")
    black_7 = Card(7, "Clubs")
    red_6 = Card(6, "Diamonds")

    # Valid moves: descending and alternating colors
    assert is_valid_tableau_move(red_7, black_8) is True
    assert is_valid_tableau_move(red_6, black_7) is True

    # Invalid moves
    assert is_valid_tableau_move(black_7, black_8) is False  # Same color
    assert is_valid_tableau_move(red_6, black_8) is False  # Not descending


def test_is_valid_foundation_move():
    """Test foundation move validation."""
    ace_hearts = Card(1, "Hearts")
    two_hearts = Card(2, "Hearts")
    three_hearts = Card(3, "Hearts")
    two_spades = Card(2, "Spades")

    # Starting foundation with Ace
    assert is_valid_foundation_move(ace_hearts, None) is True
    assert is_valid_foundation_move(two_hearts, None) is False

    # Building on existing cards
    assert is_valid_foundation_move(two_hearts, ace_hearts) is True
    assert is_valid_foundation_move(three_hearts, two_hearts) is True

    # Invalid moves
    assert is_valid_foundation_move(three_hearts, ace_hearts) is False  # Skip 2
    assert is_valid_foundation_move(two_spades, ace_hearts) is False  # Wrong suit
