"""Backward-compatible alias for the grid-based environment."""

from luthor.environment.gridworld import GridWorld

SimpleEnvironment = GridWorld

__all__ = ["SimpleEnvironment", "GridWorld"]
