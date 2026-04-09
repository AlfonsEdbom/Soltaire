# Soltaire

A Python implementation of Klondike Solitaire with both a CLI and a PyQt6 GUI. The project serves as a platform to experiment with different AI approaches to solving the game.

## Prerequisites

[uv](https://docs.astral.sh/uv/getting-started/installation/) must be installed.

## Setup

```bash
git clone <repo-url>
cd Soltaire
uv sync
```

`uv sync` creates a `.venv` and installs all dependencies (including dev tools) from the lock file.

## Running

```bash
# CLI
uv run python -m soltaire.cli

# GUI
uv run python -m soltaire.gui
```

## Tests

```bash
uv run pytest
```

## Current Status

### Working now
- Full CLI game (`uv run python -m soltaire.cli`) — draw, all move types, hint (`h`), stuck detection, win detection
- All core game logic and move validation
- `Game.get_valid_actions()` — enumerates every legal move as a tuple
- GUI window opens; cards are rendered from SVG (htdebeer/SVG-cards)

### Planned / incomplete
- **GUI board** (`uv run python -m soltaire.gui`): window and SVG card rendering work, but
  `update_display()` is a stub — the board does not change during play. Next steps:
  1. Implement `update_display()` in `src/soltaire/gui/gui.py` to read from `self.game` and re-render all zones
  2. Replace static placeholder labels with `CardWidget(card, self._renderer)` per visible card
  3. Implement drag-and-drop via `QDrag` / `QDropEvent` on `CardWidget`
- **`KlondikeEnv`** (`src/soltaire/env/solitaire_env.py`): implement `reset()`, `step()`,
  observation encoding, and action space on top of `Game`. Reward schema is documented in the file.
- **`RandomAgent`** (`src/soltaire/agents/random_agent.py`): sample from valid actions via
  `game.get_valid_actions()`.
- **`GreedyAgent`** (`src/soltaire/agents/greedy_agent.py`): score valid actions by the priority
  list in the file's docstring.
- **DRL agent**: DQN or PPO via Stable-Baselines3, once `KlondikeEnv` is stable.

## AI Agents

The project is designed as a platform for experimenting with different AI approaches to solving Klondike Solitaire.

**Architecture:**
- `src/soltaire/env/` — Gymnasium-compatible training environment (skeleton — `Game.get_valid_actions()` is complete; env implementation is the next step)
- `src/soltaire/agents/` — Agent implementations (skeletons): `RandomAgent`, `GreedyAgent`

All agents implement `BaseAgent.act(obs) -> action` and run against `KlondikeEnv`, which wraps the `Game` class with a standard `reset()` / `step(action)` interface compatible with RL libraries such as Stable-Baselines3 and RLlib.

Planned agents: random baseline → greedy heuristic → deep reinforcement learning (DQN / PPO).
