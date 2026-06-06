# Luthor : Un Modèle de Monde Agentique (JEPA)

Ce dépôt contient **Luthor**, un prototype de Modèle de Monde Agentique (Agentic World Model) inspiré des principes de l'Intelligence Machine Autonome (AMI) de Yann LeCun. Il démontre comment un agent peut apprendre une représentation abstraite du monde, prédire les conséquences de ses actions et planifier pour atteindre des objectifs, sans recourir à des modèles génératifs complexes.

## Concepts clés

- **JEPA (Joint Embedding Predictive Architecture)** : prédiction d'états futurs dans un espace latent abstrait.
- **MPC (Model Predictive Control)** : planification par échantillonnage de trajectoires.
- **Apprentissage actif** : sélection par incertitude (variance du prédicteur) avec oracle dummy.
- **GridWorld** : environnement grille 2D avec obstacles, but et bruit optionnel.
- **API FastAPI** : endpoints `/embed`, `/predict`, `/active_learn` avec stockage PostgreSQL + ChromaDB.
- **Pipeline DVC** : entraînement reproductible versionné via `params.yaml`.

## Structure du projet

```
Luthor/
├── dvc.yaml                 # Pipeline DVC (prepare_data → train)
├── params.yaml              # Hyperparamètres du pipeline
├── Makefile                 # Commandes make (demo, active, test, API, DVC…)
├── docker-compose.yml       # PostgreSQL + ChromaDB + API
├── data/raw/                # GridWorld versionné (sortie DVC)
├── docs/                    # Documentation technique
├── src/luthor/
│   ├── demo.py              # Démo JEPA + planification MPC
│   ├── active_demo.py       # Boucle d'apprentissage actif
│   ├── api/                 # Service FastAPI
│   ├── active_learning/     # Oracle, sampler, boucle AL
│   ├── environment/         # GridWorld (+ alias SimpleEnvironment)
│   ├── jepa_model/          # Encoder, Predictor, WorldModel, Planner
│   ├── pipeline/            # Scripts DVC (prepare_data, train)
│   ├── training/            # Étapes d'entraînement JEPA
│   └── utils/               # Métriques, logging, visualisation
├── tests/                   # Suite unittest (24 tests)
└── website/                 # Landing page React (FR/EN)
```

## Installation

```bash
# Cloner le dépôt
git clone https://github.com/ChawnRob/Luthor.git
cd Luthor

# Installer les dépendances Python
make install
# ou : pip install -r requirements.txt
```

Prérequis : Python 3.10+, pip. Pour l'API Docker : Docker et Docker Compose.

## Commandes Make

| Commande | Description |
|----------|-------------|
| `make install` | Installe les dépendances (`requirements.txt`) |
| `make demo` | JEPA training + planification MPC sur GridWorld |
| `make active` | Boucle d'apprentissage actif (uncertainty sampling) |
| `make test` | Lance la suite de tests (24 tests) |
| `make run-api` | Démarre l'API FastAPI sur `http://localhost:8080` |
| `make docker-up` | Lance PostgreSQL + ChromaDB + API via Docker Compose |
| `make docker-down` | Arrête les services Docker |
| `make docker-logs` | Affiche les logs du conteneur API |
| `make dvc-repro` | Exécute le pipeline DVC complet |

### Démo interactive

```bash
make demo
```

Génère des visualisations PNG dans `outputs/` et un log JSON `outputs/demo_run.json` contenant `final_loss`, `success_rate` et `steps_per_episode`.

### Apprentissage actif

```bash
make active
```

Produit `outputs/active_demo_run.json` avec les métriques d'évaluation.

### Variables d'environnement (optionnel)

Les hyperparamètres peuvent être surchargés via des variables `LUTHOR_*` (voir `src/luthor/config.py`) :

```bash
LUTHOR_ENCODER_LATENT_DIM=16 LUTHOR_PLANNER_ITERATIONS=50 make demo
LUTHOR_EVAL_EPISODES=10 make active
```

## API FastAPI

### Démarrage

```bash
# Option 1 : stack complète (PostgreSQL + ChromaDB + API)
make docker-up

# Option 2 : API seule (nécessite Postgres:5432 et ChromaDB:8001)
make run-api
```

Documentation interactive : [http://localhost:8080/docs](http://localhost:8080/docs)

### Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/health` | État API, PostgreSQL, ChromaDB |
| `POST` | `/embed` | Encode une observation → vecteur latent (stocké dans ChromaDB) |
| `POST` | `/predict` | Prédit le latent suivant + incertitude (MC dropout) |
| `POST` | `/active_learn` | Lance des rounds d'apprentissage actif |

### Exemples curl

```bash
# Encoder une observation
curl -X POST http://localhost:8080/embed \
  -H 'Content-Type: application/json' \
  -d '{"observation": [1.0, 2.0]}'

# Prédire l'état latent suivant
curl -X POST http://localhost:8080/predict \
  -H 'Content-Type: application/json' \
  -d '{"observation": [0.5, -1.0], "action": [0.2, 0.3]}'

# Lancer l'apprentissage actif
curl -X POST http://localhost:8080/active_learn \
  -H 'Content-Type: application/json' \
  -d '{"num_rounds": 3, "pool_size": 16, "query_batch_size": 4}'
```

### Configuration stockage

| Variable | Défaut |
|----------|--------|
| `LUTHOR_POSTGRES_URL` | `postgresql://luthor:luthor@localhost:5432/luthor` |
| `LUTHOR_CHROMA_HOST` | `localhost` |
| `LUTHOR_CHROMA_PORT` | `8001` |

## Pipeline DVC

Le pipeline DVC assure un entraînement reproductible et versionné.

### Stages

1. **`prepare_data`** — génère `data/raw/gridworld.json` (GridWorld versionné) depuis `params.yaml`
2. **`train`** — entraîne JEPA + apprentissage actif, exporte `metrics.json`

### Utilisation

```bash
# Modifier les hyperparamètres
vim params.yaml

# Exécuter le pipeline complet
make dvc-repro
```

### Sortie `metrics.json`

```json
{
  "final_loss": 0.12,
  "success_rate": 45.0,
  "steps_per_episode": [10, 8, 50, 12, 6]
}
```

| Champ | Description |
|-------|-------------|
| `final_loss` | Perte moyenne du dernier round d'apprentissage actif |
| `success_rate` | % d'épisodes atteignant le but en ≤ `max_steps` |
| `steps_per_episode` | Nombre de steps par épisode d'évaluation |

### Hyperparamètres (`params.yaml`)

Sections principales : `gridworld`, `encoder`, `predictor`, `planner`, `active_learning`, `eval`, `seed`.

## Tests

```bash
make test
```

Couvre : imports package, JEPA config, GridWorld, métriques, logging, API, pipeline DVC (incluant `dvc repro` end-to-end).

## Documentation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — Architecture AMI / JEPA
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — Feuille de route
- [`docs/PROCESS.md`](docs/PROCESS.md) — Historique de développement
- [`docs/COST_STRATEGY_SME.md`](docs/COST_STRATEGY_SME.md) — Stratégie coûts PME

## À propos

Projet fondé par **Robyn Chawn (ChawnRob)** — architecture et implémentation par **Manus AI**. Inspiré des travaux de Yann LeCun sur l'AMI et la JEPA. Voir [`AUTHORS`](AUTHORS) pour les contributeurs.
