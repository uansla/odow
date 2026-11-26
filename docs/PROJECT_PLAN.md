# Project Plan

## Goal
Build a small desktop application for four focused workflows: YouTube/Bilibili video downloads, Hugging Face model repository downloads, and GitHub software release downloads.

## First release
- PySide6-Essentials desktop shell; the Video tab is implemented with URL, quality, destination, cookies, progress, speed, and cancellation controls.
- yt-dlp for YouTube and Bilibili extraction and downloads. Keep media post-processing optional and document ffmpeg and JavaScript-runtime requirements.
- Hugging Face Hub client for public model repositories, revision selection, and optional file filters. Private/gated repositories use a user-provided token.
- GitHub REST API for public release listing and asset downloads. Distinguish release assets from source archives; support an optional user token for private repositories/rate limits.
- Persist task metadata and user preferences locally. Keep secrets out of ordinary config and logs.
- Report progress, speed, status, destination, errors; support cancel/retry where the underlying downloader permits it.

## Architecture
- `ui`: Qt widgets and user interaction only.
- `downloaders`: one adapter per source, normalized task events/results.
- `services`: task orchestration, persistence, and credential handling.
- `models`: typed task state and source options.

Network work must run outside the UI thread. Each adapter should expose validation, start, progress callbacks, cancellation, and clear error mapping. Do not bypass platform access controls; users supply their own authorized credentials where needed.

## Delivery milestones
1. Establish the desktop shell, settings, and task model.
2. Implement and test the yt-dlp video workflow. (Implementation is in place; live test downloads remain environment-dependent.)
3. Add Hugging Face model repository download.
4. Add GitHub release metadata and asset download.
5. Add persistence, packaging, and platform-specific verification.

## Initial non-goals
No browser integration, media library, conversion suite, account management, or arbitrary website downloader. No credential scraping or access-control circumvention.

## Validation
Use public test resources and mocked API responses. Cover malformed URLs, network interruption, cancellation, filename collisions, unavailable disk space, and expired/invalid credentials. Package only after each adapter's third-party licenses and external runtime requirements are documented.
