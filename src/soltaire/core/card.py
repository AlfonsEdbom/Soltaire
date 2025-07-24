"""Card class implementation."""


class Card:
    def __init__(self, number, suit):
        self.number = number
        self.suit = suit

        if self.number > 13:
            raise IndexError("Maximum number of card is 13")

        if self.suit not in ("Hearts", "Diamonds", "Clubs", "Spades"):
            raise TypeError(
                "Suit must be of type: 'Hearts', 'Diamonds', 'Clubs, 'Spades'"
            )

    def __str__(self):
        face_cards = {1: "Ace", 11: "Jack", 12: "Queen", 13: "King"}
        card_value = face_cards.get(self.number, str(self.number))
        return f"{card_value} of {self.suit}"

    def __eq__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        return self.number == other.number and self.suit == other.suit
