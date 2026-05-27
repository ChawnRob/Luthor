import matplotlib.pyplot as plt
import torch

class Visualizer:
    def __init__(self, goal):
        self.goal = goal
        self.history = []
        self.imagined_trajectories = []

    def add_real_step(self, pos):
        self.history.append(pos.tolist())

    def add_imagined_trajectories(self, trajectories):
        # trajectories: liste de séquences d'états latents (convertis en positions si possible)
        # Pour ce prototype simple, on suppose que les 2 premières dimensions du latent 
        # correspondent approximativement à l'espace 2D pour la visualisation
        self.imagined_trajectories = trajectories

    def plot(self, step_name):
        plt.figure(figsize=(8, 8))
        
        # Tracer l'objectif
        plt.scatter(self.goal[0], self.goal[1], c='red', marker='*', s=200, label='Objectif')
        
        # Tracer les trajectoires imaginées (en gris léger)
        for traj in self.imagined_trajectories:
            # Assurez-vous que traj est une liste de tenseurs et que chaque tenseur a au moins 2 dimensions
            if traj and all(isinstance(t, torch.Tensor) and t.dim() >= 1 for t in traj):
                # Convertir les tenseurs en numpy et prendre les 2 premières dimensions pour la visualisation
                traj_pts = torch.stack(traj).detach().cpu().numpy()[:, :2] 
                plt.plot(traj_pts[:, 0], traj_pts[:, 1], c='gray', alpha=0.1)
        
        # Tracer le trajet réel
        if self.history:
            history_pts = torch.tensor(self.history).numpy()
            plt.plot(history_pts[:, 0], history_pts[:, 1], c='blue', marker='o', label='Trajet Réel')
            plt.scatter(history_pts[-1, 0], history_pts[-1, 1], c='green', s=100, label='Position Actuelle')

        plt.title(f"Luthor Agentic Planning - {step_name}")
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.legend()
        plt.grid(True)
        plt.xlim(-6, 7)
        plt.ylim(-6, 7)
        
        filename = f"luthor_step_{step_name}.png"
        plt.savefig(filename)
        plt.close()
        return filename
