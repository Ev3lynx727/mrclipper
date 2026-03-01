"""Highlights detection tests."""

from pathlib import Path

from mrclipper.highlights import detect_highlights, select_highlights
from mrclipper.video import get_video_duration


def test_select_highlights_with_no_detections():
    """When no scene/audio points, fall back to even spacing."""
    total_dur = 30.0
    highlights = select_highlights([], [], num_clips=5, clip_length=6, total_duration=total_dur)
    assert len(highlights) == 5
    # Check even spacing
    expected_starts = [0.0, 6.0, 12.0, 18.0, 24.0]
    for i, (s, e) in enumerate(highlights):
        assert abs(s - expected_starts[i]) < 0.1, f"Start {s} != expected {expected_starts[i]}"
        assert abs(e - (s + 6)) < 0.1


def test_select_highlights_with_scenes():
    """Scenes should be used to pick highlights."""
    scenes = [5.0, 15.0, 25.0, 35.0, 45.0]
    peaks = []
    highlights = select_highlights(scenes, peaks, num_clips=3, clip_length=5, total_duration=60.0)
    assert len(highlights) == 3
    # The top 3 scene clusters should be chosen
    starts = [s for s, e in highlights]
    # They should be near the scene points (midpoint)
    for s in starts:
        # Each start should be within 2.5s of a scene point
        assert any(abs(s - scene) <= 2.5 for scene in scenes)


def test_select_highlights_strategy_scenes_only():
    """Strategy ['scene'] should use only scenes even if peaks present."""
    scenes = [10.0, 20.0, 30.0]
    peaks = [5.0, 15.0, 25.0, 35.0, 45.0]  # more peaks
    highlights = select_highlights(
        scenes, peaks, num_clips=3, clip_length=5, total_duration=60.0, strategy=["scene"]
    )
    starts = [s for s, e in highlights]
    # Should be near scene points, not peaks
    for s in starts:
        assert any(abs(s - scene) <= 2.5 for scene in scenes)


def test_select_highlights_strategy_audio_only():
    """Strategy ['audio'] should use only peaks."""
    scenes = [10.0, 20.0, 30.0]
    peaks = [15.0, 25.0, 35.0, 45.0]
    highlights = select_highlights(
        scenes, peaks, num_clips=2, clip_length=5, total_duration=60.0, strategy=["audio"]
    )
    starts = [s for s, e in highlights]
    for s in starts:
        assert any(abs(s - peak) <= 2.5 for peak in peaks)


def test_highlights_create_clips(sample_video: Path, tmp_path: Path):
    """Integration: detect_highlights creates actual clip files."""
    output_dir = tmp_path / "highlights"
    cfg = {
        "clips": {"max_highlights": 2, "highlight_length": 1},
        "highlights": {
            "strategy": ["scene", "audio"],
            "scene_threshold": 0.4,
            "audio_min_peak_db": -20.0,
        },
    }
    result_dir = detect_highlights(sample_video, output_dir, cfg=cfg)
    clips = sorted(result_dir.glob("*.mp4"))
    assert len(clips) == 2
    # Verify each clip is at least 1s long (may be shorter if video too short)
    for clip in clips:
        # Use ffprobe to check duration > 0
        import subprocess

        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(clip),
        ]
        dur = float(subprocess.run(cmd, capture_output=True, text=True).stdout.strip())
        assert dur > 0


def test_get_video_duration(sample_video: Path):

    dur = get_video_duration(sample_video)
    assert dur > 0
