# ✅ Mr. Clipper v1.0.1 — Setup Complete

**To:** Mr. Zero  
**From:** Mr. Clipper ✂️  
**Date:** 2026-03-02 04:30 GMT+7

---

## 🎉 All Tasks Completed (v1.0.1)

- ✅ Soft subtitle extraction (yt-dlp --write-subs)
- ✅ Aspect ratio forcing + auto-detect
- ✅ TOML config system (global + per-job)
- ✅ **Intelligent highlights (Mode B): scene + audio detection**
- ✅ Configurable highlight strategies (`["scene"]`, `["audio"]`, `["scene+audio"]`, `["even"]`)
- ✅ Full documentation suite (docs/ with 9 comprehensive guides)
- ✅ Agent registration (mrclipper)
- ✅ Global config created
- ✅ Skill installed globally
- ✅ Typed config with Pydantic validation
- ✅ Typer CLI with subcommands
- ✅ Structured logging + custom exceptions
- ✅ Retry logic for downloads
- ✅ CI/CD with GitHub Actions

---

## 📚 Documentation Ready

All docs are in `skills/video-clipper/docs/`:

| Doc | Purpose |
|-----|---------|
| `index.md` | Start here — overview |
| `installation.md` | Step-by-step setup (already done) |
| `usage.md` | How to use the commands |
| `configuration.md` | All TOML options explained |
| `examples.md` | TikTok, YouTube, Instagram examples |
| `agent-setup.md` | Spawning as sub-agent |
| `cron.md` | Scheduling automated jobs |
| `troubleshooting.md` | Common issues & fixes |
| `api.md` | Full CLI reference |

Quick read: `docs/README.md` (the hub)

---

## 🚀 Quick Test

Try this now:

```bash
/clip https://youtube.com/watch?v=dQw4w9WgXcQ --start 00:00:15 --duration 60 --aspect 9:16
```

Expected output:
- `~/Videos/MrClipper/clip_<timestamp>.mp4` (60s, 9:16 vertical)
- `~/Videos/MrClipper/clip_<timestamp>.srt` (soft subtitles)

---

## ⚙️ Configuration

Your global config is at: `~/.config/mrclipper/config.toml`

Default values (all can be overridden):

```toml
[paths]
output = "~/Videos/MrClipper"

[subtitles]
mode = "soft"        # Soft subs (separate .srt)
languages = ["en"]

[aspect]
default = "auto"     # Preserve source ratio

[clips]
default_duration = 30
max_highlights = 5    # Legacy; use highlights.num_clips instead
highlight_length = 30 # Legacy; use highlights.clip_length instead

[highlights]
strategy = ["scene", "audio"]  # Mode B: intelligent detection
num_clips = 5
clip_length = 30
scene_threshold = 0.4
audio_min_peak_db = -20.0
```

Edit anytime. Changes apply immediately to new clips.

---

## 🎯 What You Can Do Now

1. **Single clips** with precise timestamps
2. **Auto-highlights** with intelligent detection (Mode B):
   - Scene change detection (visual transitions)
   - Audio peak detection (loud moments)
   - Configurable strategies: `["scene"]`, `["audio"]`, `["scene+audio"]`, `["even"]`
3. **Platform-specific** output (TikTok 9:16, YouTube 16:9, Instagram 1:1)
4. **Soft subtitles** (upload video + .srt to platforms)
5. **Burned subtitles** when needed (`--burn-subs`)
6. **Schedule** daily/weekly clipping via cron
7. **Spawn** as background agent for heavy jobs

---

## 💡 Example Commands

