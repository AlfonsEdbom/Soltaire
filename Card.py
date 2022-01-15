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

    def __eq__(self, other):
        return (self.number == other.number) and (self.suit == other.suit)

    def __str__(self):
        return f"{self.number} of {self.suit}"


if __name__ == '__main__':
    card1 = Card(2, 'Hearts')
    card2 = Card(1, 'Hearts')

    print(card1 == card2)