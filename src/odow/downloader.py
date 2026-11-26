"""yt-dlp video download worker and option helpers."""

from __future__ import annotations

import shutil
import sys
import threading
from pathlib import Path
from typing import Callable
from urllib.parse import urlsplit

from PySide6.QtCore import QThread, Signal
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadCancelled


QUALITY_FORMATS = {
    "Best available": "bestvideo*+bestaudio/best",
    "1080p max": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
    "720p max": "bestvideo[height<=720]+bestaudio/best[height<=720]",
    "480p max": "bestvideo[height<=480]+bestaudio/best[height<=480]",
    "Audio only (MP3)": "bestaudio/best",
}


def is_supported_video_url(url: str) -> bool:
    host = (urlsplit(url).hostname or "").lower().rstrip(".")
    return (
        host == "youtu.be" or host == "youtube.com" or host.endswith(".youtube.com")
        or host == "b23.tv" or host == "bilibili.com" or host.endswith(".bilibili.com")
    )


def bundled_tool(name: str) -> str | None:
    """Find a tool bundled by PyInstaller or installed on the system."""
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
    for candidate in (root / name, root / f"{name}.exe"):
        if candidate.is_file():
            return str(candidate)
    environment_tool = Path(sys.prefix) / "bin" / name
    if environment_tool.is_file():
        return str(environment_tool)
    return shutil.which(name)


def build_options(
    destination: str,
    quality: str,
    cookie_file: str = "",
    progress_hook: Callable[[dict], None] | None = None,
    cancel_event: threading.Event | None = None,
) -> dict:
    """Build consistent yt-dlp options, also used by unit tests."""
    if quality not in QUALITY_FORMATS:
        raise ValueError(f"Unsupported quality: {quality}")
    output: dict = {
        "format": QUALITY_FORMATS[quality],
        "outtmpl": str(Path(destination) / "%(title).180B [%(id)s].%(ext)s"),
        "windowsfilenames": True,
        "noplaylist": True,
        "continuedl": True,
        "retries": 10,
        "fragment_retries": 10,
        "socket_timeout": 30,
        "quiet": True,
        "no_warnings": False,
        "progress_hooks": [progress_hook] if progress_hook else [],
    }
    if quality == "Audio only (MP3)":
        output["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]
    ffmpeg = bundled_tool("ffmpeg")
    if ffmpeg:
        output["ffmpeg_location"] = ffmpeg
    deno = bundled_tool("deno")
    if deno:
        output["js_runtimes"] = {"deno": {"path": deno}}
    if cookie_file:
        output["cookiefile"] = cookie_file
    if cancel_event is not None:
        def check_cancel(data: dict) -> None:
            if cancel_event.is_set():
                raise DownloadCancelled()

        output["progress_hooks"].append(check_cancel)
    return output


class VideoDownloadWorker(QThread):
    progress = Signal(int, str)
    completed = Signal(str)
    failed = Signal(str)
    cancelled = Signal()

    def __init__(self, url: str, destination: str, quality: str, cookie_file: str = "") -> None:
        super().__init__()
        self.url = url.strip()
        self.destination = destination
        self.quality = quality
        self.cookie_file = cookie_file
        self._cancel_event = threading.Event()

    def cancel(self) -> None:
        self._cancel_event.set()

    def run(self) -> None:
        Path(self.destination).mkdir(parents=True, exist_ok=True)

        def on_progress(data: dict) -> None:
            if data.get("status") == "downloading":
                total = data.get("total_bytes") or data.get("total_bytes_estimate") or 0
                downloaded = data.get("downloaded_bytes", 0)
                percent = int(downloaded * 100 / total) if total else 0
                speed = data.get("speed")
                speed_text = f"{speed / 1024 / 1024:.2f} MB/s" if speed else "正在计算速度…"
                self.progress.emit(min(percent, 100), speed_text)
            elif data.get("status") == "finished":
                self.progress.emit(100, "正在合并或处理媒体…")

        try:
            options = build_options(
                self.destination, self.quality, self.cookie_file,
                progress_hook=on_progress, cancel_event=self._cancel_event,
            )
            with YoutubeDL(options) as downloader:
                result = downloader.download([self.url])
            if self._cancel_event.is_set():
                self.cancelled.emit()
            elif result == 0:
                self.completed.emit(self.destination)
            else:
                self.failed.emit("下载内核返回错误，请检查视频链接或日志。")
        except DownloadCancelled:
            self.cancelled.emit()
        except Exception as exc:
            self.failed.emit(str(exc))
