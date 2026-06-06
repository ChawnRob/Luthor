# MCP Tool Integration (n8n, PenPot, AppFlowy, Plausible)

LUTHOR exposes external tools through an MCP-style registry and orchestrates them with **Mistral function calling**.

## Architecture

```
User request → MCPOrchestrator (Mistral) → MCPRegistry.call_tool() → Connector (httpx async)
```

- Tool schemas: `src/luthor/mcp/mcp_tools.json`
- Connectors: `src/luthor/mcp/*_connector.py`
- Registry: `src/luthor/mcp/registry.py`
- Orchestrator: `src/luthor/orchestrator.py`

## Configuration

1. Copy credentials into `.env` (or export as environment variables).
2. Enable connectors in `params.yaml`:

```yaml
mcp:
  enabled: true
  tools:
    n8n:
      enabled: true
      url: "https://n8n.example.com"
    penpot:
      enabled: true
      url: "https://penpot.example.com"
```

3. Set `MISTRAL_API_KEY` for orchestration.

### Media & scheduling connectors

| Connector | Env vars | Notes |
|-----------|----------|-------|
| Whisper | `WHISPER_MODEL_SIZE`, `WHISPER_DEVICE` | Local CPU/CUDA transcription |
| yt-dlp | `YTDLP_DOWNLOAD_DIR`, `YTDLP_MAX_DOWNLOADS_PER_USER` | Domain allowlist in `params.yaml` |
| Fooocus | `FOOOCUS_API_URL`, `FOOOCUS_API_KEY` | Requires external Fooocus API |
| Cal.com | `CALCOM_API_URL`, `CALCOM_API_KEY`, `CALCOM_EVENT_TYPE_ID` | Self-hosted or cloud |

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/mcp/tools` | List enabled MCP tools |
| POST | `/mcp/orchestrate` | Run Mistral tool selection + execution |
| GET | `/tools/n8n` | List n8n workflows |
| POST | `/tools/n8n` | Trigger workflow |
| POST | `/tools/penpot` | Design actions (`create_file`, `add_shape`, `export_image`) |
| POST | `/tools/appflowy` | Memory actions (`create_page`, `append_to_page`, `search_pages`) |
| POST | `/tools/plausible` | Analytics (`track_event`, `get_stats`) |
| POST | `/tools/transcribe` | Whisper transcription (`audio_url` or `audio_b64`) |
| POST | `/tools/download` | yt-dlp download or `extract_info` |
| POST | `/tools/generate_image` | Fooocus text-to-image |
| POST | `/tools/booking` | Cal.com create booking |
| GET | `/tools/availability` | Cal.com available slots |

## Example

```bash
curl -X POST http://localhost:8080/mcp/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"message": "Log an agent_run event in Plausible"}'
```

## Tests

```bash
python3 -m unittest tests.test_mcp_connectors tests.test_mcp_media_connectors -v
```
