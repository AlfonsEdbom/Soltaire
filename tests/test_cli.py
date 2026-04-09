"""Tests for the SolitaireCLI command parser."""

import pytest
from rich.console import Console

from soltaire.cli.cli import SolitaireCLI
from soltaire.core.card import Card
from soltaire.core.game_logic import Game


@pytest.fixture
def cli():
    """CLI with a fresh game and a quiet console (suppresses output in tests)."""
    game = Game()
    instance = SolitaireCLI(game=game)
    instance.console = Console(quiet=True)
    return instance


# ---------------------------------------------------------------------------
# Basic commands
# ---------------------------------------------------------------------------


def test_draw_command(cli):
    initial_hand = len(cli.game.hand.cards)
    result = cli.parse_and_execute("d")
    assert result is True
    assert len(cli.game.hand.cards) < initial_hand
    assert cli.moves == 1


def test_quit_command(cli):
    result = cli.parse_and_execute("q")
    assert result is False


def test_new_game_resets_moves(cli):
    cli.moves = 5
    cli.parse_and_execute("n")
    assert cli.moves == 0


def test_empty_input_returns_true(cli):
    assert cli.parse_and_execute("") is True
    assert cli.parse_and_execute("   ") is True


# ---------------------------------------------------------------------------
# Move commands — set up known game state before each test
# ---------------------------------------------------------------------------


def test_waste_to_foundation(cli):
    ace = Card(1, "Hearts")
    cli.game.waste.cards = [ace]
    cli.game.foundations.piles["Hearts"] = []

    result = cli.parse_and_execute("wf")
    assert result is True
    assert cli.moves == 1
    assert len(cli.game.foundations.piles["Hearts"]) == 1
    assert len(cli.game.waste.cards) == 0


def test_waste_to_foundation_invalid_when_waste_empty(cli):
    cli.game.waste.cards = []
    result = cli.parse_and_execute("wf")
    assert result is True
    assert cli.moves == 0


def test_waste_to_tableau(cli):
    # Place a red 7 on tableau pile 1 (index 0), put black 6 in waste
    seven = Card(7, "Hearts")
    six = Card(6, "Spades")
    cli.game.tableau.piles[0].visible_cards = [seven]
    cli.game.tableau.piles[0].hidden_cards = []
    cli.game.waste.cards = [six]

    result = cli.parse_and_execute("wt 1")
    assert result is True
    assert cli.moves == 1
    top = cli.game.tableau.piles[0].visible_cards[-1]
    assert top.number == 6 and top.suit == "Spades"
    assert len(cli.game.waste.cards) == 0


def test_tableau_to_foundation(cli):
    ace = Card(1, "Spades")
    cli.game.tableau.piles[0].visible_cards = [ace]
    cli.game.tableau.piles[0].hidden_cards = []
    cli.game.foundations.piles["Spades"] = []

    result = cli.parse_and_execute("tf 1")
    assert result is True
    assert cli.moves == 1
    assert len(cli.game.foundations.piles["Spades"]) == 1


def test_tableau_to_tableau(cli):
    # Place red 9 on pile 1 (index 0), black 10 on pile 2 (index 1)
    nine = Card(9, "Hearts")
    ten = Card(10, "Spades")
    cli.game.tableau.piles[0].visible_cards = [nine]
    cli.game.tableau.piles[0].hidden_cards = []
    cli.game.tableau.piles[1].visible_cards = [ten]
    cli.game.tableau.piles[1].hidden_cards = []

    result = cli.parse_and_execute("tt 1 2 1")
    assert result is True
    assert cli.moves == 1
    assert len(cli.game.tableau.piles[0].visible_cards) == 0
    top = cli.game.tableau.piles[1].visible_cards[-1]
    assert top.number == 9 and top.suit == "Hearts"


# ---------------------------------------------------------------------------
# Invalid input handling
# ---------------------------------------------------------------------------


def test_invalid_command_returns_true(cli):
    result = cli.parse_and_execute("xyz")
    assert result is True
    assert cli.moves == 0


def test_invalid_pile_number_out_of_range(cli):
    result = cli.parse_and_execute("wt 9")
    assert result is True
    assert cli.moves == 0


def test_invalid_pile_number_zero(cli):
    result = cli.parse_and_execute("tf 0")
    assert result is True
    assert cli.moves == 0


def test_invalid_pile_number_non_numeric(cli):
    result = cli.parse_and_execute("wt abc")
    assert result is True
    assert cli.moves == 0


def test_tt_missing_args(cli):
    result = cli.parse_and_execute("tt 1 2")
    assert result is True
    assert cli.moves == 0


def test_tt_invalid_count(cli):
    result = cli.parse_and_execute("tt 1 2 abc")
    assert result is True
    assert cli.moves == 0


# ---------------------------------------------------------------------------
# Win detection
# ---------------------------------------------------------------------------


def test_win_detection(cli):
    suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
    for suit in suits:
        cli.game.foundations.piles[suit] = [Card(n, suit) for n in range(1, 14)]

    assert cli.game.foundations.is_complete() is True
