from Card import Card
from Deck import Deck


def main():
    my_deck = Deck()
    my_deck.create()
    current_cards = my_deck.view_cards()
    print(current_cards)

if __name__ == '__main__':
    main()