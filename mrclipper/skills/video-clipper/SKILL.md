# Mr. Clipper Skill

OpenClaw skill wrapper for the Mr. Clipper video clipping CLI.

## Overview

This skill provides OpenClaw commands that invoke the `mrclipper` CLI tool:

- `/clip` — Manual video clipping with start/duration
- `/auto-highlight` — Intelligent highlight extraction (Mode B)

## Prerequisites

- `mrclipper` CLI must be installed and available in PATH
  ```bash
  pip install mrclipper
  ```

## Installation

Copy this directory to your OpenClaw skills folder:

```bash
# If you cloned the mrclipper repository:
cp -r mrclipper/skills/video-clipper ~/.openclaw/workspace/skills/

# Or from GitHub Releases, extract mrclipper-skill-vX.Y.Z.zip to skills/
```

## Configuration

Example configs are in `config/`. Copy one to `~/.config/mrclipper/config.toml` and customize.

See full documentation: [mrclipper/docs/](../../mrclipper/docs/)

## Commands

### `/clip URL [OPTIONS]`

Download and clip a video.

Options:
- `--start` — Clip start time (HH:MM:SS)
- `--duration` — Clip duration in seconds
- `--aspect` — Output aspect ratio (e.g., 9:16, 1:1)
- `--caption` — Override caption text
- `--tags` — Override tags (comma-separated)

Example:
```
/clip https://youtube.com/watch?v=abc123 --start 00:01:00 --duration 30 --aspect 9:16
```

### `/auto-highlight URL [OPTIONS]`

Automatically detect and extract highlights (Mode B).

Options:
- `--output` — Output directory (default: ~/Videos/MrClipper)
- `--strategy` — Detection strategy: scene, audio, scene+audio, even
- `--num-clips` — Number of highlights to extract
- `--clip-length` — Target clip length in seconds
- `--caption`, `--tags` — Override metadata

Example:
```
/auto-highlight https://youtube.com/watch?v=xyz --strategy scene+audio --num-clips 5
```

## Metadata Sidecars

Each clip generates a `.mp4.metadata.json` file with caption and tags for `mrpublisher`.

## Logs

Logs are written to `~/.local/share/mrclipper/mrclipper.log` (rotating).

## Support

See `mrclipper/docs/` for full documentation, configuration reference, and troubleshooting.

Issues: https://github.com/YOUR_USERNAME/mrclipper/issues

---

*Part of the Mr. Zero Agents family. ✂️*