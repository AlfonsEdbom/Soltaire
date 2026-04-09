"""Agent that scores valid actions by heuristics and picks the best each step.

Planned heuristics (highest priority first):

    1. Move any card to a foundation pile — always preferred.
    2. Move that exposes a hidden card — increases information and options.
    3. Move a King to an empty pile, but only if it uncovers a hidden card.
    4. Any other valid tableau-to-tableau move.
    5. Draw from hand if no better action is available.
"""

# TODO: implement GreedyAgent(BaseAgent)
