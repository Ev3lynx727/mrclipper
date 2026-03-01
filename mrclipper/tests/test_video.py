"""Video function tests (requires sample video)."""

from pathlib import Path


def test_get_aspect_ratio():
    from mrclipper.video import get_aspect_ratio

    # We'll test with a dummy path later; for now just ensure importable
    assert callable(get_aspect_ratio)


def test_get_video_dimensions(sample_video: Path):
    from mrclipper.video import get_video_dimensions

    w, h = get_video_dimensions(sample_video)
    assert w > 0 and h > 0


def test_get_video_duration(sample_video: Path):
    from mrclipper.video import get_video_duration

    dur = get_video_duration(sample_video)
    assert dur > 0
