import pandas as pd

cards = []
suits = ['hearts', 'clubs', 'spades', 'diamonds']
for suit in suits:
    for i in range(1, 13):
        cards.append(f"{i} of {suit}")


card_dict = {}
for suit in suits:
    num_dict = {str(i): 0 for i in range(1,13)}
    for i in range(1,13):
        num_dict[str(i)] = 0

    card_dict[suit] = num_dict
#print(card_dict)


heart_dict = {}
diamond_dict = {}
club_dict = {}
spade_dict = {}
my_dict = {heart_dict, diamond_dict, club_dict, spade_dict}
print(my_dict)
for card in cards:
    card_list = str(card).split(' ')
    card_num = card_list[0]
    card_suit = card_list[-1]
    if card_suit == 'hearts':
        heart_dict[card_num] = 1
        print(f"Adding {card_num} of {card_suit}")

    #my_dict[card_suit] = 1
    #my_dict[card_suit][card_num] = 1
    #print(my_dict)
#print(my_dict)

#df = pd.DataFrame(card_dict)
#print(df)

def test():
    hearts_list = []
    clubs_list = []
    spades_list = []
    diamonds_list = []

    for card in cards:
        card_suit = card.split(' ')[-1]
        if card_suit == 'hearts':
            hearts_list.append(card)
        if card_suit == 'clubs':
            clubs_list.append(card)
        if card_suit == 'spades':
            spades_list.append(card)
        if card_suit == 'diamonds':
            diamonds_list.append(card)

    df = pd.DataFrame(list(zip(hearts_list, clubs_list, spades_list, diamonds_list)),
                      columns=['Hearts', 'Clubs', 'Spades', 'Diamonds'])
    print(df)

