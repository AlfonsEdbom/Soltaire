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
