"""Aspect ratio processing."""

import logging
import shutil
import subprocess
from pathlib import Path

from .exceptions import ProcessingError
from .utils import run_cmd
from .video import get_video_dimensions

logger = logging.getLogger("mrclipper")


def process_aspect_ratio(
    video_in: Path, video_out: Path, target_ratio: str, pad_color: str = "black"
) -> Path:
    """Convert video to target aspect ratio with padding if needed."""
    if target_ratio in ["auto", "source"]:
        return video_in
    logger.info("Processing aspect ratio: %s (pad: %s)", target_ratio, pad_color)
    src_w, src_h = get_video_dimensions(video_in)
    tgt_w, tgt_h = map(int, target_ratio.split(":"))
    src_ratio_val = src_w * 10000 // src_h
    tgt_ratio_val = tgt_w * 10000 // tgt_h
    if src_ratio_val > tgt_ratio_val:
        # Source wider -> scale by height, pad width
        scale_h = src_h
        scale_w = src_h * tgt_w // tgt_h
        pad_x = (src_w - scale_w) // 2
        pad_y = 0
    else:
        # Source taller -> scale by width, pad height
        scale_w = src_w
        scale_h = src_w * tgt_h // tgt_w
        pad_x = 0
        pad_y = (src_h - scale_h) // 2
    # If no change, just copy
    if scale_w == src_w and scale_h == src_h and pad_x == 0 and pad_y == 0:
        logger.info("Source already matches target ratio, copying...")
        shutil.copy2(video_in, video_out)
        return video_out
    filters = f"scale={scale_w}:{scale_h}"
    if pad_x > 0 or pad_y > 0:
        filters += f",pad={scale_w}:{scale_h}:{pad_x}:{pad_y}:{pad_color}"
    # Re-encode
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(video_in),
        "-vf",
        filters,
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "23",
        "-c:a",
        "copy",
        str(video_out),
    ]
    try:
        run_cmd(cmd, "ffmpeg aspect")
        logger.info("Aspect processed: %s", video_out)
        return video_out
    except subprocess.CalledProcessError as e:
        raise ProcessingError(f"Aspect ratio conversion failed: {e.stderr}") from e
