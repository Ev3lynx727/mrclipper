# Installation Guide

This guide walks you through installing and setting up Mr. Clipper.

## Prerequisites

Make sure these are installed:

```bash
# Check dependencies
ffmpeg -version
ffprobe -version
yt-dlp --version
python3 --version
```

All are already installed on this system ✅

## Step 1: Skill Installation

The skill is already copied to OpenClaw's global skills directory:

```
~/.nvm/versions/node/v24.12.0/lib/node_modules/openclaw/skills/video-clipper/
```

If you need to reinstall:

```bash
cp -r /home/ev3lynx/.openclaw/workspace/skills/video-clipper \
  ~/.nvm/versions/node/v24.12.0/lib/node_modules/openclaw/skills/
```

## Step 2: Global Configuration

Create the global config directory and file:

```bash
# Create config directory
mkdir -p ~/.config/mrclipper

# Copy example config
cp /home/ev3lynx/.openclaw/workspace/skills/video-clipper/config/config.toml.example \
   ~/.config/mrclipper/config.toml

# Edit to your preferences
nano ~/.config/mrclipper/config.toml
```

### Minimal Config

You can start with a minimal `~/.config/mrclipper/config.toml`:

```toml
[paths]
output = "~/Videos/MrClipper"

[aspect]
default = "auto"

[subtitles]
mode = "soft"
```

## Step 3: Permissions

Ensure the Python script is executable:

```bash
chmod +x ~/.nvm/versions/node/v24.12.0/lib/node_modules/openclaw/skills/video-clipper/scripts/clip.py
```

## Step 4: Verify Installation

Test the help:

```bash
python3 ~/.nvm/versions/node/v24.12.0/lib/node_modules/openclaw/skills/video-clipper/scripts/clip.py --help
```

You should see the usage message.

## Step 5: Agent Registration (Optional)

If you want to spawn Mr. Clipper as a dedicated sub-agent:

```bash
openclaw agents add mrclipper --non-interactive --workspace /home/ev3lynx/.openclaw/workspace-mrclipper --model openrouter/stepfun/step-3.5-flash:free
```

The agent is already added ✅

## All Done!

You're ready to start clipping. See [Usage](usage.md) for next steps.