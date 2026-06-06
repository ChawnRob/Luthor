# LUTHOR — Options (couche 3)

Documentation des options activables autour du moteur JEPA et du dashboard.

## Connecteurs MCP

| Connecteur | Variable d'activation | Usage |
|------------|----------------------|-------|
| n8n | `LUTHOR_MCP_N8N_ENABLED` | Automatisation workflows |
| PenPot | `LUTHOR_MCP_PENPOT_ENABLED` | Design UI |
| AppFlowy | `LUTHOR_MCP_APPFLOWY_ENABLED` | Base de connaissances |
| Plausible | `LUTHOR_MCP_PLAUSIBLE_ENABLED` | Analytics |
| Whisper | `LUTHOR_MCP_WHISPER_ENABLED` | Transcription audio |
| yt-dlp | `LUTHOR_MCP_YTDLP_ENABLED` | Extraction média |
| Fooocus | `LUTHOR_MCP_FOOOCUS_ENABLED` | Génération d'images |
| Cal.com | `LUTHOR_MCP_CALCOM_ENABLED` | Prise de rendez-vous |

Configuration : `params.yaml` section `mcp.tools` + secrets dans `.env.prod`.

Endpoints API :
- `GET /mcp/tools` — inventaire
- `POST /mcp/orchestrate` — orchestration Mistral + outils
- `GET /sync/tools` — état de synchronisation (dashboard)

Tests : `tests/test_mcp_connectors.py`, `tests/test_mcp_media_connectors.py`, `tests/test_mcp_e2e.py`.

## Monitoring Prometheus + Grafana

- Métriques API : `GET /metrics`
- Prometheus : service `prometheus` dans `docker-compose.prod.yml`
- Grafana : `https://grafana.${LUTHOR_DOMAIN}`
- Dashboard provisionné : `docker/grafana/provisioning/dashboards/luthor.json`

Panels : requêtes HTTP, latence, inférences JEPA, versions de modèle, rounds d'active learning.

Voir aussi `docs/MONITORING.md`.

## Déploiement VPS

- Stack complète : `docker-compose.prod.yml`
- Script déploiement : `scripts/deploy_prod.sh`
- Sauvegarde : `scripts/backup_prod.sh` → `backups/<timestamp>/`
- **Restauration** : `scripts/restore_prod.sh backups/<timestamp>`

Services exposés via Traefik : API, UI (`app.`), Grafana, n8n, Plausible, Cal.com, Fooocus.

Voir `docs/DEPLOY_PROD.md`.

## Export et logs

- `GET /export/logs` — export CSV/XLSX (token `X-Export-Token`)
- `GET /logs` — consultation paginée (dashboard)

## A/B testing et prompts

- `GET /ab/metrics` — comparaison de versions de modèle
- `GET /prompts` — versions de prompts système

## SLM fallback (moteur)

Option de secours orchestrateur sans service permanent :

```env
LUTHOR_SLM_FALLBACK_ENABLED=true
LUTHOR_SLM_MODEL_PATH=./models/SmolLM3-3B-Q4_K_M.gguf
```

Dépendance optionnelle : `pip install llama-cpp-python`

## Carburant (phase ultérieure — non inclus)

Les éléments suivants sont **hors scope** de la couche Options et seront développés sur une branche séparée après pilote terrain :

- Stripe (webhooks, upgrade `quota_tier`)
- Portail développeur (clés API, Swagger interactif)
- Facturation abonnements
- Mode entreprise (organisations, rôles)
