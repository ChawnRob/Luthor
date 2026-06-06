# LUTHOR — Moteur (couche 1)

## Noyau JEPA

| Composant | Module | Tests |
|-----------|--------|-------|
| Encodeur | `src/luthor/jepa_model/encoder.py` | `tests/test_encoder.py` |
| Prédicteur | `src/luthor/jepa_model/predictor.py` | `tests/test_subquadratic_predictor.py` |
| World model | `src/luthor/jepa_model/world_model.py` | `tests/test_demo.py`, `tests/test_context_integration.py` |
| MPC Planner | `src/luthor/jepa_model/planner.py` | `tests/test_planner.py` |

## API moteur

Endpoints principaux dans `src/luthor/api/main.py` :

- `GET /health` — santé Postgres + ChromaDB
- `GET /metrics` — Prometheus
- `POST /embed` — encodage JEPA
- `POST /predict` — prédiction + incertitude
- `POST /active_learn` — boucle d'apprentissage actif

Tests : `tests/test_api.py`, `tests/test_prometheus_metrics.py`.

## SLM fallback (SmolLM3)

Secours on-demand pour l'orchestrateur MCP (pas de service permanent) :

- `src/luthor/slm_fallback.py` — chargement lazy via `llama-cpp-python`
- `src/luthor/orchestrator_llm.py` — wrapper résilient Mistral → SmolLM
- Tests : `tests/test_slm_fallback.py`

```env
LUTHOR_SLM_FALLBACK_ENABLED=true
LUTHOR_SLM_MODEL_PATH=./models/SmolLM3-3B-Q4_K_M.gguf
pip install llama-cpp-python  # optionnel
```

## Tests de charge

Profil Locust léger : `tests/locustfile.py`

```bash
make run-api   # terminal 1
make load-test # terminal 2 (nécessite: pip install locust)
```

Validation statique : `tests/test_locustfile.py` (inclus dans `make test`).
