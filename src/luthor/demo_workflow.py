from __future__ import annotations

import asyncio
import base64
import json
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from luthor.mcp.registry import MCPRegistry, get_mcp_registry
from luthor.orchestrator import MCPOrchestrator

DEFAULT_DEMO_MESSAGE = (
    "Synthèse du dernier podcast sur l'IA, génère une image et crée un rendez-vous"
)

DEMO_SYSTEM_PROMPT = (
    "You are the LUTHOR full-workflow demo orchestrator. "
    "Analyze the user request and call the most relevant MCP tools sequentially "
    "(transcription, download, image generation, booking, memory, analytics, automation). "
    "Use only tools that match the request. Prefer extract_info before download when researching media. "
    "Respond with tool calls when external actions are needed."
)

_demo_tasks: dict[str, dict[str, Any]] = {}


@dataclass
class DemoStepRecord:
    index: int
    tool_name: str
    success: bool
    duration_seconds: float
    arguments: dict[str, Any] = field(default_factory=dict)
    result: dict[str, Any] | None = None
    artifact_paths: list[str] = field(default_factory=list)
    error: str | None = None
    skipped: bool = False
    warning: str | None = None


@dataclass
class DemoWorkflowSummary:
    run_id: str
    message: str
    started_at: str
    finished_at: str
    duration_seconds: float
    final_summary: str
    used_tools: bool
    warnings: list[str]
    steps: list[DemoStepRecord]
    output_dir: str
    success: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "message": self.message,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration_seconds": self.duration_seconds,
            "final_summary": self.final_summary,
            "used_tools": self.used_tools,
            "warnings": self.warnings,
            "steps": [
                {
                    "index": step.index,
                    "tool_name": step.tool_name,
                    "success": step.success,
                    "duration_seconds": step.duration_seconds,
                    "arguments": step.arguments,
                    "result": step.result,
                    "artifact_paths": step.artifact_paths,
                    "error": step.error,
                    "skipped": step.skipped,
                    "warning": step.warning,
                }
                for step in self.steps
            ],
            "output_dir": self.output_dir,
            "success": self.success,
        }


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_output_dir() -> Path:
    return _repo_root() / "demo_outputs"


def check_mcp_availability(registry: MCPRegistry) -> tuple[bool, str, list[str]]:
    if not registry.config.enabled:
        return False, "MCP is disabled. Set mcp.enabled: true in params.yaml.", []

    active = [name for name, enabled in registry.connector_status().items() if enabled]
    if not active:
        return (
            False,
            "No MCP connectors are active. Enable and configure at least one connector.",
            [],
        )

    warnings = _collect_connector_warnings(registry)
    return True, "", warnings


def _collect_connector_warnings(registry: MCPRegistry) -> list[str]:
    warnings: list[str] = []
    labels = {
        "n8n": "n8n",
        "penpot": "PenPot",
        "appflowy": "AppFlowy",
        "plausible": "Plausible",
        "whisper": "Whisper",
        "ytdlp": "yt-dlp",
        "fooocus": "Fooocus",
        "calcom": "Cal.com",
    }
    for name, active in registry.connector_status().items():
        label = labels.get(name, name)
        connector = registry.config.tools.get(name)
        if connector is None:
            continue
        if active:
            continue
        if connector.enabled:
            warnings.append(f"{label} activé mais indisponible (credentials ou service manquant).")
        else:
            warnings.append(f"{label} désactivé — étapes associées seront ignorées si demandées.")
    return warnings


def _connector_for_tool(registry: MCPRegistry, tool_name: str) -> str | None:
    for tool in registry._tools:
        if tool["name"] == tool_name:
            return tool.get("connector")
    return None


def _is_tool_available(registry: MCPRegistry, tool_name: str) -> bool:
    connector = _connector_for_tool(registry, tool_name)
    if connector is None:
        return False
    return connector in registry._enabled_connectors()


def _save_step_artifacts(
    step_index: int,
    tool_name: str,
    payload: dict[str, Any],
    output_dir: Path,
) -> list[str]:
    step_dir = output_dir / f"step_{step_index:02d}_{tool_name}"
    step_dir.mkdir(parents=True, exist_ok=True)
    paths: list[str] = []

    result_path = step_dir / "result.json"
    result_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    paths.append(str(result_path))

    inner = payload.get("result", payload)
    if tool_name == "whisper_transcribe" and isinstance(inner, dict):
        text = inner.get("text", "")
        txt_path = step_dir / "transcription.txt"
        txt_path.write_text(text, encoding="utf-8")
        paths.append(str(txt_path))

    if tool_name == "fooocus_generate_image" and isinstance(inner, dict):
        image_b64 = inner.get("image_b64")
        if image_b64:
            image_path = step_dir / "image.png"
            image_path.write_bytes(base64.b64decode(image_b64))
            paths.append(str(image_path))

    if tool_name in {"ytdlp_download_media", "ytdlp_extract_info"} and isinstance(inner, dict):
        media_path = inner.get("path")
        if media_path:
            paths.append(str(media_path))

    if tool_name.startswith("appflowy_") and isinstance(inner, dict):
        memo_path = step_dir / "memory.txt"
        memo_path.write_text(json.dumps(inner, indent=2, ensure_ascii=False), encoding="utf-8")
        paths.append(str(memo_path))

    return paths


