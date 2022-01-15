from Card import Card
import random
import pandas as pd


class Deck:
    def __init__(self):
        self.cards = []

    def create(self):
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
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
        for suit in ['Hearts', 'Diamonds', 'Clubs', 'Spades']:
            num_dict = {str(i):0 for i in range(2,11)}
            num_dict['Jack'] = 0
            num_dict['Queen'] = 0
            num_dict['King'] = 0
            num_dict['Ace'] = 0
            card_dict[suit] = num_dict

        for card in self.cards:
            card_list = str(card).split(' ')
            card_num = card_list[0]
            card_suit = card_list[-1]

            card_dict[card_suit][card_num] = 1

        df = pd.DataFrame(card_dict)
        return df

        #index = [i for i in range(1, 14)]
        #index[0] = 'Ace'
        #index[10] = 'Jack'
        #index[11] = 'Queen'
        #index[12] = 'King'



        #return df
    def __str__(self):
        return_string = "The deck contains these cards: \n"
        for card in self.cards:
            return_string += (f"{card} \n")
        return return_string


if __name__ == '__main__':
    my_deck = Deck()
    my_deck.create()

    my_deck.remove(Card(1, 'Hearts'))
    my_deck.view_cards()

    my_deck.shuffle()
    #my_deck.view_cards()
