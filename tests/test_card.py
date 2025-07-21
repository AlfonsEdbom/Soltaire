"""Tests for Card class."""

from soltaire.card import Card
import pytest


def test_card_creation():
    card = Card(1, 'Hearts')
    assert str(card) == "Ace of Hearts"
    
    card = Card(11, 'Spades')
    assert str(card) == "Jack of Spades"

def test_card_invalid_number():
    with pytest.raises(IndexError):
        Card(14, 'Hearts')

def test_card_invalid_suit():
    with pytest.raises(TypeError):
        Card(1, 'Invalid')
