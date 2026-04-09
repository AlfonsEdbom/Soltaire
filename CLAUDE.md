# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Soltaire is a Python implementation of the classic Klondike Solitaire card game with two interfaces: a CLI and a PyQt6 GUI. The project uses a `src/` layout with the package `soltaire`.

## Commands

```bash
# Install dependencies (using uv)
uv sync

# Run CLI interface
uv run python -m soltaire.cli

# Run GUI interface
uv run python -m soltaire.gui

# Run all tests
uv run pytest

# Run a specific test file
uv run pytest tests/test_card.py

# Run a specific test
uv run pytest tests/test_card.py::test_card_creation
```

The `pyproject.toml` sets `pythonpath = "src"` for pytest, so imports work without installing the package.

## Architecture

The codebase is split into four layers:

### Core (`src/soltaire/core/`)
The game model, fully independent of any UI:

- **`card.py`** — `Card(number, suit)`: suits are `"Hearts"`, `"Diamonds"`, `"Clubs"`, `"Spades"`; numbers 1–13 (1=Ace, 13=King)
- **`deck.py`** — `Deck`: creates and shuffles 52 cards; uses `pandas` for `view_cards()` display
- **`game_rules.py`** — Pure functions for move validation (`is_valid_tableau_move`, `is_valid_foundation_move`, etc.)
- **`foundations.py`** — `Foundations`: four suit piles (Ace → King); uses `game_rules` for validation
- **`hand.py`** — `Hand`: the draw pile; draws 3 cards at a time
- **`waste.py`** — `Waste`: cards drawn from hand; top card is playable
- **`tableau.py`** — `TableauPile` and `Tableau`: 7 piles with hidden/visible card tracking; Kings can start empty piles
- **`game_logic.py`** — `Game`: orchestrates all components; the single entry point for game actions. `get_valid_actions()` returns all currently valid moves as a list of action tuples — the bridge used by `cli/cli.py` (hint command) and the `env/` and `agents/` layers

### Interfaces
- **`cli/cli.py`** — `SolitaireCLI`: rich-formatted game loop. Accepts an optional `Game` for testing. Commands:
  - `d` — draw 3 cards
  - `wf` — waste → foundation
  - `wt N` — waste → tableau pile N (1–7)
  - `tf N` — tableau pile N → foundation
  - `tt F T C` — move C cards from tableau pile F to pile T
  - `n` — new game, `q` — quit
  - Commands are always shown on screen; there is no separate help command
- **`gui/gui.py`** — `SolitaireGUI` (PyQt6 `QMainWindow`): window, menu bar (New Game / Quit), and draw button are functional. Card rendering uses `QSvgRenderer` with htdebeer/SVG-cards (`src/soltaire/gui/cards.svg`). `update_display()` is a stub (`pass`) — the board does not yet reflect game state. Drag-and-drop is not implemented.

### AI Environment (`src/soltaire/env/`) — skeleton
- **`solitaire_env.py`** — `KlondikeEnv` (Gymnasium-compatible skeleton). Will wrap `Game` with `reset()` / `step(action)` / observation and action spaces. `Game.get_valid_actions()` is complete; this class can now be written.

### AI Agents (`src/soltaire/agents/`) — skeleton
- **`base.py`** — `BaseAgent`: abstract class with `act(obs) -> int` and `reset()`
- **`random_agent.py`** — `RandomAgent` stub: picks a random valid action each step
- **`greedy_agent.py`** — `GreedyAgent` stub: scores actions by heuristic (prefer foundation moves, expose hidden cards)

## Implementation Status

### Complete
- `src/soltaire/core/` — all seven modules fully implemented
- `src/soltaire/core/game_logic.py` — `Game` class including `get_valid_actions()`
- `src/soltaire/cli/cli.py` — fully playable; uses `get_valid_actions()` for the `h` hint command
- `src/soltaire/agents/base.py` — `BaseAgent` ABC

### Stubs / work in progress
- `src/soltaire/gui/gui.py` — SVG card rendering implemented; `update_display()` is a stub so the board does not change during play; drag-and-drop not implemented
- `src/soltaire/env/solitaire_env.py` — docstring + reward schema only; class body is a single TODO
- `src/soltaire/agents/random_agent.py` — docstring only; class body is a single TODO
- `src/soltaire/agents/greedy_agent.py` — heuristic priority list documented; class body is a single TODO

### Card rendering
Cards are rendered from `src/soltaire/gui/cards.svg` ([htdebeer/SVG-cards](https://github.com/htdebeer/SVG-cards), LGPL) via PyQt6's built-in `QSvgRenderer`. One renderer instance is shared across all `CardWidget` instances. Element IDs follow the pattern `{suit}_{rank}` (e.g. `heart_1`, `spade_king`). Face-down cards use element ID `back`. No PNG files are required.

## Key Design Decisions
- `Game` in `game_logic.py` is the only class that should be instantiated by UI or agent code — it holds all game state
- `game_rules.py` functions are shared by both `Foundations` and `Tableau` to avoid duplicated logic (though `TableauPile.can_add_card` currently duplicates some of this inline)
- The `Hand` receives a copy of the deck's cards after the `Tableau` has popped its cards from the deck
- Tableau pile indices are 0-based internally; the CLI displays them as 1-based
- `SolitaireCLI` accepts an optional injected `Game` instance to make `parse_and_execute()` testable without running the full game loop
