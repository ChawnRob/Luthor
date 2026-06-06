# Démo workflow complet LUTHOR

Démonstration bout en bout : **Mistral** planifie des appels MCP, LUTHOR les exécute séquentiellement et sauvegarde les artefacts dans `demo_outputs/`.

## Prérequis

1. `mcp.enabled: true` dans `params.yaml`
2. Au moins un connecteur MCP actif et configuré
3. `MISTRAL_API_KEY` pour l'orchestration (sauf en tests mockés)

## Script CLI

```bash
export MISTRAL_API_KEY=your-key
export LUTHOR_MCP_YTDLP_ENABLED=true

python3 scripts/demo_full_workflow.py \
  --message "Synthèse du dernier podcast sur l'IA, génère une image et crée un rendez-vous"
```

Options :

| Option | Description |
|--------|-------------|
| `--message` | Requête utilisateur (défaut : message podcast + image + RDV) |
| `--output-dir` | Dossier de sortie (défaut : `demo_outputs/`) |

Sorties :

- `demo_outputs/run_<id>/step_XX_<tool>/` — artefacts par étape
- `demo_outputs/run_<id>/summary.json` — métadonnées complètes
- `demo_outputs/summary.json` — dernier run

## API

### `POST /demo/full`

```bash
curl -X POST http://localhost:8080/demo/full \
  -H "Content-Type: application/json" \
  -d '{"message": "Télécharge les métadonnées d une vidéo IA et trace un événement Plausible"}'
```

Mode asynchrone :

```bash
curl -X POST http://localhost:8080/demo/full \
  -H "Content-Type: application/json" \
  -d '{"message": "...", "async": true}'
# → {"task_id": "...", "status": "pending"}

curl http://localhost:8080/demo/tasks/<task_id>
```

- Sync (défaut) : timeout 5 minutes, retourne le `summary` JSON
- Async : retour immédiat + polling via `GET /demo/tasks/{task_id}`

### Interface web

Ouvrir [http://localhost:8080/demo-ui](http://localhost:8080/demo-ui) après `make run-api`.

## Exemples de messages

| Message | Outils probables |
|---------|------------------|
| « Synthèse podcast IA + image + RDV » | yt-dlp, Fooocus, Cal.com |
| « Transcris cet audio et sauve dans AppFlowy » | Whisper, AppFlowy |
| « Génère une image produit minimaliste » | Fooocus |
| « Crée un booking demain 10h » | Cal.com |

## Connecteurs désactivés

Si un outil est demandé mais indisponible, le workflow :

1. Affiche un avertissement (`Fooocus désactivé — étape ignorée`)
2. Continue les autres étapes
3. Inclut les warnings dans `summary.json`

## Tests

```bash
python3 -m unittest tests.test_demo_workflow tests.test_demo_endpoint -v
```
