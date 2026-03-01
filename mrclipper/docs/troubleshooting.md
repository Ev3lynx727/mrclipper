# Troubleshooting

Common issues and solutions for Mr. Clipper.

---

## Installation Issues

### "No module named 'toml'"

Install Python TOML package:

```bash
pip3 install toml
# or
sudo apt-get install python3-toml  # Debian/Ubuntu
```

---

### "yt-dlp: command not found"

Install yt-dlp:

```bash
pip3 install yt-dlp
# or
sudo apt-get install yt-dlp
```

---

### "ffmpeg: command not found"

Install ffmpeg:

```bash
sudo apt-get install ffmpeg
```

---

## Runtime Errors

### "Download failed"

Possible causes:
- Invalid URL
- Video is age-restricted / members-only
- Network issue
- yt-dlp outdated

**Fix:** Update yt-dlp: `yt-dlp -U`

---

### "No subtitle file found"

Subtitles may not be available for that video. Options:
- Use `--burn-subs` won't help if no subs exist
- Enable `auto_generate = true` in config (requires openai-whisper skill)
- Try a different language in config: `languages = ["en", "ja"]`

---

### "Aspect ratio processing failed"

Usually due to invalid ratio format. Use:
- `auto`, `source`, `16:9`, `9:16`, `1:1`, `4:3`
- Not: `169`, `916`, `16-9`

---

### "Disk space full"

Cleanup temp files:

```bash
rm -rf /tmp/vr-clipper/*
```

Or change `workdir` to a larger disk in config:

```toml
[paths]
workdir = "/path/to/big/tmp"
```

---

## Agent/Spawning Issues

### "agentId is not allowed for sessions_spawn"

Mr. Clipper agent not registered. Re-add:

```bash
openclaw agents add mrclipper --non-interactive --workspace /home/ev3lynx/.openclaw/workspace-mrclipper --model openrouter/stepfun/step-3.5-flash:free
openclaw gateway restart
```

See [Agent Setup](agent-setup.md).

---

### "Timeout" or "Agent not responding"

Long downloads can exceed timeout. For large videos:
- Use cron (background, no timeout)
- Increase session timeout in agent config
- Download first, then clip separately

---

## Performance Problems

### Re-encoding is slow

Avoid re-encoding by:
- Not using `--burn-subs` (soft subs are faster)
- Using `--aspect auto` or `source` (no scaling)
- Stream copy is default when possible

If you must re-encode, reduce `crf` quality or use faster `preset`:

```toml
[output]
preset = "fast"  # or "veryfast"
```

---

## Permission Errors

### "Permission denied" on output directory

Ensure the agent user can write to output path:

```bash
chmod 755 ~/Videos
# or change output to a writable location
```

---

## Debug Mode

Add verbosity to commands:

```bash
# See full yt-dlp output
# (Mr. Clipper already logs progress to stderr)
/clip URL --start 00:01:00 --duration 30 2>&1 | tee ~/clip.log
```

Or set in config:

```toml
[logging]
level = "debug"  # Not yet implemented
```

---

## Still Stuck?

1. Check logs: `openclaw logs --agent mrclipper --follow`
2. Test script directly: `python3 scripts/clip.py --help`
3. Verify dependencies: `ffmpeg -version && yt-dlp --version && python3 --version`
4. Ensure config file exists: `ls ~/.config/mrclipper/config.toml`
5. Try a short test: `/clip URL --start 00:00:05 --duration 10`

---

**Need help?** Reach out in the Mr. Zero Agents family chat.