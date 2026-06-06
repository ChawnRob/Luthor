import torch


class Planner:
    def __init__(self, world_model, action_dim, horizon, num_samples, cost_function):
        self.world_model = world_model
        self.action_dim = action_dim
        self.horizon = horizon
        self.num_samples = num_samples
        self.cost_function = cost_function

    def plan(self, current_observation, goal_observation, context=None):
        best_action_sequence = None
        min_total_cost = float("inf")
        all_imagined_trajectories = []

        current_latent_state = self.world_model.encode(current_observation, context=context)
        goal_latent_state = self.world_model.encode(goal_observation, context=context)

        for _ in range(self.num_samples):
            action_sequence = torch.rand(self.horizon, self.action_dim) * 2 - 1

            simulated_latent_state = current_latent_state
            current_trajectory = [simulated_latent_state]
            total_cost = 0

            for t in range(self.horizon):
                action = action_sequence[t]
                simulated_latent_state = self.world_model.predict(
                    simulated_latent_state,
                    action,
                    context=context,
                )
                current_trajectory.append(simulated_latent_state)
                total_cost += self.cost_function(simulated_latent_state, goal_latent_state)

            all_imagined_trajectories.append(current_trajectory)

            if total_cost < min_total_cost:
                min_total_cost = total_cost
                best_action_sequence = action_sequence

        return (
            best_action_sequence[0]
            if best_action_sequence is not None
            else torch.zeros(self.action_dim)
        ), all_imagined_trajectories
