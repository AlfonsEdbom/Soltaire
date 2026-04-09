"""Agent that selects a random valid action each step.

Useful as a baseline to compare other agents against.

Implementation notes:
    - Call env.action_space.sample() to get a random action index.
    - Filter to valid actions using Game.get_valid_actions() to avoid
      wasting steps on illegal moves.

Game.get_valid_actions() is implemented. Straightforward implementation:
    - Call env.unwrapped.game.get_valid_actions() to get valid action tuples.
    - Map tuples to integer indices; use random.choice() to pick one.
    - This guarantees every submitted action is valid.
"""

# TODO: implement RandomAgent(BaseAgent)
