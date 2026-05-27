# Feuille de Route de Luthor : Évolutions Futures

Ce document décrit la feuille de route pour le développement futur de **Luthor**, un Modèle de Monde Agentique (Agentic World Model) basé sur les principes JEPA. Le prototype actuel pose les bases, mais de nombreuses améliorations et extensions sont possibles pour le rendre plus robuste, performant et proche de la vision d'une Intelligence Machine Autonome.

## 1. Améliorations du Modèle du Monde (JEPA) et Intégration Subquadratique

-   **Exploration des Architectures Subquadratiques (SSA/SSM)** :
    -   Évaluer et intégrer des architectures subquadratiques (comme la Sparse Attention de Subquadratic ou les State Space Models type Mamba) pour le prédicteur du modèle du monde. Cela permettra de gérer des horizons temporels beaucoup plus longs avec une efficacité de calcul linéaire, résolvant ainsi les limitations des architectures quadratiques.
    -   Analyser les APIs disponibles (comme celle de Subquadratic) pour une intégration rapide, tout en considérant les défis de latence et de modalité des données.



-   **Encodeurs et Prédicteurs plus Complexes** :
    -   Remplacer les réseaux linéaires actuels par des architectures plus sophistiquées (par exemple, des réseaux convolutifs pour des entrées visuelles, des Transformers pour des séquences).
    -   Explorer des encodeurs multi-modaux pour intégrer des informations provenant de différentes sources (vision, audio, texte, capteurs).
-   **Apprentissage Hiérarchique (H-JEPA)** :
    -   Implémenter une architecture JEPA hiérarchique où différents niveaux de l'encodeur apprennent des représentations à différentes échelles de temps et d'abstraction.
    -   Permettre au modèle de prédire des événements à long terme en se basant sur des représentations de haut niveau.
-   **Gestion de l'Incertitude** :
    -   Intégrer des mécanismes pour modéliser l'incertitude dans les prédictions (par exemple, des modèles probabilistes, des ensembles de prédicteurs).
    -   Utiliser des fonctions de perte qui tiennent compte de la confiance du modèle dans ses prédictions.

## 2. Raffinement du Planificateur

-   **Planification plus Efficace** :
    -   Explorer des algorithmes de planification plus avancés que l'échantillonnage aléatoire (par exemple, Monte Carlo Tree Search, Cross-Entropy Method, ou des méthodes basées sur les gradients si le modèle du monde est entièrement différentiable).
    -   Optimiser la recherche d'actions pour des horizons de planification plus longs.
-   **Planification Hiérarchique** :
    -   Développer un planificateur capable de décomposer des objectifs complexes en sous-objectifs, en exploitant les représentations hiérarchiques du H-JEPA.
    -   Permettre à l'agent de raisonner à différents niveaux d'abstraction pour des tâches à long terme.
-   **Intégration de la Motivation Intrinsèque** :
    -   Formaliser et intégrer des fonctions de coût basées sur la curiosité, la nouveauté ou la réduction de l'incertitude pour encourager l'exploration autonome de l'environnement.

## 3. Environnements et Tâches plus Riches

-   **Environnements 3D/Physiques** :
    -   Migrer vers des environnements de simulation plus réalistes (par exemple, PyBullet, MuJoCo, Unity) pour tester Luthor dans des scénarios de robotique ou de navigation complexe.
    -   Utiliser des données réelles (vidéos, capteurs) pour l'entraînement du modèle du monde.
-   **Tâches Complexes** :
    -   Appliquer Luthor à des tâches nécessitant un raisonnement et une planification à long terme (par exemple, manipulation d'objets, résolution de puzzles, jeux vidéo complexes).
    -   Évaluer la capacité de l'agent à transférer des connaissances entre différentes tâches.

## 4. Architecture et Infrastructure

-   **Modularité et Extensibilité** :
    -   Continuer à améliorer la modularité du code pour faciliter l'intégration de nouveaux composants et la collaboration.
    -   Mettre en place un système de gestion de configuration pour les hyperparamètres et les architectures de modèle.
-   **Optimisation des Performances** :
    -   Utiliser des techniques d'optimisation (par exemple, compilation de graphes, parallélisation) pour accélérer l'entraînement et l'inférence.
    -   Explorer le déploiement sur du matériel spécialisé (GPU, TPU).
-   **Tests et Évaluation** :
    -   Développer une suite de tests unitaires et d'intégration complète.
    -   Mettre en place des métriques d'évaluation robustes pour mesurer les performances du modèle du monde et du planificateur.

## 5. Collaboration et Communauté

-   **Contribution Open Source** :
    -   Encourager les contributions de la communauté pour enrichir le projet.
    -   Fournir des guides clairs pour les contributeurs.
-   **Documentation et Tutoriels** :
    -   Créer des tutoriels détaillés pour aider les nouveaux utilisateurs à comprendre et à utiliser Luthor.
    -   Maintenir une documentation à jour et facile à naviguer.

Cette feuille de route est un document évolutif qui sera mis à jour au fur et à mesure de l'avancement du projet et des nouvelles découvertes dans le domaine de l'IA. L'intégration de l'architecture Subquadratic est une priorité pour les prochaines étapes de développement.
