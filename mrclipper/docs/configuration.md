# Configuration Reference

Complete TOML configuration options for Mr. Clipper.

## Config File Locations

- **Global:** `~/.config/mrclipper/config.toml` (applies to all runs)
- **Job:** `--config /path/to/job.toml` (overrides global)

Both files use the same format.

## Configuration Schema

### `[output]`

Video output settings.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `format` | string | `"mp4"` | Output container format |
| `codec` | string | `"libx264"` | Video codec (libx264, libx265, etc.) |
| `crf` | integer | `23` | Quality (18=best, 28=worst, 23=default) |
| `preset` | string | `"fast"` | Encoding speed: ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow |

### `[paths]`

File system paths.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `workdir` | string | `"/tmp/vr-clipper"` | Temporary download/processing directory |
| `output` | string | `"/tmp/vr-clipper/clips"` | Default output directory for clips |
| `log_file` | string | `"~/.local/share/mrclipper/mrclipper.log"` | Persistent log file (rotating, max 5MB, 3 backups) |

**Note:** Paths can use `~` for home directory.

### `[subtitles]`

Subtitle handling.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `mode` | string | `"soft"` | `"soft"` (separate file), `"burn"` (embed), `"none"` |
| `languages` | array | `["en"]` | Subtitle language codes to download (e.g., `["en", "id"]`) |
| `auto_generate` | boolean | `false` | If true, use Whisper to generate when no subs found (requires openai-whisper skill) |

### `[aspect]`

Aspect ratio control.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `default` | string | `"auto"` | Default ratio: `"auto"`, `"source"`, `"16:9"`, `"9:16"`, `"1:1"`, `"4:3"` |
| `pad_color` | string | `"black"` | Padding color for letterboxing: `"black"`, `"white"`, `"blur"` |

### `[clips]`

Auto-highlight settings (legacy; use `[highlights]` for Mode B features).

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `default_duration` | integer | `30` | Default clip length (seconds) when `--duration` not specified |
| `max_highlights` | integer | `5` | Number of highlight clips to generate (use `highlights.num_clips` for Mode B) |
| `highlight_length` | integer | `30` | Duration of each highlight clip (seconds) (use `highlights.clip_length` for Mode B) |

### `[highlights]`

**Mode B** intelligent highlight detection settings.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `strategy` | array of strings | `["scene", "audio"]` | Detection strategy order. Options: `"scene"`, `"audio"`, `"scene+audio"`, `"even"`. First strategy that yields enough clips wins. |
| `num_clips` | integer | `5` | Number of highlight clips to generate |
| `clip_length` | integer | `30` | Duration of each highlight clip (seconds) |
| `scene_threshold` | float (0.0-1.0) | `0.4` | Sensitivity for scene change detection (lower = more sensitive) |
| `audio_min_peak_db` | float | `-20.0` | Minimum audio peak level in dB (negative values; e.g., -20 = quiet, -10 = loud) |

**Strategy examples:**
- `["scene+audio"]` — Only use points where both scene and audio coincide (very selective)
- `["scene", "audio"]` — Use scene changes first, fill gaps with audio peaks (default)
- `["audio"]` — Audio peaks only (good for podcasts, concerts)
- `["even"]` — Fallback to old even-spacing behavior

### `[manifest]`

Downloads and operations tracking.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `enabled` | boolean | `true` | Enable manifest recording (JSONL database) |
| `path` | string | `"~/.local/share/mrclipper/manifest.jsonl"` | Path to manifest file |

**Manifest format:** Each line is a JSON object with fields:
- `operation`: `"download"`, `"clip"`, `"highlight_start"`, `"highlight_clip"`
- `timestamp`: ISO 8601 UTC
- `input_file`, `output_file`, `url` (if applicable)
- `success`: boolean
- `error` (if failed)
- `duration_seconds` (if timed)
- `metadata`: additional context (subtitle mode, aspect, start time, etc.)

**View history:** Use `mrclipper manifest recent` or parse the JSONL file with `jq`.

### `[publisher]`

Metadata generation for `mrpublisher` integration (caption + tags).

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `caption_template` | string | `null` | Template for auto-generated captions. Placeholders: `{title}`, `{start}`, `{duration}`, `{url}`. If null, uses sensible default. |
| `default_tags` | array of strings | `[]` | Static tags to add to every clip (e.g., `["mrclipper", "highlight"]`) |
| `auto_generate_tags` | boolean | `true` | If true, generate tags from video title using simple keyword extraction |

**Caption template example:**
```toml
[publisher]
caption_template = "🎬 {title}\n⏱ {start} ({duration}s)\n\nFull video: {url}"
```

**Metadata output:** Each clip gets a sidecar file:
- `clip_001.mp4` → `clip_001.mp4.metadata.json`

**Metadata JSON structure:**
```json
{
  "title": "Video Title Here",
  "caption": "Generated or custom caption text",
  "tags": ["tag1", "tag2", "tag3"],
  "source_url": "https://youtube.com/watch?v=...",
  "clip_start": "00:01:30",
  "duration_seconds": 30,
  "created_at": "2026-03-02T04:30:00Z",
  "file_path": "/path/to/clip_001.mp4"
}
```

`mrpublisher` can read these `.metadata.json` files to auto-generate posts with proper captions and hashtags.

### `[yt-dlp]`

YouTube download options.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `format` | string | `"best[ext=mp4]"` | Format selector for yt-dlp (see yt-dlp docs) |

---

## Complete Example Config

```toml
# ~/.config/mrclipper/config.toml

[output]
format = "mp4"
codec = "libx264"
crf = 20           # Higher quality
preset = "medium"  # Slower but better compression

[paths]
workdir = "/tmp/vr-clipper"
output = "~/Videos/MrClipper"

[subtitles]
mode = "soft"
languages = ["en", "id"]
auto_generate = false

[aspect]
default = "auto"
pad_color = "black"

[clips]
default_duration = 30
max_highlights = 10
highlight_length = 45

[yt-dlp]
format = "best[ext=mp4]"
```

---

## Overriding Config per Job

Create a job-specific TOML (e.g., `~/jobs/tiktok.toml`):

```toml
[aspect]
default = "9:16"

[subtitles]
mode = "soft"

[clips]
default_duration = 30
```

Use it:

```bash
/clip URL --start 00:00:30 --duration 30 --config ~/jobs/tiktok.toml
```

Settings merge: job config overrides global, everything else falls back to global.

---

## Tips

- **Quality vs Speed:** Lower `crf` = better quality but larger files. Higher `preset` = slower encode but better compression.
- **Paths:** Use absolute paths or `~` for home. Relative paths are relative to current working directory.
- **Subtitles:** `mode = "soft"` is fastest and highest quality. Use `"burn"` only when necessary.
- **Aspect:** `auto` preserves original. Force ratios only when targeting specific platforms (TikTok = 9:16, YouTube = 16:9).

See also: [Usage](usage.md), [Examples](examples.md)