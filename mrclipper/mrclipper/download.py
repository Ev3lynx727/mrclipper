"""Download videos and find subtitles."""

import logging
import subprocess
import time
from pathlib import Path

from .exceptions import DownloadError
from .manifest import manifest
from .utils import retry, run_cmd

logger = logging.getLogger("mrclipper")


@retry(tries=3, delay=2.0, backoff=2.0)
def download_video(url: str, workdir: Path, cfg: dict) -> Path:
    """Download video using yt-dlp, return path to file.

    Records operation to manifest if enabled.

    Args:
        url: Video URL
        workdir: Temporary working directory
        cfg: Configuration dict

    Returns:
        Path to downloaded video file

    Raises:
        DownloadError: If download fails after retries
    """
    start_time = time.time()
    manifest_enabled = cfg.get("manifest", {}).get("enabled", True)
    manifest_path = cfg.get("manifest", {}).get("path")
    if manifest_enabled and manifest_path:
        manifest.path = Path(manifest_path)  # Ensure manifest initialized

    try:
        workdir.mkdir(parents=True, exist_ok=True)
        out_template = str(workdir / "%(title)s.%(ext)s")
        yt_opts = cfg.get("yt-dlp", {}).get("format", "best[ext=mp4]")
        subs_mode = cfg.get("subtitles", {}).get("mode", "soft")
        langs = cfg.get("subtitles", {}).get("languages", ["en"])
        cmd = [
            "yt-dlp",
            yt_opts,
            "--output",
            out_template,
            "--no-playlist",
            "--restrict-filenames",
        ]
        if subs_mode != "none":
            logger.info("Enabling subtitle download (mode: %s)", subs_mode)
            cmd.extend(["--write-subs", "--sub-lang", ",".join(langs)])
        cmd.append(url)
        run_cmd(cmd, "yt-dlp")
        # Find the newest mp4 file
        videos = sorted(workdir.glob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not videos:
            videos = sorted(workdir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
            if videos:
                output_file = videos[0]
            else:
                raise DownloadError("Downloaded file not found")
        else:
            output_file = videos[0]

        duration = time.time() - start_time

        # Record success to manifest
        if manifest_enabled:
            manifest.record(
                operation="download",
                url=url,
                output_file=output_file,
                input_file=None,
                success=True,
                duration_seconds=duration,
                metadata={"subtitle_mode": subs_mode, "workdir": str(workdir)},
            )
        logger.info("Download completed: %s (%.2fs)", output_file, duration)
        return output_file

    except subprocess.CalledProcessError as e:
        duration = time.time() - start_time
        error_msg = f"yt-dlp failed: {e.stderr}"
        if manifest_enabled:
            manifest.record(
                operation="download",
                url=url,
                output_file=None,
                input_file=None,
                success=False,
                error=error_msg,
                duration_seconds=duration,
            )
        raise DownloadError(error_msg) from e
    except Exception as e:
        duration = time.time() - start_time
        error_msg = f"Download failed: {e}"
        if manifest_enabled:
            manifest.record(
                operation="download",
                url=url,
                output_file=None,
                input_file=None,
                success=False,
                error=error_msg,
                duration_seconds=duration,
            )
        raise DownloadError(error_msg) from e


def find_subtitle_file(video: Path) -> Path | None:
    """Find subtitle file (srt/vtt/ass) next to video."""
    base = video.with_suffix("")
    for ext in ["srt", "vtt", "ass", "ssa"]:
        sub = base.with_suffix(f".{ext}")
        if sub.exists():
            return sub
    return None