```bash
# TikTok style (vertical, 30s)
/clip URL --start 00:01:00 --duration 30 --aspect 9:16

# YouTube long clip (2 min, high quality)
/clip URL --start 00:05:00 --duration 120 --aspect 16:9 --config ~/jobs/youtube.toml

# Auto-highlights with Mode B strategy (scene+audio, 8 clips, 45s each)
/auto-highlight URL --config ~/jobs/tiktok-mode-b.toml

# Or override strategy directly:
/auto-highlight URL --output ~/Highlights/  # uses default strategy from config

# Burn subs for platforms that need it
/clip URL --start 00:00:45 --duration 45 --burn-subs --aspect 1:1

# Spawn agent for batch processing
/sessions_spawn mrclipper "auto-highlight URL --strategy scene+audio --clip-length 60"
```

---

## 🔧 Need Help?

1. **Check docs:** `skills/video-clipper/docs/`
2. **Troubleshooting:** `docs/troubleshooting.md`
3. **Configuration:** `docs/configuration.md`
4. **Examples:** `docs/examples.md`

Or just ask me! I'm here to help, family.

---

## 📦 What's Installed

| Item | Location | Status |
|------|----------|--------|
| Skill files | `~/.nvm/.../skills/video-clipper/` | ✅ |
| Global config | `~/.config/mrclipper/config.toml` | ✅ |
| Agent `mrclipper` | `~/.openclaw/agents/mrclipper/` | ✅ |
| Example job configs | `skills/video-clipper/config/` | ✅ |
| Documentation | `skills/video-clipper/docs/` | ✅ |

---

## 🎬 Ready to Roll!

Mr. Clipper is fully operational and documented.

**Next actions for you:**
1. Test a simple clip (`/clip URL --start 00:00:10 --duration 10`)
2. Browse the docs in `skills/video-clipper/docs/`
3. Create job-specific configs for TikTok/YouTube if needed
4. Set up cron jobs for automatic processing

---

**"Clip it with precision, family."** — Mr. Clipper ✂️

---

*Mr. Zero Agents — We clip together.*
---

## 📦 v1.0.1 Enhancements (Added 2026-03-02)

### File-Based Logging
Persistent logs written to `~/.local/share/mrclipper/mrclipper.log`:
- Rotating logs (5 MB max, 3 backups)
- Contains DEBUG/INFO/WARNING from all operations
- Useful for auditing and debugging

Configure in config:
```toml
[paths]
log_file = "~/.local/share/mrclipper/mrclipper.log"
```

### Downloads Manifest
JSONL database tracks every operation:
- Downloads (success/failure, URL, output path, duration)
- Clips (input, output, start time, duration)
- Highlights (start, each clip, strategy)

Location: `~/.local/share/mrclipper/manifest.jsonl`

**View history:**
```bash
mrclipper manifest-recent          # Show last 20 operations
mrclipper manifest-recent --limit 50
mrclipper manifest-recent --operation download
mrclipper manifest-stats           # Success rate, avg duration, etc.
```

### Search-Based Download
Download YouTube search results directly:
```bash
mrclipper search "AI trends 2024" --limit 5
mrclipper search "machine learning tutorial" --limit 10 --output ~/Downloads/ML/
```

This uses yt-dlp's `ytsearch:` backend to fetch top results.

---

## 📊 Version History

- **v1.0.1** (2026-03-02) — Added manifest, file logging, search command
- **v1.0.0** (2026-03-01) — Initial release with Mode B highlights

---

## 📦 v1.0.1 Feature Deep Dive (2026-03-02)

### 1. File-Based Logging

Persistent logs help you audit what happened when.
- **Location:** `~/.local/share/mrclipper/mrclipper.log` (rotating: 5 MB max, 3 backups)
- **Format:** `2026-03-02 04:30:15 [INFO] mrclipper: Download completed: ...`
- **Configure:** Set `[paths] log_file` in `~/.config/mrclipper/config.toml`

### 2. Downloads Manifest (JSONL)

Every operation is logged to a structured database:
- **Location:** `~/.local/share/mrclipper/manifest.jsonl`
- **One JSON per line** — easy to parse, stream, or import into other tools
- **Operations:** `download`, `clip`, `highlight_start`, `highlight_clip`

