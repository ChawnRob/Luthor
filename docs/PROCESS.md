# Processus de Construction de Luthor : Un Modèle de Monde Agentique

Ce document retrace les étapes détaillées de la conception et de l'implémentation du projet **Luthor**, un prototype de Modèle de Monde Agentique (Agentic World Model) inspiré des travaux de Yann LeCun. L'objectif est de fournir une transparence complète sur la démarche d'ingénierie, les choix techniques et l'évolution du projet depuis sa conception initiale jusqu'à sa structuration pour un dépôt GitHub professionnel.

## 1. Compréhension Initiale et Planification

La demande initiale de l'utilisateur était de créer un "agentic world model" basé sur les principes de l'AMI de Yann LeCun. Une phase de recherche approfondie a été menée pour collecter les informations clés sur l'architecture AMI, la Joint Embedding Predictive Architecture (JEPA), ses variantes (V-JEPA, H-JEPA), les fonctions de coût et la motivation intrinsèque. Cette recherche a permis de poser les bases théoriques nécessaires à la conception du prototype.

Le plan initial a été structuré en phases distinctes :
-   **Recherche et collecte des sources AMI / JEPA / LeCun** : Acquisition des connaissances fondamentales.
-   **Rédaction du document technique de référence** : Synthèse des informations et formalisation de la compréhension.
-   **Livraison du document à l'utilisateur** : Présentation des conclusions de la recherche.

## 2. Conception et Implémentation du Prototype Initial (jepa_prototype)

Suite à la validation du document technique, l'utilisateur a demandé la création d'un prototype fonctionnel. La décision a été prise de développer un prototype "skeleton" en Python, se concentrant sur les trois piliers de l'architecture :
1.  **L'Intégration Conjointe (Joint Embedding)** : Un encodeur pour projeter les observations dans un espace latent.
2.  **Le Prédicteur Latent** : Un module pour prédire l'état futur dans cet espace latent.
3.  **La Planification par MPC (Model Predictive Control)** : Un mécanisme de décision utilisant le modèle pour minimiser un coût.

### 2.1. Structuration du Répertoire Initial

Un répertoire `jepa_prototype` a été créé avec une structure simple :
-   `jepa_prototype/jepa_model` : Pour les composants du modèle (encodeur, prédicteur, planificateur).
-   `jepa_prototype/environment` : Pour l'environnement de simulation.
-   `jepa_prototype/utils` : Pour les fonctions utilitaires (fonction de coût).

### 2.2. Développement des Modules Clés

-   **`encoder.py`** : Implémentation d'un `nn.Sequential` simple pour transformer un `input_dim` en `latent_dim`.
-   **`predictor.py`** : Implémentation d'un `nn.Sequential` qui prend un état latent et une action pour prédire le prochain état latent.
-   **`world_model.py`** : Un module `nn.Module` combinant l'encodeur et le prédicteur pour former le cœur du modèle du monde.
-   **`planner.py`** : Implémentation d'un planificateur basé sur le Model Predictive Control (MPC). Il échantillonne des séquences d'actions, simule les trajectoires avec le `WorldModel` et choisit la meilleure action en fonction d'une fonction de coût.
-   **`simple_env.py`** : Un environnement 2D minimaliste pour simuler la dynamique d'un agent se déplaçant dans un espace.
-   **`cost_function.py`** : Une fonction de coût simple (distance euclidienne) pour évaluer la proximité d'un état latent par rapport à un objectif.

### 2.3. Script de Démonstration (`demo.py`)

Un script `demo.py` a été créé pour orchestrer l'apprentissage du `WorldModel` (phase 1) et la planification de l'agent vers un objectif (phase 2). L'apprentissage du modèle du monde est réalisé de manière auto-supervisée en minimisant la différence entre l'état latent prédit et l'état latent réel de l'observation suivante.

## 3. Intégration de la Visualisation

