"""Scene and audio analysis for smart highlights."""

import logging
import re
import subprocess
from pathlib import Path

logger = logging.getLogger("mrclipper")


def detect_scene_changes(video: Path, threshold: float = 0.4) -> list[float]:
    """
    Detect scene changes using ffmpeg's scene filter.

    Args:
        video: Path to video file
        threshold: Scene detection threshold (0.0-1.0, lower = more sensitive)

    Returns:
        List of timestamps (in seconds) where scenes change
    """
    logger.debug("Detecting scene changes (threshold=%.2f)", threshold)
    # Use ffmpeg with scene filter to get timestamps of scene changes
    # The filter outputs frame number and scene score; we parse pts_time
    cmd = [
        "ffmpeg",
        "-i",
        str(video),
        "-vf",
        f"select='gt(scene,{threshold})',metadata=print",
        "-f",
        "null",
        "-",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    timestamps = []
    # Parse lines like: frame:123   pts:12345   pts_time:12.345
    for line in result.stderr.split("\n"):
        if "pts_time:" in line:
            match = re.search(r"pts_time:([\d.]+)", line)
            if match:
                timestamps.append(float(match.group(1)))

    # Remove duplicates that are too close (< 0.5s apart)
    if timestamps:
        filtered = [timestamps[0]]
        for ts in timestamps[1:]:
            if ts - filtered[-1] >= 0.5:
                filtered.append(ts)
        logger.debug("Found %d scene changes", len(filtered))
        return filtered
    logger.debug("No scene changes detected")
    return []


def detect_audio_peaks(video: Path, min_peak_ratio: float = 0.3) -> list[float]:
    """
    Detect audio volume peaks using ffmpeg's astats filter.

    Args:
        video: Path to video file
        min_peak_ratio: Minimum peak level as fraction of max (0.0-1.0)

    Returns:
        List of timestamps (in seconds) with high audio volume
    """
    logger.debug("Detecting audio peaks (min_ratio=%.2f)", min_peak_ratio)
    # Use ffmpeg with astats to get per-frame audio stats
    # We'll analyze max_volume per frame
    cmd = ["ffmpeg", "-i", str(video), "-af", "astats=metadata=1:reset=1", "-f", "null", "-"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    peaks = []
    max_volume_seen = 0.0

    # First pass: find maximum volume overall
    for line in result.stderr.split("\n"):
        if "N=" in line and "max_volume=" in line:
            max_match = re.search(r"max_volume=([\d.-]+) dB", line)
            if max_match:
                vol = float(max_match.group(1))
                # Convert dB to linear ratio (approximate)
                linear = 10 ** (vol / 20) if vol < 0 else 1.0
                if linear > max_volume_seen:
                    max_volume_seen = linear

    # If no audio found
    if max_volume_seen == 0:
        logger.debug("No audio detected")
        return []

    # Second pass: collect peaks
    threshold_linear = max_volume_seen * min_peak_ratio
    cmd2 = ["ffmpeg", "-i", str(video), "-af", "astats=metadata=1:reset=1", "-f", "null", "-"]
    result2 = subprocess.run(cmd2, capture_output=True, text=True)

    for line in result2.stderr.split("\n"):
        if "N=" in line and "max_volume=" in line:
            time_match = re.search(r"t=([\d.]+)", line)
            vol_match = re.search(r"max_volume=([\d.-]+) dB", line)
            if time_match and vol_match:
                t = float(time_match.group(1))
                vol = float(vol_match.group(1))
                linear = 10 ** (vol / 20) if vol < 0 else 1.0
                if linear >= threshold_linear:
                    peaks.append(t)

    # Deduplicate close peaks
    if peaks:
        deduped = [peaks[0]]
        for ts in peaks[1:]:
            if ts - deduped[-1] >= 1.0:  # at least 1s apart
                deduped.append(ts)
        logger.debug("Found %d audio peaks", len(deduped))
        return deduped
    logger.debug("No audio peaks detected")
    return []


def cluster_timestamps(timestamps: list[float], max_gap: float = 5.0) -> list[list[float]]:
    """Group nearby timestamps into clusters."""
    if not timestamps:
        return []
    sorted_ts = sorted(timestamps)
    clusters = []
    current_cluster = [sorted_ts[0]]
    for ts in sorted_ts[1:]:
        if ts - current_cluster[-1] <= max_gap:
            current_cluster.append(ts)
        else:
            clusters.append(current_cluster)
            current_cluster = [ts]
    clusters.append(current_cluster)
    return clusters


def select_highlights(
    scenes: list[float],
    peaks: list[float],
    num_clips: int,
    clip_length: int,
    total_duration: float,
    strategy: list[str] | None = None,
) -> list[tuple[float, float]]:
    """
    Select highlight segments based on scene and audio detections.

    Args:
        scenes: Timestamps of scene changes
        peaks: Timestamps of audio peaks
        num_clips: Number of highlights to generate
        clip_length: Duration of each clip (seconds)
        total_duration: Total video duration
        strategy: Order of strategies to use, e.g. ["scene", "audio"].
                  If a strategy yields enough points, we use only those.
                  If not enough, we combine all and cluster.

    Strategy:
        1. If strategy is ["scene"] and scenes >= num_clips: pick top scene clusters
        2. If strategy is ["audio"] and peaks >= num_clips: pick top audio peaks
        3. If strategy is ["scene", "audio"]: combine and cluster all points
        4. If insufficient detections, fall back to even spacing
    """
    if strategy is None:
        strategy = ["scene", "audio"]

    # Decide which points to use based on strategy
    if strategy == ["scene"] and len(scenes) >= num_clips:
        points = scenes
    elif strategy == ["audio"] and len(peaks) >= num_clips:
        points = peaks
    elif "scene" in strategy and "audio" in strategy:
        points = sorted(set(scenes + peaks))
    else:
        # Mixed strategy not fully implementable; use combination anyway
        points = sorted(set(scenes + peaks))

    # Combine and cluster
    if not points:
        # Fallback to even spacing
        logger.debug("No detection points, falling back to even spacing")
        interval = total_duration / num_clips
        starts = [i * interval for i in range(num_clips)]
        return [(s, min(s + clip_length, total_duration)) for s in starts]

    clusters = cluster_timestamps(points, max_gap=5.0)
    logger.debug("Clustered into %d activity zones", len(clusters))

    # Score clusters: size (number of points) weighted
    cluster_scores = [(len(cluster), cluster) for cluster in clusters]
    cluster_scores.sort(key=lambda x: x[0], reverse=True)

    # Pick top clusters but ensure they're spread
    selected_starts: list[float] = []

    for score, cluster in cluster_scores:
        if len(selected_starts) >= num_clips:
            break
        # Use cluster midpoint as candidate
        midpoint = sum(cluster) / len(cluster)
        # Ensure clip fits within video bounds
        start = max(0, midpoint - clip_length / 2)
        end = start + clip_length
        if end > total_duration:
            start = total_duration - clip_length
            if start < 0:
                start = 0
            end = total_duration if start + clip_length > total_duration else start + clip_length
        # Check not too close to already selected
        too_close = any(abs(start - s) < (clip_length * 0.5) for s in selected_starts)
        if not too_close:
            selected_starts.append(start)

    # If we didn't get enough, fill with even spacing avoiding used zones
    if len(selected_starts) < num_clips:
        logger.debug(
            "Only %d highlights from clusters, filling to %d with even spacing",
            len(selected_starts),
            num_clips,
        )
        interval = total_duration / num_clips
        for i in range(num_clips):
            candidate = i * interval
            if not any(abs(candidate - s) < (clip_length * 0.5) for s in selected_starts):
                selected_starts.append(candidate)
                if len(selected_starts) >= num_clips:
                    break

    # Sort and convert to tuples
    selected_starts.sort()
    highlights = [(s, min(s + clip_length, total_duration)) for s in selected_starts[:num_clips]]
    logger.debug("Selected %d highlights: %s", len(highlights), highlights)
    return highlights
