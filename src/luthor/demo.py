import torch
import torch.optim as optim
from luthor.jepa_model.world_model import WorldModel
from luthor.jepa_model.planner import Planner
from luthor.environment.simple_env import SimpleEnvironment
from luthor.utils.cost_function import euclidean_distance_cost
from luthor.utils.visualizer import Visualizer

def main():
    # Hyperparamètres
    input_dim = 2
    latent_dim = 2 # Réduit à 2 pour une visualisation directe
    action_dim = 2
    horizon = 5
    num_samples = 50
    learning_rate = 0.01
    num_episodes = 100

    # Initialisation
    env = SimpleEnvironment(input_dim, action_dim)
    world_model = WorldModel(input_dim, latent_dim, action_dim)
    optimizer = optim.Adam(world_model.parameters(), lr=learning_rate)
    planner = Planner(world_model, action_dim, horizon, num_samples, euclidean_distance_cost)

    print("--- Phase 1: Apprentissage du Modèle du Monde (Luthor) ---")
    for episode in range(num_episodes):
        obs = env.reset()
        total_loss = 0
        for _ in range(10):
            action = torch.rand(action_dim) * 2 - 1
            next_obs = env.step(action)
            
            optimizer.zero_grad()
            current_latent = world_model.encoder(obs)
            target_latent = world_model.encoder(next_obs).detach()
            predicted_latent = world_model.predictor(current_latent, action)
            
            loss = torch.mean((predicted_latent - target_latent)**2)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            obs = next_obs
        
        if (episode + 1) % 20 == 0:
            print(f"Épisode {episode+1}/{num_episodes}, Perte: {total_loss/10:.6f}")

    print("\n--- Phase 2: Planification Agentique vers un But ---")
    goal = torch.tensor([5.0, 5.0])
    current_obs = env.reset()
    
    viz = Visualizer(goal)
    viz.add_real_step(current_obs)

    print(f"Départ: {current_obs.tolist()}")
    print(f"Objectif: {goal.tolist()}")

    for step in range(15):
        # Planifier et obtenir les trajectoires imaginées
        action, imagined = planner.plan(current_obs, goal)
        
        # Ajouter les trajectoires imaginées à la visualisation
        # Convertir les trajectoires latentes en coordonnées 2D pour la visualisation
        imagined_2d_trajectories = []
        for traj in imagined:
            # Chaque élément de traj est un tenseur latent. Nous prenons les 2 premières dimensions.
            imagined_2d_trajectories.append([t[:2] for t in traj])
        viz.add_imagined_trajectories(imagined_2d_trajectories)
        
        # Sauvegarder l'image de la réflexion de Luthor
        img_path = viz.plot(f"step_{step+1}")
        
        # Appliquer l'action
        next_obs = env.step(action)
        viz.add_real_step(next_obs)
        
        dist = torch.norm(next_obs - goal).item()
        print(f"Étape {step+1}: Position {next_obs.tolist()}, Distance au but: {dist:.4f}")
        
        current_obs = next_obs
        if dist < 0.5:
            print("But atteint !")
            break
    
    print("\nVisualisations générées sous forme d'images PNG.")

if __name__ == "__main__":
    main()
