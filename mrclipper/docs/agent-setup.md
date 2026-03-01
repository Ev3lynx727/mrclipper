# Agent Setup

How to use Mr. Clipper as a dedicated sub-agent within OpenClaw.

## Overview

Mr. Clipper can be:
1. **Invoked directly** from main session: `/clip URL ...`
2. **Spawned as a sub-agent**: `sessions_spawn mrclipper "task..."`

Sub-agent mode is useful for:
- Background processing (don't block main session)
- Scheduled cron jobs (agent runs independently)
- Dedicated resource allocation
- Isolation (different workspace, auth)

---

## Prerequisites

- Mr. Clipper skill installed ✅
- Global config created ✅
- Agent registered in `openclaw.json` ✅

---

## Using as Sub-Agent

### Direct Spawn

```bash
/sessions_spawn mrclipper "Clip this video: https://youtube.com/watch?v=abc --start 00:01:00 --duration 60 --aspect 9:16"
```

The task runs in a separate session. Results are sent back to your main chat when complete.

**Response:**

```
[sessionSpawning] Spawning: mrclipper
Task queued...
```

You'll get a message when the clip is ready.

---

### Via Cron

Cron jobs automatically spawn the `mrclipper` agent.

**Example `~/.openclaw/cron/jobs.json`:**

```json
[
  {
    "id": "morning-tiktok",
    "agent": "mrclipper",
    "schedule": "0 8 * * *",
    "task": "auto-highlight https://youtube.com/watch?v=xyz --config /home/ev3lynx/jobs/tiktok.toml --output /home/ev3lynx/Highlights/Morning/",
    "enabled": true
  }
]
```

See [Cron Scheduling](cron.md) for details.

---

## Agent Workspace

Mr. Clipper's agent-specific workspace is at:

```
/home/ev3lynx/.openclaw/workspace-mrclipper/
```

This is separate from the main workspace. The agent stores its own:
- Session history
- Temp files (unless configured otherwise)
- Logs

You can customize its config independently if needed.

---

## Checking Agent Status

```bash
openclaw agents list
```

Shows all registered agents including `mrclipper`.

```bash
openclaw status
```

Shows agent heartbeat status and sessions.

---

## Troubleshooting

### "agentId is not allowed for sessions_spawn"

The agent may not be properly registered. Check:

```bash
openclaw agents list
```

If `mrclipper` is missing, add it:

```bash
openclaw agents add mrclipper --non-interactive --workspace /home/ev3lynx/.openclaw/workspace-mrclipper --model openrouter/stepfun/step-3.5-flash:free
```

Then restart gateway:

```bash
openclaw gateway restart
```

---

### Agent Session Fails

Check the agent's session logs:

```bash
ls -la /home/ev3lynx/.openclaw/agents/mrclipper/sessions/
```

Or view via `openclaw logs --agent mrclipper --follow`.

---

### Configuration Not Found

Sub-agent uses its own workspace config unless you pass `--config` with an absolute path.

Make sure global config exists at:

```
/home/ev3lynx/.config/mrclipper/config.toml
```

or provide `--config /full/path/to/config.toml` in the task string.

---

## Best Practices

- **Absolute paths** in cron tasks and `--config` (sub-agent may have different CWD)
- **Keep clips short** (30-60s) for quick processing
- **Use soft subtitles** (default) unless you specifically need burned-in
- **Set appropriate `crf`** in config for quality vs file size trade-off
- **Monitor temp disk space** in `workdir` (default `/tmp/vr-clipper`)

---

## Advanced: Custom Agent Model

You can override the model for Mr. Clipper (though it mostly runs shell commands):

```bash
openclaw agents set-identity mrclipper --model openrouter/stepfun/step-3.5-flash:free
```

---

See also:
- [Usage](usage.md)
- [Cron Scheduling](cron.md)
- [Troubleshooting](troubleshooting.md)