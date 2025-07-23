"""Tests for Card class."""

import pytest

from soltaire.card import Card


def test_card_creation():
    card = Card(1, "Hearts")
    assert card.suit == "Hearts"
    assert card.number == 1

    card = Card(11, "Spades")
    assert card.suit == "Spades"
    assert card.number == 11

    card = Card(7, "Clubs")
    assert card.suit == "Clubs"
    assert card.number == 7


def test_card_invalid_number():
    with pytest.raises(IndexError):
        Card(14, "Hearts")


def test_card_invalid_suit():
    with pytest.raises(TypeError):
        Card(1, "Invalid")
