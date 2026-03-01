# Documentation Hub

This directory contains comprehensive documentation for Mr. Clipper v1.0.0.

## 📚 Docs Index

| File | Purpose |
|------|---------|
| [index.md](index.md) | **Start here** — overview and quick navigation |
| [installation.md](installation.md) | Step-by-step install guide |
| [usage.md](usage.md) | How to use Mr. Clipper (clipping, subtitles, aspect) |
| [configuration.md](configuration.md) | TOML config reference (all options) |
| [examples.md](examples.md) | Real-world use cases (TikTok, YouTube, etc.) |
| [agent-setup.md](agent-setup.md) | Spawning as sub-agent, workspace, best practices |
| [cron.md](cron.md) | Scheduling automated clipping jobs |
| [troubleshooting.md](troubleshooting.md) | Common issues and fixes |
| [api.md](api.md) | Command-line reference, exit codes, Python API |

---

## Quick Start

1. **Install** → See [installation.md](installation.md)
2. **Configure** → Edit `~/.config/mrclipper/config.toml`
3. **Use** → Read [usage.md](usage.md) and try:

```bash
/clip URL --start 00:01:00 --duration 60 --aspect 9:16
```

---

## Overview

Mr. Clipper is a video clipping agent that:
- Downloads from YouTube/generic URLs
- Extracts clips by timestamp
- Handles subtitles (soft or burned)
- Converts aspect ratios (16:9, 9:16, etc.)
- Auto-generates highlights
- Supports cron scheduling and sub-agent spawning

Built for Mr. Zero Agents family. Warm, friendly, efficient. ✂️

---

## Version

**Current:** 1.0.0  
**Release Date:** 2026-03-01

---

**Need help?** Start with [Troubleshooting](troubleshooting.md) or check the [Usage Guide](usage.md).