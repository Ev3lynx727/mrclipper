# Cron Scheduling

Automate video clipping with OpenClaw's built-in cron system.

## Overview

OpenClaw cron allows you to run Mr. Clipper tasks on a schedule without manual intervention.

**Use cases:**
- Daily highlight extraction from favorite channels
- Weekly clipping of livestreams
- Periodic content processing

---

## Cron Configuration

Cron jobs are stored in:

```
~/.openclaw/cron/jobs.json
```

This file contains an array of job objects.

---

## Job Schema

```json
{
  "id": "unique-job-id",
  "agent": "mrclipper",
  "schedule": "0 9 * * *",
  "task": "auto-highlight https://youtube.com/... --config /path/to/config.toml --output /path/to/output/",
  "enabled": true
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier (for management) |
| `agent` | string | Agent ID to run task (`mrclipper`) |
| `schedule` | string | Standard cron expression (5 fields) |
| `task` | string | Command line task (same as you'd type in chat) |
| `enabled` | boolean | Enable/disable this job |

---

## Cron Expressions

Standard 5-field cron format:

```
┬    ┬    ┬    ┬    ┬
│    │    │    │    │
│    │    │    │    └ day of week (0-7) (Sunday=0 or 7)
│    │    │    └───── month (1-12)
│    │    └────────── day of month (1-31)
│    └─────────────── hour (0-23)
└──────────────────── minute (0-59)
```

**Examples:**

| Schedule | Expression | Meaning |
|----------|------------|---------|
| Every 6 hours | `0 */6 * * *` | At minute 0 past every 6th hour |
| Daily at 9 AM | `0 9 * * *` | Every day at 09:00 |
| Weekly Monday 8 AM | `0 8 * * 1` | Monday at 08:00 |
| Every 30 minutes | `*/30 * * * *` | At minute 0 and 30 |

**Tip:** Use [crontab.guru](https://crontab.guru) to validate expressions.

---

## Adding a Job

Edit `~/.openclaw/cron/jobs.json`:

```bash
nano ~/.openclaw/cron/jobs.json
```

Add a new object to the array:

```json
[
  {
    "id": "daily-youtube-highlights",
    "agent": "mrclipper",
    "schedule": "0 9 * * *",
    "task": "auto-highlight https://youtube.com/watch?v=XYZ --config /home/ev3lynx/jobs/youtube.toml --output /home/ev3lynx/Highlights/Daily/",
    "enabled": true
  }
]
```

Save and exit. Changes take effect immediately (no restart needed).

---

## Managing Jobs

### List Jobs

```bash
openclaw cron list
```

Shows all jobs with next run time.

### Enable/Disable

Edit `jobs.json` and set `"enabled": false` to pause a job.

Or use CLI (if available):

```bash
openclaw cron disable daily-youtube-highlights
openclaw cron enable daily-youtube-highlights
```

### View Logs

Cron task output goes to the agent's session logs:

```bash
openclaw logs --agent mrclipper --follow
```

### Run Job Manually (Test)

You can simulate the cron task by running the command in chat:

```
/auto-highlight URL --config /path/to/config.toml --output /path/to/output/
```

Or spawn the agent with the exact task string from `jobs.json`.

---

## Best Practices

1. **Use absolute paths** in `task` (cwd may not be what you expect)
2. **Test manually first** before putting in cron
3. **Log to file** if long-running: add `>> ~/cron.log 2>&1` to task
4. **Space out schedules** to avoid overlapping runs
5. **Monitor disk space** in `workdir` and `output` directories
6. **Set reasonable durations** (cron should finish before next run)

---

## Troubleshooting

### Job Not Running?

1. Check `enabled: true`
2. Validate cron expression with `crontab.guru`
3. View cron daemon logs: `openclaw logs --component cron`
4. Ensure `agent: mrclipper` is spelled correctly

### Task Fails in Cron (Works Manually)?

Most likely a **path issue**. Cron runs with minimal environment.

- Always use **absolute paths** for `--config`, `--output`
- Don't rely on `~` for other users (but `~` for the agent user is ok)
- Ensure permissions on output directory

Add debugging to task:

```json
"task": "echo \"Starting at $(date)\" >> /tmp/cron-debug.log && auto-highlight URL ..."
```

---

### Too Many Concurrent Runs?

If a task takes longer than the interval, you'll get overlapping runs.

Solutions:
- Increase interval (e.g., `0 */12 * * *` instead of `*/6`)
- Add lockfile logic (future feature)
- Make tasks shorter (subset of videos)

---

## Example Configurations

### Daily TikTok Highlights (8 AM)

```json
{
  "id": "tiktok-daily",
  "agent": "mrclipper",
  "schedule": "0 8 * * *",
  "task": "auto-highlight https://youtube.com/... --config /home/ev3lynx/jobs/tiktok.toml --output /home/ev3lynx/TikTok/Daily/",
  "enabled": true
}
```

### Every 6 Hours (YouTube, 10 Clips)

```json
{
  "id": "youtube-highlights",
  "agent": "mrclipper",
  "schedule": "0 */6 * * *",
  "task": "auto-highlight https://youtube.com/... --config /home/ev3lynx/jobs/youtube.toml --output /home/ev3lynx/Highlights/",
  "enabled": true
}
```

---

See also:
- [Agent Setup](agent-setup.md)
- [Configuration](configuration.md)
- [Troubleshooting](troubleshooting.md)