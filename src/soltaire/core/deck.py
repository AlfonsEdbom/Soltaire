"""Deck class implementation."""

import random

import pandas as pd

from .card import Card


class Deck:
    def __init__(self):
        self.cards = []

    def create(self):
        suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
        for i in range(1, 14):
            for suit in suits:
                self.cards.append(Card(i, suit))

    def remove(self, card_to_remove):
        if card_to_remove in self.cards:
            self.cards.remove(card_to_remove)
        else:
            raise IndexError("The card you are trying to remove does not exist")

    def shuffle(self):
        random.shuffle(self.cards)

    def view_cards(self):
        card_dict = {}
        for suit in ["Hearts", "Diamonds", "Clubs", "Spades"]:
            num_dict = {str(i): 0 for i in range(1, 14)}
            card_dict[suit] = num_dict

        for card in self.cards:
            # Access the card attributes directly instead of parsing the string
            card_num = str(card.number)  # Convert to string to match dictionary keys
            card_suit = card.suit

            # Update the count in the dictionary
            card_dict[card_suit][card_num] = 1

        df = pd.DataFrame(card_dict)
        return df

    def __str__(self):
        return_string = "The deck contains these cards: \n"
        for card in self.cards:
            return_string += f"{card} \n"
        return return_string
