"""Implementation of the Solitaire tableau piles."""

from soltaire.card import Card


class TableauPile:
    """Represents a single pile in the tableau.

    A tableau pile consists of face-down cards and face-up cards.
    Only the top card of the face-down pile can be flipped when the face-up pile is empty.
    """

    def __init__(self, initial_cards: list[Card]):
        self.visible_cards: list[Card] = []  # Cards that are face up
        self.hidden_cards: list[Card] = []  # Cards that are face down

        # Last card should be visible, rest hidden
        self.hidden_cards = initial_cards[:-1]

        if len(initial_cards) > 0:
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

        if not self.can_add_card(cards[0]):
            return False

        self.visible_cards.extend(cards)
        return True

    def remove_cards(self, count: int) -> list[Card]:
        """Remove the specified number of cards from the top of the visible pile."""
        if count > len(self.visible_cards):
            raise ValueError("Not enough visible cards to remove")

        removed_cards = self.visible_cards[-count:]
        self.visible_cards = self.visible_cards[:-count]

        # If we have no more visible cards but have hidden cards,
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
        visible = " ".join(str(card) for card in self.visible_cards)
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

    def can_move_cards(self, from_pile: int, to_pile: int, count: int) -> bool:
        """Check if cards can be moved between piles."""
        if not (0 <= from_pile < 7 and 0 <= to_pile < 7):
            return False

        source_pile = self.piles[from_pile]
        target_pile = self.piles[to_pile]

        if count > len(source_pile.visible_cards):
            return False

        cards_to_move = source_pile.visible_cards[-count:]
        return target_pile.can_add_card(cards_to_move[0])

    def move_cards(self, from_pile: int, to_pile: int, count: int) -> bool:
        """Move cards from one pile to another."""
        if not self.can_move_cards(from_pile, to_pile, count):
            return False

        cards = self.piles[from_pile].remove_cards(count)
        return self.piles[to_pile].add_cards(cards)

    def __str__(self) -> str:
        return "\n".join(f"Pile {i}: {pile}" for i, pile in enumerate(self.piles))