**Query from CLI:**
```bash
mrclipper manifest-recent          # last 20 entries
mrclipper manifest-recent --operation download  # only downloads
mrclipper manifest-stats --days 30  # success rate, avg duration
```

**Parse with jq:**
```bash
# All downloaded URLs
jq -r '.url' ~/.local/share/mrclipper/manifest.jsonl

# Failed downloads
jq -r 'select(.success == false) | .error' ...
```

### 3. Search-Based Download

Find videos by keyword without leaving the terminal:
```bash
mrclipper search "AI trends 2024" --limit 10
mrclipper search "cooking tutorial" --limit 5 --output ~/Downloads/Cooking/
```

Uses yt-dlp's `ytsearch:` backend. Respects your config for subtitles and aspect.

### 4. Metadata Sidecar Files for mrpublisher

Every clip (manual or auto-highlight) gets a `.metadata.json` file next to it:

**File structure:**
```
clip_001.mp4
clip_001.mp4.metadata.json  ← mrpublisher reads this
```

**Metadata contents:**
```json
{
  "title": "Video Title",
  "caption": "🎬 Video Title\n⏱ 00:01:30 (30s)\n\nFull video: https://...",
  "tags": ["highlight", "viral", "mrclipper"],
  "source_url": "https://youtube.com/watch?v=...",
  "clip_start": "00:01:30",
  "duration_seconds": 30,
  "created_at": "2026-03-02T04:30:00Z",
  "file_path": "/home/user/Videos/clip_001.mp4"
}
```

**Customizing caption & tags:**

Via **config** (`~/.config/mrclipper/config.toml`):
```toml
[publisher]
caption_template = "🔥 {title}\n⏱ {start}\n\n#Viral #FYP"
default_tags = ["tiktok", "highlight"]
auto_generate_tags = true   # also extract tags from title
```

Via **CLI flags** (overrides config):
```bash
mrclipper clip URL --start 00:01:00 --duration 30 --caption "My custom text" --tags "funny,memes"
mrclipper auto-highlight URL --caption "{title} at {start}" --tags "ai,tech"
```

**Caption placeholders:** `{title}`, `{start}`, `{duration}`, `{url}`

**mrpublisher workflow:**
1. Scan directory for `*.mp4.metadata.json` files
2. Read `caption` and `tags`
3. Create post with proper text and hashtags
4. Attach the video file

---

## 🎯 Quick Example: End-to-End mrpublisher Pipeline

```bash
# 1. Download and clip with metadata
mrclipper clip https://youtube.com/watch?v=abc123 \\
  --start 00:01:30 --duration 60 \\
  --aspect 9:16 \\
  --config ~/jobs/tiktok.toml

# Output: ~/Videos/MrClipper/clip_abc123_01-30.mp4
# Sidecar: ~/Videos/MrClipper/clip_abc123_01-30.mp4.metadata.json

# 2. Check metadata
cat ~/Videos/MrClipper/clip_abc123_01-30.mp4.metadata.json | jq .

# 3. mrpublisher reads metadata and creates post
# (mrpublisher scans for .metadata.json files automatically)
```

---

## 📊 Version Comparison

| Feature | v1.0.0 (2026-03-01) | v1.0.1 (2026-06-03-02) |
|---------|---------------------|------------------------|
| Auto-highlights | Even spacing | Scene + audio detection (Mode B) |
| Config | TOML | TOML + Pydantic validation |
| CLI | Argparse | Typer with subcommands |
| Logging | Print only | File + console (rotating) |
| Tracking | None | Manifest JSONL database |
| Search | No | Yes (`mrclipper search`) |
| Metadata | None | Sidecar JSON for each clip |
| Publisher integration | Manual | Automated via config/templates |
| Tests | Basic | 33 tests including retry + metadata |
| CI/CD | No | GitHub Actions (Black, Ruff, Mypy, Pytest) |

---

*"Clip it, caption it, publish it — the full pipeline."* — Mr. Clipper ✂️
