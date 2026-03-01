"""Tests for metadata generation."""

from pathlib import Path

from mrclipper.metadata import write_metadata


def test_write_metadata_creates_file(tmp_path: Path, sample_video: Path):
    """Metadata sidecar file is created with correct fields."""
    output_clip = tmp_path / "test_clip.mp4"
    output_clip.touch()  # Create empty file

    metadata_path = write_metadata(
        output=output_clip,
        video=sample_video,
        start="00:00:10",
        duration=30,
        source_url="https://example.com/video",
        caption="Test caption",
        tags=["test", "sample"],
    )

    assert metadata_path.exists()
    import json

    with open(metadata_path) as f:
        data = json.load(f)

    assert data["title"] == sample_video.stem
    assert data["caption"] == "Test caption"
    assert data["tags"] == ["test", "sample"]
    assert data["source_url"] == "https://example.com/video"
    assert data["clip_start"] == "00:00:10"
    assert data["duration_seconds"] == 30
    assert data["file_path"] == str(output_clip)
    assert "created_at" in data


def test_write_metadata_auto_generate(sample_video: Path, tmp_path: Path):
    """Auto-generation uses video title and extracts tags."""
    output_clip = tmp_path / "auto_clip.mp4"
    output_clip.touch()

    metadata_path = write_metadata(
        output=output_clip,
        video=sample_video,
        start="00:00:05",
        duration=15,
        source_url=None,
        caption=None,
        tags=None,
    )

    import json

    with open(metadata_path) as f:
        data = json.load(f)

    assert data["caption"] is not None
    assert "title" in data
    assert data["tags"] is not None  # auto-generated from filename
    assert isinstance(data["tags"], list)


def test_write_metadata_with_template(sample_video: Path, tmp_path: Path):
    """Custom caption template is applied."""
    output_clip = tmp_path / "templated.mp4"
    output_clip.touch()

    template = "Video: {title} | Time: {start} | Duration: {duration}s | Link: {url}"
    metadata_path = write_metadata(
        output=output_clip,
        video=sample_video,
        start="00:01:00",
        duration=45,
        source_url="https://youtube.com/watch?v=123",
        caption=None,
        tags=None,
        caption_template=template,
    )

    import json

    with open(metadata_path) as f:
        data = json.load(f)

    expected = f"Video: {sample_video.stem} | Time: 00:01:00 | Duration: 45s | Link: https://youtube.com/watch?v=123"
    assert data["caption"] == expected
