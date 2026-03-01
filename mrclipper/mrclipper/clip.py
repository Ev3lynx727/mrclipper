"""Core video clipping logic."""

import logging
import subprocess
import time
from pathlib import Path

from .exceptions import ProcessingError
from .manifest import manifest
from .metadata import write_metadata
from .utils import run_cmd

logger = logging.getLogger("mrclipper")


def clip_video(
    video: Path,
    start: str,
    duration: int,
    output: Path,
    sub_file: Path | None = None,
    cfg: dict | None = None,
    source_url: str | None = None,
    caption: str | None = None,
    tags: list[str] | None = None,
):
    """Extract clip from video using ffmpeg stream copy.

    Records operation to manifest if enabled. Also writes metadata sidecar
    (output.metadata.json) for mrpublisher integration.

    Args:
        video: Input video path
        start: Start time (HH:MM:SS)
        duration: Duration in seconds
        output: Output file path
        sub_file: Optional subtitle file to mux in
        cfg: Configuration dict (for caption template, tags)
        source_url: Original video URL (for caption)
        caption: Custom caption (overrides auto-gen)
        tags: Custom tags list (overrides auto-gen)

    Returns:
        Output Path on success

    Raises:
        ProcessingError: If ffmpeg fails
    """
    output.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Clipping: start=%s, duration=%ds", start, duration)
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-ss",
        start,
        "-i",
        str(video),
        "-t",
        str(duration),
        "-map",
        "0:v",
        "-map",
        "0:a?",
    ]
    if sub_file:
        sub_ext = sub_file.suffix.lstrip(".")
        sub_codec = "ass" if sub_ext in ["ass", "ssa"] else "mov_text"
        cmd += ["-c:s", sub_codec, "-map", "1:s"]
    cmd += ["-c:v", "copy", "-c:a", "copy", str(output)]

    start_time = time.time()
    try:
        run_cmd(cmd, "ffmpeg clip")
        elapsed = time.time() - start_time
        logger.info("Clip saved: %s (%.2fs)", output, elapsed)

        # Write metadata sidecar
        try:
            publisher_cfg = cfg.get("publisher", {}) if cfg else {}
            caption_template = publisher_cfg.get("caption_template")
            default_tags = publisher_cfg.get("default_tags", [])
            auto_generate = publisher_cfg.get("auto_generate_tags", True)
            write_metadata(
                output=output,
                video=video,
                start=start,
                duration=duration,
                source_url=source_url,
                caption=caption,
                tags=tags,
                caption_template=caption_template,
                default_tags=default_tags,
                auto_generate_tags=auto_generate,
            )
        except Exception as e:
            logger.warning("Failed to write metadata: %s", e)

        # Record to manifest
        manifest.record(
            operation="clip",
            input_file=video,
            output_file=output,
            success=True,
            duration_seconds=elapsed,
            metadata={
                "start": start,
                "clip_duration": duration,
                "has_subtitles": sub_file is not None,
                "has_metadata": True,
            },
        )
        return output

    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start_time
        logger.error("Clipping failed: %s", e.stderr)
        manifest.record(
            operation="clip",
            input_file=video,
            output_file=output,
            success=False,
            error=str(e.stderr),
            duration_seconds=elapsed,
            metadata={"start": start, "clip_duration": duration},
        )
        raise ProcessingError(f"Clipping failed: {e.stderr}") from e
