# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Soltaire is a Python implementation of the classic Klondike Solitaire card game with two interfaces: a CLI and a PyQt6 GUI. The project uses a `src/` layout with the package `soltaire`.

## Commands

```bash
# Install dependencies (using uv)
uv sync

# Run CLI interface
python -m soltaire.cli

# Run GUI interface
python -m soltaire.gui

# Run all tests
pytest

# Run a specific test file
pytest tests/test_card.py

# Run a specific test
pytest tests/test_card.py::test_card_creation
```

The `pyproject.toml` sets `pythonpath = "src"` for pytest, so imports work without installing the package.

## Architecture

The codebase is split into three layers:

### Core (`src/soltaire/core/`)
The game model, fully independent of any UI:

- **`card.py`** — `Card(number, suit)`: suits are `"Hearts"`, `"Diamonds"`, `"Clubs"`, `"Spades"`; numbers 1–13 (1=Ace, 13=King)
- **`deck.py`** — `Deck`: creates and shuffles 52 cards; uses `pandas` for `view_cards()` display
- **`game_rules.py`** — Pure functions for move validation (`is_valid_tableau_move`, `is_valid_foundation_move`, etc.)
- **`foundations.py`** — `Foundations`: four suit piles (Ace → King); uses `game_rules` for validation
- **`hand.py`** — `Hand`: the draw pile; draws 3 cards at a time
- **`waste.py`** — `Waste`: cards drawn from hand; top card is playable
- **`tableau.py`** — `TableauPile` and `Tableau`: 7 piles with hidden/visible card tracking; Kings can start empty piles
- **`game_logic.py`** — `Game`: orchestrates all components; the single entry point for game actions

### Interfaces
- **`cli/cli.py`** — `SolitaireCLI`: text-based game loop with commands `d` (draw), `m` (move), `n` (new game), `q` (quit)
- **`gui/gui.py`** — `SolitaireGUI` (PyQt6 `QMainWindow`): card images loaded from `cards/{number}_{suit_lowercase}.png`; drag-and-drop not yet implemented

### Key Design Decisions
- `Game` in `game_logic.py` is the only class that should be instantiated by UI code — it holds all game state
- `game_rules.py` functions are shared by both `Foundations` and `Tableau` to avoid duplicated logic (though `TableauPile.can_add_card` currently duplicates some of this inline)
- The `Hand` receives a copy of the deck's cards after the `Tableau` has popped its cards from the deck
- Tableau pile indices are 0-based internally; the CLI displays them as 1-based
