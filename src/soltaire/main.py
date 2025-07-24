"""Main entry point for Soltaire."""

from soltaire.core.deck import Deck


def main():
    my_deck = Deck()
    my_deck.create()
    current_cards = my_deck.view_cards()
    print(current_cards)


if __name__ == "__main__":
    main()
