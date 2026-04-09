"""Base class for all Soltaire agents."""

from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """Abstract base for agents that interact with KlondikeEnv.

    All agents follow the same loop::

        obs, info = env.reset()
        agent.reset()
        while not done:
            action = agent.act(obs)
            obs, reward, terminated, truncated, info = env.step(action)

    Concrete subclasses differ only in how they implement act().
    """

    @abstractmethod
    def act(self, obs) -> int:
        """Select an action given an observation from KlondikeEnv.

        Args:
            obs: observation returned by KlondikeEnv.reset() or .step()

        Returns:
            Integer action index into the environment's action space.
        """
        ...

    def reset(self) -> None:
        """Called at the start of each episode. Override if the agent has internal state."""
        pass
