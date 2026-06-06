from __future__ import annotations

import asyncio
import base64
import os
import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx


class WhisperConnector:
    """Local speech-to-text via faster-whisper."""

    def __init__(
        self,
        model_size: str | None = None,
        device: str | None = None,
    ):
        self.model_size = model_size or os.getenv("WHISPER_MODEL_SIZE", "tiny")
        self.device = device or os.getenv("WHISPER_DEVICE", "cpu")
        self._model: Any = None

    @property
    def enabled(self) -> bool:
        return self.model_size in {"tiny", "base", "small", "medium", "large"}

    def _load_model(self) -> Any:
        if self._model is None:
            from faster_whisper import WhisperModel

            compute_type = "int8" if self.device == "cpu" else "float16"
            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=compute_type,
            )
        return self._model

    async def _resolve_audio_path(self, audio_path_or_url: str) -> tuple[str, bool]:
        parsed = urlparse(audio_path_or_url)
        if parsed.scheme in {"http", "https"}:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(audio_path_or_url)
                response.raise_for_status()
            suffix = Path(parsed.path).suffix or ".wav"
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            temp_file.write(response.content)
            temp_file.close()
            return temp_file.name, True

        path = Path(audio_path_or_url)
        if not path.exists():
            raise ValueError(f"Audio file not found: {audio_path_or_url}")
        return str(path), False

    def _transcribe_file(self, audio_path: str, language: str | None) -> str:
        model = self._load_model()
        segments, _ = model.transcribe(audio_path, language=language)
        return " ".join(segment.text.strip() for segment in segments).strip()

    async def transcribe_audio(
        self,
        audio_path_or_url: str,
        language: str | None = None,
    ) -> dict[str, Any]:
        if not self.enabled:
            raise ValueError("Whisper connector is not configured")

        audio_path, is_temp = await self._resolve_audio_path(audio_path_or_url)
        try:
            text = await asyncio.to_thread(self._transcribe_file, audio_path, language)
        finally:
            if is_temp:
                Path(audio_path).unlink(missing_ok=True)

        return {
            "text": text,
            "language": language,
            "model": self.model_size,
        }

    async def transcribe_base64(
        self,
        audio_b64: str,
        language: str | None = None,
        suffix: str = ".wav",
    ) -> dict[str, Any]:
        if not self.enabled:
            raise ValueError("Whisper connector is not configured")

        audio_bytes = base64.b64decode(audio_b64)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp_file.write(audio_bytes)
        temp_file.close()
        try:
            text = await asyncio.to_thread(self._transcribe_file, temp_file.name, language)
        finally:
            Path(temp_file.name).unlink(missing_ok=True)

        return {
            "text": text,
            "language": language,
            "model": self.model_size,
        }
