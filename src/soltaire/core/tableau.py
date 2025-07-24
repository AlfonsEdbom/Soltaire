"""Implementation of the Solitaire tableau piles."""

from .card import Card


class TableauPile:
    """Represents a single pile in the tableau.

    A tableau pile consists of face-down cards and face-up cards.
    Only the top card of the face-down pile can be flipped when the face-up pile is empty.
    """

    def __init__(self, initial_cards: list[Card]):
        self.visible_cards: list[Card] = []  # Cards that are face up
        self.hidden_cards: list[Card] = []  # Cards that are face down

        # Last card should be visible, rest hidden
        if initial_cards:
            self.hidden_cards = initial_cards[:-1]
            self.visible_cards = [initial_cards[-1]]

    def can_add_card(self, card: Card) -> bool:
        """Check if a card can be added to this pile.

        In Solitaire, cards must be placed in alternating colors and descending order.
        A King can be placed on an empty pile.
        """
        if not self.visible_cards:
            # Only Kings (13) can be placed on empty piles
            return card.number == 13

        top_card = self.visible_cards[-1]

        # Check for alternating colors (Hearts/Diamonds are red, Clubs/Spades are black)
        def is_red_suit(suit: str) -> bool:
            return suit in ["Hearts", "Diamonds"]

        is_different_color = is_red_suit(card.suit) != is_red_suit(top_card.suit)

        # Check for descending order
        is_descending = card.number == top_card.number - 1

        return is_different_color and is_descending

    def add_cards(self, cards: list[Card]) -> bool:
        """Add one or more cards to the visible pile."""
        if not cards:
            return False

        # For multiple cards, only need to check the bottom card
        if not self.can_add_card(cards[0]):
            return False

        self.visible_cards.extend(cards)
        return True

    def get_top_card(self) -> Card:
        """Get the top card without removing it."""
        if not self.visible_cards:
            if not self.hidden_cards:
                raise ValueError("No cards in pile")
            # Flip the top hidden card
            self.visible_cards.append(self.hidden_cards.pop())

        return self.visible_cards[-1]

    def remove_top_card(self) -> Card:
        """Remove and return the top card."""
        if not self.visible_cards:
            if not self.hidden_cards:
                raise ValueError("No cards in pile")
            # Flip the top hidden card
            self.visible_cards.append(self.hidden_cards.pop())

        card = self.visible_cards.pop()

        # If we removed all visible cards and have hidden cards,
        # flip the next one
        if not self.visible_cards and self.hidden_cards:
            self.visible_cards.append(self.hidden_cards.pop())

        return card

    def remove_cards(self, count: int) -> list[Card]:
        """Remove and return multiple cards from the top."""
        if count > len(self.visible_cards):
            raise ValueError("Not enough visible cards")

        removed_cards = self.visible_cards[-count:]
        self.visible_cards = self.visible_cards[:-count]

        # If we removed all visible cards and have hidden cards,
        # flip the top hidden card
        if not self.visible_cards and self.hidden_cards:
            self.visible_cards.append(self.hidden_cards.pop())

        return removed_cards

    def get_visible_cards(self) -> list[Card]:
        """Return the visible cards in this pile."""
        return self.visible_cards.copy()

    def get_hidden_count(self) -> int:
        """Return the number of hidden cards."""
        return len(self.hidden_cards)

    def __str__(self) -> str:
        hidden = f"[{len(self.hidden_cards)} hidden]" if self.hidden_cards else "[]"
        visible = ", ".join(str(card) for card in self.visible_cards)
        return f"{hidden} {visible}"


class Tableau:
    """Manages all seven piles in the Solitaire tableau."""

    def __init__(self):
        # Initialize Tableau with 7 empty piles
        self.piles: list[TableauPile] = [TableauPile([]) for _ in range(7)]

    def initialize_from_deck(self, deck) -> None:
        """Set up the initial tableau from a deck of cards.

        In Solitaire, the first pile gets 1 card, second gets 2, etc.
        The top card of each pile is face up.
        """
        for i in range(7):
            # Take i + 1 cards for pile i
            cards_for_pile = [deck.cards.pop() for _ in range(i + 1)]
            self.piles[i] = TableauPile(cards_for_pile)

    def get_top_card(self, pile_index: int) -> Card:
        """Get the top card from a tableau pile."""
        if not (0 <= pile_index < 7):
            raise ValueError("Invalid pile index")
        return self.piles[pile_index].get_top_card()

    def remove_top_card(self, pile_index: int) -> Card:
        """Remove and return the top card from a tableau pile."""
        if not (0 <= pile_index < 7):
            raise ValueError("Invalid pile index")
        return self.piles[pile_index].remove_top_card()

    def get_cards_from_pile(self, pile_index: int, count: int) -> list[Card]:
        """Get cards from a tableau pile without removing them."""
        if not (0 <= pile_index < 7):
            raise ValueError("Invalid pile index")
        pile = self.piles[pile_index]
        if count > len(pile.visible_cards):
            raise ValueError("Not enough visible cards in pile")
        return pile.visible_cards[-count:].copy()

    def remove_cards_from_pile(self, pile_index: int, count: int) -> list[Card]:
        """Remove and return cards from a tableau pile."""
        if not (0 <= pile_index < 7):
            raise ValueError("Invalid pile index")
        pile = self.piles[pile_index]
        if count > len(pile.visible_cards):
            raise ValueError("Not enough visible cards in pile")
        return [pile.remove_top_card() for _ in range(count)]

    def can_add_card_to_pile(self, card: Card, pile_index: int) -> bool:
        """Check if a card can be added to a tableau pile."""
        if not (0 <= pile_index < 7):
            return False
        return self.piles[pile_index].can_add_card(card)

    def add_card_to_pile(self, card: Card, pile_index: int) -> bool:
        """Add a card to a tableau pile."""
        if not (0 <= pile_index < 7):
            return False
        return self.piles[pile_index].add_cards([card])

    def can_add_cards_to_pile(self, cards: list[Card], pile_index: int) -> bool:
        """Check if cards can be added to a tableau pile."""
        if not cards or not (0 <= pile_index < 7):
            return False
        return self.piles[pile_index].can_add_card(cards[0])

    def add_cards_to_pile(self, cards: list[Card], pile_index: int) -> bool:
        """Add cards to a tableau pile."""
        if not (0 <= pile_index < 7):
            return False
        return self.piles[pile_index].add_cards(cards)

    def __str__(self) -> str:
        return "\n".join(f"Pile {i}: {pile}" for i, pile in enumerate(self.piles))
