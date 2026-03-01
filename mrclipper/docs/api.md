# API Reference

Command-line interface reference for Mr. Clipper.

---

## Main Command

```bash
mrclipper [OPTIONS] COMMAND [ARGS]...
```

Or from OpenClaw:

```
/clip <url> [options]
/auto-highlight <url> [options]
/search "query" [options]
/manifest-recent [options]
/manifest-stats [options]
```

---

## Global Options

These apply to all commands:

| Option | Type | Description |
|--------|------|-------------|
| `--version, -V` | flag | Show version and exit |
| `--verbose, -v` | flag | Enable debug logging |
| `--quiet, -q` | flag | Suppress info logs (warnings only) |
| `--help` | flag | Show help message |

---

## Commands

### `clip` — Manual Video Clipping

Extract a specific segment from a video.

```bash
mrclipper clip URL --start HH:MM:SS --duration SECONDS [OPTIONS]
```

**Arguments:**
- `url` — Video URL (YouTube or supported site)

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--start, -s` | string | **required** | Start time (HH:MM:SS) |
| `--duration, -d` | integer | 30 | Clip length in seconds |
| `--output, -o` | path | from config | Output file path |
| `--config, -c` | path | global config | Job-specific TOML config |
| `--aspect, -a` | string | `auto` | Target aspect ratio: `auto`, `source`, `16:9`, `9:16`, `1:1`, `4:3` |
| `--burn-subs` | flag | false | Burn subtitles into video (re-encode) |
| `--caption` | string | from config | Custom caption for metadata (overrides config) |
| `--tags` | string | from config | Comma-separated tags for metadata (overrides config) |

**Example:**
```bash
mrclipper clip https://youtube.com/watch?v=abc123 --start 00:01:30 --duration 60 --aspect 9:16
```

---

### `auto-highlight` — Intelligent Highlights

Automatically detect and extract multiple highlight clips using scene + audio detection (Mode B).

```bash
mrclipper auto-highlight URL [OPTIONS]
```

**Arguments:**
- `url` — Video URL

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--output, -o` | path | from config | Output directory for clips |
| `--config, -c` | path | global config | Job-specific TOML config |
| `--caption` | string | from config | Custom caption template (overrides config) |
| `--tags` | string | from config | Comma-separated tags (overrides config) |

**Example:**
```bash
mrclipper auto-highlight https://youtube.com/watch?v=xyz --output ~/Highlights/ --config ~/jobs/tiktok.toml
```

---

### `search` — YouTube Search & Download

Find videos by keyword and download top results.

```bash
mrclipper search "QUERY" [OPTIONS]
```

**Arguments:**
- `query` — Search query string

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--limit, -l` | integer | 5 | Number of results to download |
| `--output, -o` | path | from config | Output directory |
| `--config, -c` | path | global config | Job-specific TOML config |

**Example:**
```bash
mrclipper search "AI trends 2024" --limit 10 --output ~/Downloads/AI/
```

---

### `manifest-recent` — Show Recent Operations

Display recent entries from the downloads manifest.

```bash
mrclipper manifest-recent [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--limit, -n` | integer | 20 | Number of entries to show |
| `--operation, -o` | string | none | Filter by operation type (`download`, `clip`, `highlight_start`, `highlight_clip`) |

**Example:**
```bash
mrclipper manifest-recent --limit 50 --operation download
```

---

### `manifest-stats` — Show Manifest Statistics

Display success rates and timing statistics.

```bash
mrclipper manifest-stats [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--days, -d` | integer | 7 | Number of days to include in stats |

**Example:**
```bash
mrclipper manifest-stats --days 30
```

---

### `config-validate` — Validate Configuration

Check a TOML config file for errors.

```bash
mrclipper config-validate [PATH]
```

**Arguments:**
- `path` — Path to config TOML (default: `~/.config/mrclipper/config.toml`)

**Example:**
```bash
mrclipper config-validate ~/.config/mrclipper/config.toml
mrclipper config-validate ~/jobs/tiktok.toml
```

---

## Configuration Reference

See [Configuration](configuration.md) for complete TOML options.

### Key Sections

| Section | Purpose |
|---------|---------|
| `[paths]` | Directories: `workdir`, `output`, `log_file` |
| `[subtitles]` | Subtitle mode (`soft`, `burn`, `none`) and languages |
| `[aspect]` | Default aspect ratio and padding color |
| `[clips]` | Legacy clip settings (use `[highlights]` for auto) |
| `[highlights]` | Mode B: `strategy`, `num_clips`, `clip_length`, detection thresholds |
| `[publisher]` | mrpublisher integration: `caption_template`, `default_tags`, `auto_generate_tags` |
| `[manifest]` | Manifest tracking: `enabled`, `path` |
| `[yt-dlp]` | YouTube download format selector |

---

## File Outputs

### Manual Clip (`clip`)

```
<output_dir>/
  ├── clip_<timestamp>_<start>.mp4
  ├── clip_<timestamp>_<start>.srt  (if soft subs)
  └── clip_<timestamp>_<start>.mp4.metadata.json  (caption + tags)
```

### Auto-Highlights (`auto-highlight`)

```
<output_dir>/
  ├── highlight_0000.mp4
  ├── highlight_0000.mp4.metadata.json
  ├── highlight_0001.mp4
  └── ...
```

---

## Logs & Manifest

- **Log file:** `~/.local/share/mrclipper/mrclipper.log` (rotating, 5 MB)
- **Manifest:** `~/.local/share/mrclipper/manifest.jsonl` (JSON lines)

Configure paths in `[paths]` and `[manifest]`.

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error (see stderr) |
| 2 | Invalid usage (missing args, bad options) |

---

## Examples by Use Case

See [Examples](examples.md) for complete workflows.

---

*Last updated: v1.0.1 (2026-03-02)*
