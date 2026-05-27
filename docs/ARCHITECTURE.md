# Architecture de Luthor : Un Modèle de Monde Agentique (JEPA)

Ce document décrit l'architecture du projet **Luthor**, un prototype de Modèle de Monde Agentique (Agentic World Model) inspiré des principes de l'Intelligence Machine Autonome (AMI) de Yann LeCun. L'objectif est de fournir une compréhension claire des composants clés, de leur interaction et des fondements théoriques sous-jacents.

## 1. Vue d'Ensemble de l'Architecture AMI

L'architecture de Luthor s'inscrit dans la vision de Yann LeCun pour une IA plus proche de l'intelligence humaine et animale, capable de raisonner, de planifier et de comprendre le monde physique. Elle est modulaire et repose sur l'apprentissage auto-supervisé de modèles du monde non génératifs.

Les principaux modules de cette architecture sont :
-   **Percepteur** : Reçoit les observations de l'environnement.
-   **Modeleur du Monde (World Model)** : Apprend une représentation abstraite du monde et prédit les conséquences des actions. C'est le cœur de l'implémentation JEPA.
-   **Configurateur** : Orchestre l'interaction entre les modules (non explicitement implémenté comme un module séparé dans ce prototype simple, mais son rôle est implicitement géré par la logique de `demo.py`).
-   **Planificateur** : Utilise le Modeleur du Monde pour explorer des séquences d'actions et choisir la meilleure.
-   **Acteur** : Exécute les actions choisies par le Planificateur.
-   **Système de Coût/Motivation Intrinsèque** : Guide l'apprentissage et le comportement de l'agent.

## 2. Le Cœur de Luthor : Joint Embedding Predictive Architecture (JEPA)

Au centre du Modeleur du Monde de Luthor se trouve une implémentation simplifiée de la **Joint Embedding Predictive Architecture (JEPA)**. Contrairement aux modèles génératifs qui tentent de prédire chaque pixel ou chaque détail de l'observation future, JEPA se concentre sur la prédiction dans un espace de représentation abstrait (latent).

### 2.1. Composants de la JEPA

La JEPA est composée de deux réseaux principaux :

-   **Encodeur (`jepa_model/encoder.py`)** :
    -   **Rôle** : Transforme une observation brute de l'environnement (par exemple, un état 2D `[x, y]`) en une représentation vectorielle de dimension inférieure dans un espace latent.
    -   **Implémentation** : Un simple réseau de neurones (`nn.Sequential`) avec des couches linéaires et des fonctions d'activation ReLU. L'objectif est d'apprendre des caractéristiques pertinentes de l'observation.

-   **Prédicteur (`jepa_model/predictor.py`)** :
    -   **Rôle** : Prend en entrée l'état latent actuel et une action, et prédit l'état latent futur résultant de cette action.
    -   **Implémentation** : Un réseau de neurones qui concatène l'état latent et l'action avant de les faire passer à travers des couches linéaires et ReLU pour produire la prédiction de l'état latent futur.

### 2.2. Apprentissage de la JEPA

L'apprentissage de la JEPA est auto-supervisé et non génératif. Il se déroule comme suit :
1.  L'Encodeur transforme l'observation actuelle `obs_t` en un état latent `z_t`.
2.  Une action `a_t` est appliquée dans l'environnement, résultant en une nouvelle observation `obs_{t+1}`.
3.  L'Encodeur transforme `obs_{t+1}` en un état latent cible `z_{t+1}`.
4.  Le Prédicteur prend `z_t` et `a_t` pour prédire `z'_{t+1}`.
5.  La fonction de perte minimise la distance entre `z'_{t+1}` (prédiction) et `z_{t+1}` (cible), mais `z_{t+1}` est traité comme une cible fixe (`.detach()`) pour éviter que l'encodeur ne s'effondre sur des représentations triviales. Cela encourage le prédicteur à apprendre une dynamique précise dans l'espace latent.

L'avantage de cette approche est qu'elle ne nécessite pas de reconstruire l'observation brute, ce qui est souvent bruité et imprévisible. Au lieu de cela, elle se concentre sur les aspects prédictibles et sémantiquement importants du monde.

## 3. Planification par Model Predictive Control (MPC)

Le **Planificateur (`jepa_model/planner.py`)** de Luthor utilise une stratégie de Model Predictive Control (MPC) pour prendre des décisions. Le MPC permet à l'agent de planifier ses actions en simulant les conséquences futures à l'aide de son modèle du monde.

### 3.1. Fonctionnement du Planificateur

1.  **Échantillonnage d'Actions** : Pour une observation actuelle donnée et un objectif, le planificateur génère plusieurs séquences d'actions aléatoires sur un horizon de temps défini.
2.  **Simulation** : Pour chaque séquence d'actions, le planificateur utilise le Modeleur du Monde (JEPA) pour simuler la trajectoire future de l'état latent de l'agent.
3.  **Évaluation des Coûts** : Une fonction de coût (`utils/cost_function.py`) évalue chaque trajectoire simulée en fonction de sa proximité avec l'objectif. Dans Luthor, une simple distance euclidienne est utilisée.
4.  **Sélection de la Meilleure Action** : La première action de la séquence qui minimise le coût total simulé est choisie et appliquée à l'environnement réel.
5.  **Répétition** : Le processus est répété à chaque pas de temps, permettant à l'agent de réévaluer et d'ajuster son plan en fonction des nouvelles observations.

## 4. Environnement de Simulation (`environment/simple_env.py`)

Pour démontrer le fonctionnement de Luthor, un `SimpleEnvironment` 2D est utilisé. Cet environnement simule une dynamique très basique où les actions de l'agent influencent directement son état, avec un peu de bruit. Cela permet de se concentrer sur la logique de l'Agentic World Model sans la complexité d'un environnement réaliste.

## 5. Visualisation (`utils/visualizer.py`)

Le module `Visualizer` utilise `matplotlib` pour illustrer le processus de planification de Luthor. Il affiche :
-   La trajectoire réelle de l'agent.
-   L'objectif à atteindre.
-   Les multiples trajectoires que le planificateur a "imaginées" et évaluées avant de choisir la meilleure action. Ces trajectoires sont représentées dans l'espace 2D, correspondant aux deux premières dimensions de l'espace latent pour une interprétation simplifiée.

## 6. Fondements Théoriques et Inspirations

L'architecture de Luthor s'inspire directement des travaux de Yann LeCun sur :
-   **L'apprentissage auto-supervisé non contrastif** : L'idée que les modèles peuvent apprendre des représentations riches sans nécessiter des paires positives/négatives explicites, en se concentrant sur la prédiction de parties masquées d'une entrée à partir d'autres parties.
-   **Les modèles basés sur l'énergie (EBM)** : Une approche où l'apprentissage consiste à définir une fonction d'énergie qui attribue une faible énergie aux configurations de données cohérentes et une énergie élevée aux configurations incohérentes.
-   **L'importance des modèles du monde** : La conviction que la capacité à construire des modèles internes du monde est fondamentale pour l'intelligence, permettant le raisonnement, la planification et l'acquisition rapide de nouvelles compétences.

Ce prototype est une première étape vers la réalisation d'un système d'IA capable de comprendre et d'interagir avec le monde de manière plus autonome et intelligente.
