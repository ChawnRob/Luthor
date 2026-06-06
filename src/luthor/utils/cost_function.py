import torch


def euclidean_distance_cost(latent_state, goal_latent_state):
    return torch.norm(latent_state - goal_latent_state, p=2)


class CostFunction:
    """Default cost functions for latent-space planning."""

    euclidean = staticmethod(euclidean_distance_cost)
