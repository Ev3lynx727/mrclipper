"""Subtitle handling (soft and burn-in)."""

import logging
import subprocess
from pathlib import Path

from .exceptions import ProcessingError
from .utils import run_cmd

logger = logging.getLogger("mrclipper")


def burn_subtitles(video_in: Path, sub_file: Path, video_out: Path):
    """Burn subtitles into video (re-encode)."""
    logger.info("Burning subtitles into video...")
    sub_ext = sub_file.suffix.lstrip(".")
    sub_codec = "ass" if sub_ext in ["ass", "ssa"] else "mov_text"
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(video_in),
        "-i",
        str(sub_file),
        "-c:v",
        "copy",
        "-c:a",
        "copy",
        "-c:s",
        sub_codec,
        "-map",
        "0:v",
        "-map",
        "0:a",
        "-map",
        "1:s",
        str(video_out),
    ]
    try:
        run_cmd(cmd, "ffmpeg burn")
        logger.info("Burned subtitles to: %s", video_out)
    except subprocess.CalledProcessError as e:
        raise ProcessingError(f"Subtitle burning failed: {e.stderr}") from e
