# Luthor : Un Modèle de Monde Agentique (JEPA)

Ce dépôt contient **Luthor**, un prototype de Modèle de Monde Agentique (Agentic World Model) inspiré des principes de l'Intelligence Machine Autonome (AMI) de Yann LeCun. Il vise à démontrer comment un agent peut apprendre une représentation abstraite du monde, prédire les conséquences de ses actions et planifier pour atteindre des objectifs, sans recourir à des modèles génératifs complexes.

## Concepts Clés Implémentés

-   **JEPA (Joint Embedding Predictive Architecture)** : Le cœur du modèle du monde, apprenant à prédire l'état futur dans un **espace latent abstrait** plutôt que de reconstruire des observations brutes.
-   **Non-Génératif** : Focalisation sur les aspects prédictibles et sémantiquement importants du monde, rendant le modèle plus robuste face à l'incertitude.
-   **MPC (Model Predictive Control)** : Un planificateur qui utilise le modèle du monde pour simuler et évaluer différentes séquences d'actions afin de choisir la meilleure pour atteindre un objectif.
-   **Visualisation de la Planification** : Des outils graphiques pour observer comment Luthor 
explore mentalement les futurs possibles.

## Structure du Projet

```
Luthor/
├── docs/
│   ├── ARCHITECTURE.md
│   ├── PROCESS.md
│   └── ROADMAP.md
├── src/
│   └── luthor/
│       ├── __init__.py
│       ├── demo.py
│       ├── environment/
│       │   └── simple_env.py
│       ├── jepa_model/
│       │   ├── encoder.py
│       │   ├── __init__.py
│       │   ├── planner.py
│       │   ├── predictor.py
│       │   └── world_model.py
│       └── utils/
│           ├── cost_function.py
│           └── visualizer.py
├── .gitignore
├── README.md
└── requirements.txt
```

-   **`docs/`** : Contient la documentation technique détaillée du projet.
    -   `ARCHITECTURE.md` : Description de l'architecture de Luthor.
    -   `PROCESS.md` : Détail du processus de développement.
    -   `ROADMAP.md` : Feuille de route pour les évolutions futures.
    -   `COST_STRATEGY_SME.md` : Stratégie pour réduire les coûts de l'IA pour les PME.
    -   `SUBQUADRATIC_ANALYSIS.md` : Analyse technique de l'architecture Subquadratic.
-   **`src/luthor/`** : Le code source principal du projet.
    -   `jepa_model/` : Implémentation de l'encodeur, du prédicteur, du modèle du monde et du planificateur JEPA.
    -   `environment/` : Environnement de simulation simple.
    -   `utils/` : Fonctions utilitaires et module de visualisation.
    -   `demo.py` : Script principal pour l'apprentissage et la planification.
-   **`.gitignore`** : Fichier de configuration pour Git.
-   **`README.md`** : Ce fichier.
-   **`requirements.txt`** : Liste des dépendances Python.

## Installation

Pour installer les dépendances nécessaires, utilisez pip :

```bash
pip install -r requirements.txt
```

## Utilisation

Pour exécuter la démonstration de Luthor, qui inclut l'apprentissage du modèle du monde et la planification avec visualisation :

```bash
python src/luthor/demo.py
```

Les visualisations de la planification seront sauvegardées sous forme d'images PNG dans le répertoire courant.

## À Propos

Ce projet a été développé par **Manus AI** en tant que prototype d'Agentic World Model, explorant les concepts d'Intelligence Machine Autonome (AMI) et de Joint Embedding Predictive Architecture (JEPA) de Yann LeCun. Il sert de base pour la recherche et le développement de systèmes d'IA plus autonomes et intelligents.
