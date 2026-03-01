"""Highlights detection with scene/audio awareness."""

import logging
from pathlib import Path
from typing import Any

from .clip import clip_video
from .metadata import write_metadata
from .scene_detector import detect_audio_peaks, detect_scene_changes, select_highlights
from .video import get_video_duration

logger = logging.getLogger("mrclipper")


def detect_highlights(video: Path, output_dir: Path, cfg: dict[str, Any] | None = None):
    """
    Smart highlight detection using scene and audio cues.

    Args:
        video: Input video path
        output_dir: Where to save highlight clips
        cfg: Configuration dict (keys: clips.max_highlights, clips.highlight_length,
             highlights.strategy, highlights.scene_threshold, highlights.audio_min_peak_db,
             publisher.caption_template, publisher.default_tags, publisher.auto_generate_tags)

    Falls back to even spacing if detectors fail or find nothing.
    """
    from .manifest import manifest

    output_dir.mkdir(parents=True, exist_ok=True)

    # Extract config with defaults
    if cfg is None:
        cfg = {}
    clips_cfg = cfg.get("clips", {})
    highlights_cfg = cfg.get("highlights", {})
    publisher_cfg = cfg.get("publisher", {})

    num_clips = clips_cfg.get("max_highlights", 5)
    clip_len = clips_cfg.get("highlight_length", 30)

    # Get total duration
    logger.info("Analyzing video for highlights...")
    total_dur = get_video_duration(video)
    logger.debug("Total duration: %.2fs", total_dur)

    # Record ingestion to manifest
    manifest.record(
        operation="highlight_start",
        input_file=video,
        output_file=output_dir,
        success=True,
        metadata={
            "strategy": highlights_cfg.get("strategy", ["scene", "audio"]),
            "num_clips": num_clips,
            "clip_length": clip_len,
        },
    )

    # Run detectors (always run both; strategy decides which points to use)
    logger.info("Detecting scene changes...")
    scenes = detect_scene_changes(video, threshold=highlights_cfg.get("scene_threshold", 0.4))
    logger.info("Detected %d scene changes", len(scenes))
    logger.debug("Scenes: %s", scenes)

    logger.info("Detecting audio peaks...")
    peaks = detect_audio_peaks(
        video, min_peak_ratio=_db_to_ratio(highlights_cfg.get("audio_min_peak_db", -20.0))
    )
    logger.info("Detected %d audio peaks", len(peaks))
    logger.debug("Peaks: %s", peaks)

    # Select highlight segments using strategy
    logger.info(
        "Selecting highlights (strategy: %s)...", highlights_cfg.get("strategy", ["scene", "audio"])
    )
    highlights = select_highlights(
        scenes,
        peaks,
        num_clips=num_clips,
        clip_length=clip_len,
        total_duration=total_dur,
        strategy=highlights_cfg.get("strategy", ["scene", "audio"]),
    )

    logger.info("Selected %d highlight segments", len(highlights))

    # Create clips
    created_clips = []
    for i, (start, end) in enumerate(highlights):
        duration = int(end - start)
        clip_name = output_dir / f"highlight_{i:04d}.mp4"
        try:
            # Call clip_video with cfg to enable metadata writing
            clip_video(
                video=video,
                start=str(start),
                duration=duration,
                output=clip_name,
                sub_file=None,
                cfg=cfg,
                source_url=None,
                caption=None,
                tags=None,
            )
            # Write additional metadata specific to highlight (overwrite to add index)
            try:
                write_metadata(
                    output=clip_name,
                    video=video,
                    start=str(start),
                    duration=duration,
                    source_url=None,
                    caption=publisher_cfg.get("caption_template"),  # Could be None
                    tags=publisher_cfg.get("default_tags"),
                    default_tags=publisher_cfg.get("default_tags", []),
                    auto_generate_tags=publisher_cfg.get("auto_generate_tags", True),
                    extra={
                        "highlight_index": i,
                        "strategy_used": highlights_cfg.get("strategy"),
                        "is_highlight": True,
                    },
                )
            except Exception as e:
                logger.warning("Failed to write metadata for highlight %d: %s", i, e)
            created_clips.append((clip_name, start, end))
            # Record individual clip to manifest
            manifest.record(
                operation="highlight_clip",
                input_file=video,
                output_file=clip_name,
                success=True,
                duration_seconds=duration,
                metadata={
                    "clip_index": i,
                    "start_time": start,
                    "end_time": end,
                    "has_metadata": True,
                },
            )
        except Exception as e:
            logger.warning("Failed to create clip %d: %s", i, e)
            manifest.record(
                operation="highlight_clip",
                input_file=video,
                output_file=clip_name,
                success=False,
                error=str(e),
                duration_seconds=duration,
                metadata={"clip_index": i},
            )

    logger.info("Created %d highlight clips in: %s", len(created_clips), output_dir)
    return output_dir


def _db_to_ratio(db_value: float) -> float:
    """Convert dB (negative) to linear ratio (0-1)."""
    if db_value >= 0:
        return 1.0
    return 10 ** (db_value / 20)
