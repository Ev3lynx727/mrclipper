# Mr. Clipper Documentation

**Version:** 1.0.1  
**Family:** Mr. Zero Agents  
**Emoji:** ✂️

Welcome to Mr. Clipper's documentation hub. This covers everything from installation to advanced usage.

## Quick Navigation

- [Installation](installation.md) - Get up and running
- [User Guide](usage.md) - How to use Mr. Clipper
- [Configuration](configuration.md) - TOML config reference
- [Examples](examples.md) - Real-world use cases
- [Agent Setup](agent-setup.md) - Spawning Mr. Clipper as a sub-agent
- [Cron Scheduling](cron.md) - Automate your clipping tasks
- [Troubleshooting](troubleshooting.md) - Common issues and fixes
- [API Reference](api.md) - Command-line options and flags

## What is Mr. Clipper?

Mr. Clipper is a specialized video processing agent that:
- Downloads videos from YouTube and generic URLs
- Clips videos by precise timestamps
- Extracts subtitles (soft or burned-in)
- Handles aspect ratio conversion (16:9, 9:16, etc.)
- Auto-generates highlights using scene + audio detection (Mode B)
- Tracks all operations in manifest and logs
- Generates metadata sidecars for `mrpublisher` integration
- Supports both manual and scheduled (cron) operation

Built for the Mr. Zero Agents family with ❤️.

## Features at a Glance

| Feature | Status | Notes |
|---------|--------|-------|
| YouTube/generic URL download | ✅ | yt-dlp powered |
| Manual clipping | ✅ | `--start` + `--duration` |
| Auto-highlights (Mode B) | ✅ | Scene + audio detection |
| Soft subtitles | ✅ | Separate `.srt` files |
| Burned subtitles | ✅ | Re-encode with subs |
| Aspect ratio control | ✅ | 16:9, 9:16, 1:1, 4:3, auto |
| Search & download | ✅ | `mrclipper search "query"` |
| File-based logging | ✅ | Rotating logs |
| Downloads manifest | ✅ | JSONL database |
| Metadata sidecars | ✅ | For mrpublisher |
| TOML configuration | ✅ | Global + per-job |
| Cron support | ✅ | Built-in scheduling |
| Sub-agent spawning | ✅ | `sessions_spawn mrclipper` |

## Requirements

- `ffmpeg` (with libx264)
- `ffprobe`
- `yt-dlp`
- `python3` 3.10+
- `toml` Python package

All dependencies are already installed on this system.

## Getting Started

1. Copy the skill to OpenClaw skills directory (already done ✅)
2. Create global config: `~/.config/mrclipper/config.toml` (already created ✅)
3. Try a test clip:

```bash
/clip https://youtube.com/watch?v=dQw4w9WgXcQ --start 00:00:15 --duration 30 --aspect 9:16
```

That's it! Read the [User Guide](usage.md) for more.

---

*"Clip it with precision, family."* — Mr. Clipper ✂️