À la demande de l'utilisateur, une fonctionnalité de visualisation a été ajoutée pour mieux comprendre le processus de planification de Luthor. Cela a impliqué :
-   **`visualizer.py`** : Création d'une classe `Visualizer` utilisant `matplotlib` pour tracer le chemin réel de l'agent, l'objectif et les trajectoires imaginées par le planificateur.
-   **Mise à jour de `planner.py`** : Modification du planificateur pour qu'il retourne non seulement la meilleure action, mais aussi toutes les trajectoires simulées.
-   **Mise à jour de `demo.py`** : Intégration de la classe `Visualizer` pour générer et sauvegarder des images à chaque étape de planification.

Des ajustements ont été nécessaires pour gérer les dépendances (`torch`, `matplotlib`, `numpy`) et résoudre les problèmes de compatibilité de version (`numpy` en particulier).

## 4. Transformation en Projet Professionnel (Luthor) pour GitHub

Pour préparer le projet à être partagé sur GitHub sous le nom **Luthor** et le compte **ChawRob**, une restructuration majeure a été entreprise pour adopter une architecture de package Python standard et inclure une documentation complète.

### 4.1. Nouvelle Structure de Répertoire

Le répertoire `jepa_prototype` a été supprimé et remplacé par `Luthor` avec la structure suivante :
-   `Luthor/src/luthor/` : Contient le code source principal, organisé en sous-modules (`jepa_model`, `environment`, `utils`).
-   `Luthor/tests/` : Pour les futurs tests unitaires et d'intégration.
-   `Luthor/docs/` : Pour la documentation technique.
-   `Luthor/` (à la racine) : Pour les fichiers de configuration du projet (`README.md`, `requirements.txt`, etc.).

### 4.2. Mise à Jour du Code Source

-   Tous les fichiers `.py` ont été déplacés dans `Luthor/src/luthor/`.
-   Les imports dans `demo.py` et `world_model.py` ont été mis à jour pour refléter la nouvelle structure de package (par exemple, `from luthor.jepa_model.world_model import WorldModel`).
-   Un fichier `__init__.py` vide a été ajouté dans `Luthor/src/luthor/` pour le déclarer comme un package Python.

### 4.3. Création de la Documentation Technique

Trois documents clés ont été rédigés dans le répertoire `docs/` :
-   **`ARCHITECTURE.md`** : Décrit en détail l'architecture de Luthor, les composants JEPA, le fonctionnement du planificateur MPC, l'environnement de simulation et la visualisation, ainsi que les fondements théoriques.
-   **`ROADMAP.md`** : Présente les évolutions futures envisagées pour le projet, incluant des améliorations du modèle du monde, du planificateur, des environnements et de l'infrastructure.
-   **`PROCESS.md`** (ce document) : Détaillé le processus de construction étape par étape.

### 4.4. Fichiers de Configuration du Projet

-   **`README.md`** : Mis à jour pour refléter le nom du projet "Luthor", sa nouvelle structure et les instructions d'installation/utilisation.
-   **`.gitignore`** : Ajouté pour ignorer les fichiers temporaires, les dossiers d'environnement virtuel et les images générées (`*.png`).
-   **`requirements.txt`** : Liste les dépendances Python nécessaires (`torch`, `matplotlib`, `numpy`).
-   **`pyproject.toml`** : Fichier de configuration pour la gestion du projet Python (non implémenté dans ce prototype simple, mais mentionné pour une future évolution).

## 5. Instructions de Déploiement GitHub

Des instructions claires ont été fournies à l'utilisateur pour initialiser un dépôt Git localement, ajouter les fichiers, commiter et pousser le tout vers son dépôt GitHub `ChawRob/Luthor`. Cela permet à l'utilisateur de garder le contrôle total sur le processus de déploiement tout en bénéficiant d'un projet structuré et documenté.

Ce processus itératif a permis de transformer une demande conceptuelle en un prototype fonctionnel et bien documenté, prêt à être exploré et étendu. Chaque étape a été guidée par les principes d'ingénierie logicielle et les meilleures pratiques pour le développement de projets open source.
