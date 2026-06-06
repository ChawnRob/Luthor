from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from luthor.config import MCPConnectorConfig

_YTDLP_INSTALL_HINT = (
    "yt-dlp is required for media downloads. "
    "Install dependencies with: make install  (or pip install -r requirements.txt)"
)


def _get_yt_dlp():
    try:
        import yt_dlp
    except ImportError as exc:
        raise ImportError(_YTDLP_INSTALL_HINT) from exc
    return yt_dlp


class YtDlpConnector:
    """Media download and metadata extraction via yt-dlp."""

    def __init__(self, config: MCPConnectorConfig | None = None):
        self.config = config or MCPConnectorConfig()
        self.download_dir = Path(
            self.config.download_dir or os.getenv("YTDLP_DOWNLOAD_DIR", "./data/downloads")
        )
        self.allowed_domains = list(
            self.config.allowed_domains
            or ["youtube.com", "youtu.be", "vimeo.com"]
        )
        self.max_downloads_per_user = int(
            self.config.max_downloads_per_user
            or int(os.getenv("YTDLP_MAX_DOWNLOADS_PER_USER", "10"))
        )
        self._user_counts: dict[str, int] = {}

    @property
    def enabled(self) -> bool:
        return True

    def _validate_url(self, url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            raise ValueError("Only http/https URLs are supported")
        host = (parsed.hostname or "").lower().removeprefix("www.")
        if not any(host == domain or host.endswith(f".{domain}") for domain in self.allowed_domains):
            raise ValueError(f"Domain not allowed: {host}")

    def _check_quota(self, user_id: str) -> None:
        count = self._user_counts.get(user_id, 0)
        if count >= self.max_downloads_per_user:
            raise ValueError(f"Download quota exceeded for user '{user_id}'")

    def _increment_quota(self, user_id: str) -> None:
        self._user_counts[user_id] = self._user_counts.get(user_id, 0) + 1

    def _base_opts(self, output_template: str | None = None) -> dict[str, Any]:
        self.download_dir.mkdir(parents=True, exist_ok=True)
        return {
            "outtmpl": output_template
            or str(self.download_dir / "%(title)s.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
        }

    def _extract_info_sync(self, url: str) -> dict[str, Any]:
        yt_dlp = _get_yt_dlp()
        self._validate_url(url)
        with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}) as ydl:
            info = ydl.extract_info(url, download=False)
        return {
            "title": info.get("title"),
            "duration": info.get("duration"),
            "description": info.get("description"),
            "uploader": info.get("uploader"),
            "webpage_url": info.get("webpage_url", url),
        }

    def _download_media_sync(
        self,
        url: str,
        output_template: str | None = None,
        format: str | None = None,
    ) -> str:
        yt_dlp = _get_yt_dlp()
        self._validate_url(url)
        opts = self._base_opts(output_template)
        if format:
            opts["format"] = "bestaudio/best" if format == "mp3" else format
            if format == "mp3":
                opts["postprocessors"] = [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ]
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(info)
            if format == "mp3":
                path = str(Path(path).with_suffix(".mp3"))
        return path

    async def extract_info(self, url: str) -> dict[str, Any]:
        return await asyncio.to_thread(self._extract_info_sync, url)

    async def download_media(
        self,
        url: str,
        *,
        output_template: str | None = None,
        format: str | None = None,
        user_id: str = "default",
    ) -> dict[str, Any]:
        self._check_quota(user_id)
        path = await asyncio.to_thread(
            self._download_media_sync,
            url,
            output_template,
            format,
        )
        self._increment_quota(user_id)
        return {"path": path, "url": url, "format": format or "best"}
