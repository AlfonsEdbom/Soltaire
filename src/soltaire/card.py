"""Card class implementation."""

class Card:
    def __init__(self, number, suit):
        self.number = number
        self.suit = suit

        if self.number > 13:
            raise IndexError("Maximum number of card is 13")

        if self.number == 1:
            self.number = 'Ace'

        if self.number == 11:
            self.number = 'Jack'

        if self.number == 12:
            self.number = 'Queen'

        if self.number == 13:
            self.number = 'King'

        if self.suit not in ('Hearts', 'Diamonds', 'Clubs', 'Spades'):
            raise TypeError("Suit must be of type: 'Hearts', 'Diamonds', 'Clubs, 'Spades'")
