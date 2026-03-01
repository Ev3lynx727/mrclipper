"""Clip metadata generation for mrpublisher integration."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger("mrclipper")


def generate_caption(
    video_title: str,
    start: str,
    duration: int,
    source_url: str | None = None,
    template: str | None = None,
    custom_caption: str | None = None,
) -> str:
    """Generate caption for a clip.

    Args:
        video_title: Original video title
        start: Start time (HH:MM:SS)
        duration: Clip duration in seconds
        source_url: Original video URL (optional)
        template: Optional template with {title}, {start}, {duration}, {url} placeholders
        custom_caption: Override entirely

    Returns:
        Caption string
    """
    if custom_caption:
        return custom_caption

    if template:
        return template.format(
            title=video_title,
            start=start,
            duration=duration,
            url=source_url or "",
        )

    # Default template
    lines = [f"🎬 {video_title}", f"⏱ {start} ({duration}s)"]
    if source_url:
        lines.append(f"\nFull video: {source_url}")
    return "\n".join(lines)


def generate_tags(
    video_title: str,
    custom_tags: list[str] | None = None,
    default_tags: list[str] | None = None,
    auto_generate: bool = True,
    max_tags: int = 10,
) -> list[str]:
    """Generate hashtags from video title or use defaults.

    Args:
        video_title: Original title
        custom_tags: User-provided tags (overrides everything)
        default_tags: Static tags from config (prepended if auto_generate)
        auto_generate: If true, extract tags from title
        max_tags: Max number of auto-generated tags

    Returns:
        List of tag strings
    """
    if custom_tags:
        return list(custom_tags)

    tags = list(default_tags or [])

    if auto_generate:
        stopwords = {"the", "and", "for", "with", "in", "on", "at", "to", "of", "a", "an"}
        words = video_title.lower().split()
        for word in words:
            clean = "".join(c for c in word if c.isalnum())
            if clean and clean not in stopwords and len(clean) > 2:
                if clean not in tags:  # avoid duplicates
                    tags.append(clean)
                if len(tags) >= max_tags:
                    break

    return tags


def write_metadata(
    output: Path,
    video: Path,
    start: str,
    duration: int,
    source_url: str | None = None,
    caption: str | None = None,
    tags: list[str] | None = None,
    caption_template: str | None = None,
    default_tags: list[str] | None = None,
    auto_generate_tags: bool = True,
    extra: dict[str, Any] | None = None,
) -> Path:
    """Write metadata sidecar file for a clip.

    Args:
        output: Clip video file path (e.g., clip_001.mp4)
        video: Original video file path
        start: Start time (HH:MM:SS)
        duration: Clip duration in seconds
        source_url: Original video URL (if known)
        caption: Custom caption (overrides auto-gen)
        tags: Custom tags list (overrides auto-gen)
        caption_template: Template for auto-generated caption
        default_tags: Default tags from config to include
        auto_generate_tags: Whether to auto-generate tags from title
        extra: Additional fields to include

    Returns:
        Path to metadata file (e.g., clip_001.mp4.metadata.json)
    """
    metadata_path = output.with_suffix(output.suffix + ".metadata.json")
    video_title = video.stem  # Use filename as title fallback

    generated_caption = generate_caption(
        video_title=video_title,
        start=start,
        duration=duration,
        source_url=source_url,
        template=caption_template,
        custom_caption=caption,
    )

    generated_tags = generate_tags(
        video_title=video_title,
        custom_tags=tags,
        default_tags=default_tags,
        auto_generate=auto_generate_tags,
    )

    metadata = {
        "title": video_title,
        "caption": generated_caption,
        "tags": generated_tags,
        "source_url": source_url,
        "clip_start": start,
        "duration_seconds": duration,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "file_path": str(output),
    }

    if extra:
        metadata.update(extra)

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    logger.info("Wrote metadata: %s", metadata_path)
    return metadata_path
