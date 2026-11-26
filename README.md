# Odow

Odow is a focused desktop downloader for YouTube and Bilibili videos, Hugging Face model repositories, and GitHub release assets.

## Current status

The repository contains the initial PySide6 application shell and architecture plan. Download adapters and task orchestration are not implemented yet.

## Requirements

- Python 3.10+
- Optional `ffmpeg` for audio/video post-processing
- A JavaScript runtime may be required by yt-dlp for some YouTube extraction paths

## Run from source

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -e .
odow
```

## Scope and architecture

See [docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md) for the first-release scope, adapter boundaries, milestones, and validation plan. Network operations will run outside the Qt UI thread. Use only resources and credentials you are authorized to access.
