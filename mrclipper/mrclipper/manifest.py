"""Downloads manifest — tracks all download and clipping operations."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger("mrclipper")


class DownloadManifest:
    """JSON-line manifest for tracking all video operations.

    Each entry records:
    - operation: "download" | "clip" | "highlight"
    - url: source URL (if applicable)
    - input_file: local input path
    - output_file: local output path
    - timestamp: ISO 8601 UTC
    - success: bool
    - error: error message (if failed)
    - duration_seconds: processing time
    - metadata: extra fields (title, aspect, subtitles, etc.)
    """

    def __init__(self, manifest_path: Path | None = None):
        """Initialize manifest handler.

        Args:
            manifest_path: Path to manifest file (e.g., ~/.local/share/mrclipper/manifest.jsonl)
                          If None, manifest disabled.
        """
        self.path = manifest_path  # Alias for easy access (mypy-friendly)
        if manifest_path:
            manifest_path.parent.mkdir(parents=True, exist_ok=True)

    def record(
        self,
        operation: str,
        input_file: Path | None = None,
        output_file: Path | None = None,
        url: str | None = None,
        success: bool = True,
        error: str | None = None,
        duration_seconds: float | None = None,
        **metadata: Any,
    ):
        """Write a manifest entry.

        Args:
            operation: Type of operation ("download", "clip", "highlight")
            input_file: Input video path
            output_file: Output video path
            url: Source URL (for downloads)
            success: Whether operation succeeded
            error: Error message if failed
            duration_seconds: Processing time (for timing)
            **metadata: Additional fields (title, aspect, subtitles, strategy, etc.)
        """
        if not self.path:
            return  # Manifest disabled

        entry = {
            "operation": operation,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "success": success,
        }
        if url:
            entry["url"] = url
        if input_file:
            entry["input_file"] = str(input_file)
        if output_file:
            entry["output_file"] = str(output_file)
        if error:
            entry["error"] = error
        if duration_seconds is not None:
            entry["duration_seconds"] = round(duration_seconds, 3)
        if metadata:
            entry["metadata"] = metadata

        try:
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.warning("Failed to write manifest: %s", e)

    def recent(self, limit: int = 20, operation: str | None = None) -> list[dict]:
        """Read recent entries from manifest.

        Args:
            limit: Max number of entries to return
            operation: Filter by operation type (e.g., "download")

        Returns:
            List of manifest entries (newest first)
        """
        if not self.path or not self.path.exists():
            return []

        entries = []
        try:
            with self.path.open("r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in reversed(lines):  # Newest first
                    try:
                        entry = json.loads(line.strip())
                        if operation and entry.get("operation") != operation:
                            continue
                        entries.append(entry)
                        if len(entries) >= limit:
                            break
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.error("Failed to read manifest: %s", e)
        return entries

    def search(self, query: str, limit: int = 20) -> list[dict]:
        """Search entries by URL or output filename.

        Args:
            query: Search string (case-insensitive)
            limit: Max results

        Returns:
            Matching entries (newest first)
        """
        results = []
        for entry in self.recent(limit=1000):  # Scan up to 1000 entries
            url = entry.get("url", "").lower()
            output = entry.get("output_file", "").lower()
            if query.lower() in url or query.lower() in output:
                results.append(entry)
                if len(results) >= limit:
                    break
        return results

    def stats(self, days: int = 7) -> dict:
        """Get basic statistics.

        Returns:
            Dict with total downloads, success rate, avg duration, etc.
        """
        from datetime import datetime, timedelta

        cutoff = datetime.utcnow() - timedelta(days=days)
        total = 0
        successes = 0
        durations = []

        for entry in self.recent(limit=10000):
            try:
                ts = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
                if ts < cutoff:
                    continue
                total += 1
                if entry.get("success"):
                    successes += 1
                if "duration_seconds" in entry:
                    durations.append(entry["duration_seconds"])
            except (KeyError, ValueError):
                continue

        avg_dur = sum(durations) / len(durations) if durations else 0.0

        return {
            "period_days": days,
            "total_entries": total,
            "successful": successes,
            "failed": total - successes,
            "success_rate": round(successes / total * 100, 1) if total else 0,
            "avg_duration_seconds": round(avg_dur, 3),
        }


# Global singleton instance — will be configured at runtime via cli.py
manifest = DownloadManifest()
