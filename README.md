# Odow

Odow is a lightweight desktop downloader. The current build implements YouTube and Bilibili video downloads using yt-dlp.

## Debian 13 / Python 3.13

Install Debian's FFmpeg package and the project dependencies. The yt-dlp deno extra installs Deno into the Python environment, and the default extra includes yt-dlp-ejs.

    sudo apt update
    sudo apt install ffmpeg
    /home/software/.venv-3.13/bin/python -m pip install -e '.[build,test]'

MP3 extraction uses FFmpeg.

## Run from source

    /home/software/.venv-3.13/bin/python -m odow.app

## Build

Install ffmpeg from Debian, then run ./scripts/build_debian.sh. The script locates Deno in the configured Python environment and bundles it; ffmpeg remains a Debian system dependency. Review third-party licenses before redistribution.

## Video features

- Best available, 1080p, 720p, 480p, or MP3 audio-only extraction.
- Resumable downloads, retries, progress/speed reporting, and cancellation.
- Optional Netscape-format cookies.txt for content you are authorized to access.
- One video at a time; playlists are disabled.

See docs/PROJECT_PLAN.md for remaining milestones.
