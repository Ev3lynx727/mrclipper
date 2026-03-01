# Examples

Real-world use cases and command patterns for Mr. Clipper.

## Table of Contents

- [TikTok/Reels](#tiktokreels)
- [YouTube](#youtube)
- [Instagram](#instagram)
- [Auto-Highlights](#auto-highlights)
- [Search & Download](#search-download)
- [Metadata & mrpublisher](#metadata--mrpublisher)
- [Manifest & Logging](#manifest--logging)
- [Cron Jobs](#cron-jobs)

---

## TikTok/Reels

Vertical video (9:16) with soft subtitles.

**Config:** `~/jobs/tiktok.toml`

```toml
[aspect]
default = "9:16"
pad_color = "black"

[subtitles]
mode = "soft"
languages = ["en"]

[highlights]
strategy = ["scene+audio"]
num_clips = 8
clip_length = 30

[publisher]
caption_template = "🔥 {title}\n⏱ {start}\n\n#TikTok #Viral #FYP"
default_tags = ["tiktok", "viral", "fyp"]
auto_generate_tags = false
```

**Command:**

```bash
/clip URL --start 00:00:30 --duration 30 --config ~/jobs/tiktok.toml
# or with custom caption:
/clip URL --start 00:01:00 --duration 30 --aspect 9:16 --caption "Check this out!" --tags "funny,memes"
```

**Output:** `video.mp4` + `video.srt` (upload both to TikTok) + `video.mp4.metadata.json` (for mrpublisher).

---

## YouTube

Horizontal (16:9), higher quality, longer clips allowed.

**Config:** `~/jobs/youtube.toml`

```toml
[aspect]
default = "16:9"

[subtitles]
mode = "soft"
languages = ["en"]

[output]
crf = 20  # Better quality
preset = "medium"

[highlights]
strategy = ["scene", "audio"]
num_clips = 10
clip_length = 45

[publisher]
caption_template = "🎥 {title}\n🕒 {start} ({duration}s)\n\nWatch the full video: {url}"
auto_generate_tags = true
```

**Command:**

```bash
/clip URL --start 00:05:00 --duration 120 --config ~/jobs/youtube.toml
/auto-highlight URL --config ~/jobs/youtube.toml --output ~/Highlights/
```

---

## Instagram

Square (1:1) with burned subtitles for compatibility.

```bash
/clip URL --start 00:00:45 --duration 30 --aspect 1:1 --burn-subs
```

Instagram doesn't support soft subtitle uploads for all post types, so burning is safer.

**With metadata for later posting:**

```bash
/clip URL --start 00:00:30 --duration 45 --aspect 1:1 --burn-subs --tags "instagram,reels"
```

Creates `clip.mp4.metadata.json` with tags.

---

## Auto-Highlights

### From a Livestream or Long Video

```bash
# YouTube highlights (10 clips, 45s each)
/auto-highlight URL --config ~/jobs/youtube.toml --output ~/Highlights/Stream/

# Uses config: num_clips=10, clip_length=45
```

### TikTok-Style Highlights

```bash
/auto-highlight URL --config ~/jobs/tiktok.toml --output ~/TikTok/Highlights/
# 8 clips × 30s = 4 minutes total
```

### Custom Override via CLI

```bash
# Override number of clips and caption template
/auto-highlight URL --config ~/jobs/youtube.toml \
  --caption "🔥 Highlight: {title} at {start}" \
  --tags "highlight,trending"
```

---

## Search & Download

Find videos by keyword without leaving the terminal.

### Download Top 10 AI Trends

```bash
mrclipper search "AI trends 2024" --limit 10 --output ~/Downloads/AI-Trends/
```

### Search for Cooking Tutorials

```bash
mrclipper search "easy pasta recipe" --limit 5 --output ~/Downloads/Cooking/
```

### Search with Job Config

```bash
mrclipper search "machine learning tutorial" --limit 10 --config ~/jobs/youtube.toml
```

Respects subtitle mode, aspect, and output directory from config.

---

## Metadata & mrpublisher

Every clip gets a `.metadata.json` sidecar for `mrpublisher` integration.

### Example Metadata File

`clip_001.mp4.metadata.json`:

```json
{
  "title": "My Video Title",
  "caption": "🎬 My Video Title\n⏱ 00:01:30 (30s)\n\nFull video: https://youtube.com/watch?v=abc",
  "tags": ["highlight", "viral", "mrclipper"],
  "source_url": "https://youtube.com/watch?v=abc",
  "clip_start": "00:01:30",
  "duration_seconds": 30,
  "created_at": "2026-03-02T04:30:00Z",
  "file_path": "/home/user/Videos/clip_001.mp4"
}
```

### Custom Caption Template

**Global config:**

```toml
[publisher]
caption_template = "🔥 {title}\n📌 {start} ({duration}s)\n\nSource: {url}"
default_tags = ["mrclipper", "highlight"]
auto_generate_tags = true
```

**CLI override:**

```bash
mrclipper clip URL --start 00:01:00 --duration 30 \
  --caption "Daily highlight: {title} at {start}" \
  --tags "daily,highlight"
```

### mrpublisher Workflow

1. Run `mrclipper clip` or `auto-highlight` → creates video + `.metadata.json`
2. `mrpublisher` scans output directory for `*.mp4.metadata.json`
3. Reads `caption` and `tags` from each
4. Creates social media posts automatically
5. Attaches video file

---

## Manifest & Logging

### Check What You've Downloaded

```bash
# Last 10 downloads
mrclipper manifest-recent --operation download --limit 10

# All recent clips
mrclipper manifest-recent --operation clip

# Highlights specifically
mrclipper manifest-recent --operation highlight_clip
```

### Statistics

```bash
# Last 7 days (default)
mrclipper manifest-stats

# Last 30 days
mrclipper manifest-stats --days 30
```

Output:
```
📊 Mr. Clipper Manifest Statistics (last 30 days)
   Total entries: 150
   Successful: 148
   Failed: 2
   Success rate: 98.7%
   Avg duration: 45.321s
```

### Parse Manifest with jq

```bash
# All downloaded URLs
jq -r '.url' ~/.local/share/mrclipper/manifest.jsonl

# Failed operations with errors
jq -r 'select(.success == false) | "\(.timestamp): \(.error)"' ~/.local/share/mrclipper/manifest.jsonl

# Unique output files
jq -r '.output_file' ~/.local/share/mrclipper/manifest.jsonl | sort -u
```

### View Logs

```bash
# Follow log in real-time
tail -f ~/.local/share/mrclipper/mrclipper.log

# Last 50 lines
tail -n 50 ~/.local/share/mrclipper/mrclipper.log

# Errors only
grep -i error ~/.local/share/mrclipper/mrclipper.log
```

---

## Cron Jobs

Schedule automatic highlight extraction.

### Daily YouTube Highlights

```json
{
  "id": "daily-youtube-highlights",
  "agent": "mrclipper",
  "schedule": "0 9 * * *",
  "task": "auto-highlight https://youtube.com/channel/UCXXXX --config /home/ev3lynx/jobs/youtube.toml --output /home/ev3lynx/Highlights/Daily/",
  "enabled": true
}
```

Runs every day at 9:00 AM.

### Weekly TikTok Batch

```json
{
  "id": "weekly-tiktok-search",
  "agent": "mrclipper",
  "schedule": "0 10 * * 1",
  "task": "search \"AI trends\" --limit 5 --config /home/ev3lynx/jobs/tiktok.toml --output /home/ev3lynx/TikTok/Weekly/",
  "enabled": true
}
```

Runs every Monday at 10:00 AM, searches and downloads top 5 AI trends.

---

## Common Patterns

### 1. Quick Clip (Uses Defaults)

```bash
/clip URL --start 00:01:00 --duration 30
```

Applies all settings from global `~/.config/mrclipper/config.toml`.

---

### 2. Custom Output Location

```bash
/clip URL --start 00:00:30 --duration 60 --output ~/Videos/Special/clip.mp4
```

Overrides output path.

---

### 3. Preserve Original Aspect (No Scaling)

```bash
/clip URL --start 00:02:00 --duration 45 --aspect source
```

No letterboxing/pillarboxing.

---

### 4. Batch Processing (Multiple URLs)

Currently requires separate commands. Future: `--batch urls.txt`.

```bash
/clip URL1 --start 00:01:00 --duration 30
/clip URL2 --start 00:00:45 --duration 45 --aspect 16:9
```

---

### 5. Spawn as Sub-Agent

```bash
/sessions_spawn mrclipper "Clip this: URL --start 00:05:00 --duration 60 --config ~/jobs/youtube.toml"
```

Runs in background; returns result when done.

---

### 6. Full End-to-End: Search → Highlights → Publish

```bash
# 1. Search and download top 5 videos
mrclipper search "AI news" --limit 5 --output ~/Downloads/AI-News/ --config ~/jobs/youtube.toml

# 2. Generate highlights from each downloaded video
for video in ~/Downloads/AI-News/*.mp4; do
  mrclipper auto-highlight "$video" --output ~/Highlights/AI-News/ --config ~/jobs/youtube.toml
done

# 3. Check manifest to verify all clips
mrclipper manifest-recent --operation highlight_clip --limit 20

# 4. mrpublisher reads ~/Highlights/AI-News/*.metadata.json and creates posts
```

---

## Tips & Tricks

- **Test with short durations first** (e.g., `--duration 10`) to verify config
- **Use `--config`** for different platforms instead of changing global each time
- **Soft subtitles** are preferred: no quality loss, smaller files
- **`--burn-subs`** should be last resort (re-encode is slower, quality loss)
- **Cron jobs** should log output: append `>> ~/cron.log 2>&1` in task string
- **Metadata sidecars** are created automatically — check `.metadata.json` files for mrpublisher
- **Search command** downloads full videos; use with `--limit` to avoid filling disk

---

See [Configuration](configuration.md) for full option reference.
