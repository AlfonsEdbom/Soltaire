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
