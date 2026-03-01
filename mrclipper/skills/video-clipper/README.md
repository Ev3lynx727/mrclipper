# Mr. Clipper Skill

Quick reference for the OpenClaw skill wrapper.

## What is this?

This folder (`skills/video-clipper/`) is the OpenClaw integration for [Mr. Clipper](https://github.com/YOUR_USERNAME/mrclipper).

## Installation

1. Ensure `mrclipper` CLI is installed:
   ```bash
   pip install mrclipper
   ```

2. Copy this folder to OpenClaw skills:
   ```bash
   cp -r video-clipper ~/.openclaw/workspace/skills/
   ```

3. Restart OpenClaw or reload skills.

## Usage in OpenClaw

- `/clip URL --start 00:01:00 --duration 30`
- `/auto-highlight URL --strategy scene+audio`

See `SKILL.md` for full command reference.

## Configuration

Copy example config from `config/` to `~/.config/mrclipper/config.toml`.

## Documentation

Full docs are in `docs/` (symlink to main project docs) or online at the GitHub repo.

## Requirements

- Python 3.10+
- `mrclipper` package (provides CLI)
- FFmpeg + ffprobe
- yt-dlp

---

*Mr. Clipper v1.0.1 — Mr. Zero Agents family*