async def _execute_planned_tools(
    registry: MCPRegistry,
    tool_calls: list[dict[str, Any]],
    warnings: list[str],
    output_dir: Path,
) -> list[DemoStepRecord]:
    steps: list[DemoStepRecord] = []
    for index, call in enumerate(tool_calls, start=1):
        tool_name = call["name"]
        arguments = call.get("arguments", {})
        if isinstance(arguments, str):
            arguments = json.loads(arguments)

        started = time.perf_counter()
        if not _is_tool_available(registry, tool_name):
            connector = _connector_for_tool(registry, tool_name) or "unknown"
            warning = f"Outil {tool_name} ignoré ({connector} indisponible)."
            warnings.append(warning)
            steps.append(
                DemoStepRecord(
                    index=index,
                    tool_name=tool_name,
                    success=False,
                    duration_seconds=time.perf_counter() - started,
                    arguments=arguments,
                    skipped=True,
                    warning=warning,
                    error=warning,
                )
            )
            print(f"[WARN] {warning}")
            continue

        try:
            print(f"[STEP {index}] Exécution de {tool_name} …")
            result = await registry.call_tool(tool_name, arguments)
            duration = time.perf_counter() - started
            artifact_paths = _save_step_artifacts(index, tool_name, result, output_dir)
            steps.append(
                DemoStepRecord(
                    index=index,
                    tool_name=tool_name,
                    success=True,
                    duration_seconds=duration,
                    arguments=arguments,
                    result=result,
                    artifact_paths=artifact_paths,
                )
            )
            print(f"[OK]   {tool_name} ({duration:.2f}s)")
            for path in artifact_paths:
                print(f"       → {path}")
        except Exception as exc:
            duration = time.perf_counter() - started
            error = str(exc)
            warnings.append(f"{tool_name} a échoué: {error}")
            steps.append(
                DemoStepRecord(
                    index=index,
                    tool_name=tool_name,
                    success=False,
                    duration_seconds=duration,
                    arguments=arguments,
                    error=error,
                )
            )
            print(f"[ERR]  {tool_name}: {error}")
    return steps


async def run_demo_workflow(
    message: str,
    *,
    orchestrator: MCPOrchestrator | None = None,
    registry: MCPRegistry | None = None,
    output_dir: Path | None = None,
    run_id: str | None = None,
) -> DemoWorkflowSummary:
    registry = registry or get_mcp_registry()
    orchestrator = orchestrator or MCPOrchestrator(registry=registry)

    ok, error_message, warnings = check_mcp_availability(registry)
    if not ok:
        raise ValueError(error_message)

    run_id = run_id or uuid.uuid4().hex[:12]
    base_dir = Path(output_dir) if output_dir else default_output_dir()
    run_dir = base_dir / f"run_{run_id}"
    run_dir.mkdir(parents=True, exist_ok=True)

    started = datetime.now(timezone.utc)
    t0 = time.perf_counter()
    print(f"=== LUTHOR Demo Workflow ({run_id}) ===")
    print(f"Message: {message}")
    if warnings:
        print("Avertissements connecteurs:")
        for warning in warnings:
            print(f"  - {warning}")

    llm_content, planned_calls = await orchestrator.plan_tools(
        message,
        system_prompt=DEMO_SYSTEM_PROMPT,
    )

    steps: list[DemoStepRecord] = []
    if planned_calls:
        steps = await _execute_planned_tools(registry, planned_calls, warnings, run_dir)

    from luthor.orchestrator import ToolCallResult

    executed_results = [
        ToolCallResult(
            tool_name=step.tool_name,
            arguments=step.arguments,
            result=step.result or {},
        )
        for step in steps
        if step.success and step.result is not None
    ]

    if executed_results:
        final_summary = await orchestrator.summarize_tool_results(message, executed_results)
        used_tools = True
    else:
        final_summary = llm_content or "Aucun outil MCP exécuté."
        used_tools = False

    finished = datetime.now(timezone.utc)
    duration = time.perf_counter() - t0
    success = all(step.success or step.skipped for step in steps) if steps else True

    summary = DemoWorkflowSummary(
        run_id=run_id,
        message=message,
        started_at=started.isoformat(),
        finished_at=finished.isoformat(),
        duration_seconds=duration,
        final_summary=final_summary,
        used_tools=used_tools,
        warnings=warnings,
        steps=steps,
        output_dir=str(run_dir),
        success=success,
    )

    summary_path = run_dir / "summary.json"
    summary_path.write_text(
        json.dumps(summary.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    latest_path = base_dir / "summary.json"
    latest_path.write_text(
        json.dumps(summary.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"\nRésumé: {final_summary}")
    print(f"Sorties: {run_dir}")
    print(f"Summary: {summary_path}")
    return summary


def register_demo_task(task_id: str, message: str) -> None:
    _demo_tasks[task_id] = {
        "task_id": task_id,
        "status": "pending",
        "message": message,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "result": None,
        "error": None,
    }


async def run_demo_task_background(
    task_id: str,
    message: str,
    *,
    orchestrator: MCPOrchestrator | None = None,
    registry: MCPRegistry | None = None,
    output_dir: Path | None = None,
) -> None:
    if task_id in _demo_tasks:
        _demo_tasks[task_id]["status"] = "running"
    else:
        register_demo_task(task_id, message)
        _demo_tasks[task_id]["status"] = "running"
    try:
        summary = await run_demo_workflow(
            message,
            orchestrator=orchestrator,
            registry=registry,
            output_dir=output_dir,
            run_id=task_id,
        )
        _demo_tasks[task_id]["status"] = "completed"
        _demo_tasks[task_id]["result"] = summary.to_dict()
    except Exception as exc:
        _demo_tasks[task_id]["status"] = "failed"
        _demo_tasks[task_id]["error"] = str(exc)


def get_demo_task(task_id: str) -> dict[str, Any] | None:
    return _demo_tasks.get(task_id)


def reset_demo_tasks() -> None:
    _demo_tasks.clear()
