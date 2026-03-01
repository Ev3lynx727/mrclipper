# User Guide

How to use Mr. Clipper for video clipping tasks.

## Table of Contents

- [Basic Clipping](#basic-clipping)
- [Auto-Highlights](#auto-highlights)
- [Search & Download](#search-download)
- [Manifest & Logs](#manifest--logs)
- [Metadata for mrpublisher](#metadata-for-mrpublisher)
- [Subtitles](#subtitles)
- [Aspect Ratios](#aspect-ratios)
- [Configuration Files](#configuration-files)

---

## Basic Clipping

Clip a specific segment from a video:

```bash
/clip <URL> --start HH:MM:SS --duration SECONDS
```

**Example:**

```bash
/clip https://youtube.com/watch?v=abc123 --start 00:01:30 --duration 60
```

This downloads the video, extracts a 60-second clip starting at 1:30, and saves to the output directory (from config).

### Options

| Flag | Description |
|------|-------------|
| `--start HH:MM:SS` | Start time (required) |
| `--duration N` | Clip length in seconds (default: 30) |
| `--output PATH` | Custom output file path |
| `--aspect RATIO` | Target aspect ratio (see below) |
| `--burn-subs` | Burn subtitles into video |
| `--config PATH` | Use a specific TOML config file |
| `--caption TEXT` | Custom caption for metadata (overrides config) |
| `--tags TEXT` | Comma-separated tags for metadata (overrides config) |

---

## Auto-Highlights

Automatically detect and extract multiple highlight clips using scene + audio detection (Mode B):

```bash
/auto-highlight <URL> [--output DIR] [--config PATH]
```

**Example:**

```bash
/auto-highlight https://youtube.com/watch?v=xyz --output ~/Highlights/
```

By default creates 5 clips, 30 seconds each. Configure in `[highlights]` section.

### Options

| Flag | Description |
|------|-------------|
| `--output DIR` | Output directory for clips |
| `--config PATH` | Job-specific config |
| `--caption TEMPLATE` | Override caption template |
| `--tags tag1,tag2` | Override tags (comma-separated) |

---

## Search & Download

Find videos by keyword and download top results:

```bash
mrclipper search "QUERY" [--limit N] [--output DIR]
```

**Example:**

```bash
mrclipper search "AI trends 2024" --limit 10 --output ~/Downloads/AI/
mrclipper search "cooking tutorial" --limit 5
```

This uses yt-dlp's `ytsearch:` to fetch YouTube results. Respects your config for subtitles and aspect.

**Note:** Search results are downloaded in bulk; no clipping performed.

---

## Manifest & Logs

### View Recent Operations

```bash
mrclipper manifest-recent              # Last 20 operations
mrclipper manifest-recent --limit 50   # More entries
mrclipper manifest-recent --operation download  # Only downloads
mrclipper manifest-recent --operation clip      # Only clips
```

### View Statistics

```bash
mrclipper manifest-stats --days 7    # Last week (default)
mrclipper manifest-stats --days 30   # Last month
```

Shows:
- Total operations
- Success / failure counts
- Success rate percentage
- Average processing duration

### Log File

All operations are logged to:
- **Console:** Real-time
- **File:** `~/.local/share/mrclipper/mrclipper.log` (rotating, 5 MB)

Check logs for debugging:

```bash
tail -f ~/.local/share/mrclipper/mrclipper.log
```

Configure log location in `[paths] log_file`.

---

## Metadata for mrpublisher

Every clip (manual or highlight) gets a `.metadata.json` sidecar file:

```
clip_001.mp4
clip_001.mp4.metadata.json  ← mrpublisher reads this
```

### Metadata Structure

```json
{
  "title": "Video Title",
  "caption": "Generated or custom caption",
  "tags": ["tag1", "tag2"],
  "source_url": "https://youtube.com/watch?v=...",
  "clip_start": "00:01:30",
  "duration_seconds": 30,
  "created_at": "2026-03-02T04:30:00Z",
  "file_path": "/path/to/clip_001.mp4",
  "highlight_index": 0,        // Only for auto-highlights
  "is_highlight": true         // Only for auto-highlights
}
```

### Customizing Caption & Tags

**Via config** (`~/.config/mrclipper/config.toml`):

```toml
[publisher]
caption_template = "🎬 {title}\n⏱ {start} ({duration}s)\n\nFull video: {url}"
default_tags = ["highlight", "viral"]
auto_generate_tags = true   # Also extract tags from title
```

**Via CLI** (overrides config):

```bash
mrclipper clip URL --start 00:01:00 --duration 30 \
  --caption "Check out this highlight!" \
  --tags "funny,memes,viral"
```

**Caption placeholders:**
- `{title}` — Video title
- `{start}` — Clip start time (HH:MM:SS)
- `{duration}` — Duration in seconds
- `{url}` — Original video URL (if known)

**mrpublisher workflow:**
1. Scan directory for `*.mp4.metadata.json`
2. Read `caption` and `tags`
3. Create post with proper text and hashtags
4. Attach the video file

---

## Subtitles

### Soft Subtitles (Default)

Subtitles are downloaded as separate `.srt` files. No re-encoding, quality preserved.

```bash
/clip URL --start 00:01:00 --duration 45
# Outputs: video.mp4 + video.srt
```

Upload both to YouTube/TikTok → subtitles appear automatically.

### Burned Subtitles

Embed subtitles directly into the video frame (re-encode):

```bash
/clip URL --start 00:01:00 --duration 45 --burn-subs
```

Use this when the platform doesn't support soft subtitle uploads.

### Supported Subtitle Formats

- `.srt` (SubRip)
- `.vtt` (WebVTT)
- `.ass` / `.ssa` (Advanced SubStation Alpha)

---

## Aspect Ratios

### Auto-Detect (Default)

Preserves the source video's native aspect ratio:

```bash
/clip URL --start 00:01:00 --duration 30  # uses config default (auto)
```

### Force Specific Ratio

```bash
# TikTok/Reels (vertical 9:16)
/clip URL --start 00:00:30 --duration 30 --aspect 9:16

# YouTube (horizontal 16:9)
/clip URL --start 00:02:00 --duration 60 --aspect 16:9

# Instagram feed (square 1:1)
/clip URL --start 00:00:45 --duration 30 --aspect 1:1
```

### Valid Ratios

- `auto` or `source` — keep original
- `16:9` — widescreen
- `9:16` — vertical
- `1:1` — square
- `4:3` — traditional

### Padding

If the source video doesn't match the target ratio, Mr. Clipper adds letterbox/pillarbox bars. Color is configurable (`aspect.pad_color` in TOML).

---

## Configuration Files

### Global Config

Location: `~/.config/mrclipper/config.toml`

Applied to all clips unless overridden by `--config`.

### Job-Specific Config

Create a TOML file for a specific workflow:

```toml
# ~/jobs/tiktok.toml
[aspect]
default = "9:16"

[subtitles]
mode = "soft"

[highlights]
strategy = ["scene+audio"]
num_clips = 8

[publisher]
caption_template = "🔥 {title}\n⏱ {start}\n\n#TikTok #Viral"
default_tags = ["tiktok", "viral"]
```

Use it:

```bash
/clip URL --start 00:00:30 --duration 30 --config ~/jobs/tiktok.toml
/auto-highlight URL --config ~/jobs/tiktok.toml
```

This overrides global settings for this run only.

---

## Examples

### 1. TikTok Clip (9:16, soft subs)

```bash
/clip URL --start 00:00:15 --duration 60 --aspect 9:16
```

### 2. YouTube Long Clip (16:9, 2 minutes)

```bash
/clip URL --start 00:05:00 --duration 120 --aspect 16:9 --output ~/Videos/YouTube/long_clip.mp4
```

### 3. Instagram with Burned Subs

```bash
/clip URL --start 00:01:00 --duration 45 --aspect 1:1 --burn-subs
```

### 4. Auto-Highlights for Marathon Stream

```bash
/auto-highlight URL --output ~/Highlights/Marathon/ --config ~/jobs/youtube.toml
```

### 5. Search & Download AI Trends

```bash
mrclipper search "AI trends 2024" --limit 10 --output ~/Downloads/AI/
```

### 6. Check Recent Downloads

```bash
mrclipper manifest-recent --operation download --limit 10
```

---

Need more? Check [Configuration](configuration.md) or [Examples](examples.md).
