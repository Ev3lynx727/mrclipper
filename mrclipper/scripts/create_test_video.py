#!/usr/bin/env python3
"""Generate a minimal test video (1s, color bars, silent)."""

import subprocess
from pathlib import Path


def create_test_video(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "test_video_1s.mp4"
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        "color=c=blue:s=320x240:d=1",
        "-f",
        "lavfi",
        "-i",
        "anullsrc=r=44100:cl=stereo",
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "23",
        "-c:a",
        "aac",
        str(output_file),
    ]
    print(f"Creating: {output_file}")
    subprocess.run(cmd, capture_output=True, check=True)
    return output_file


if __name__ == "__main__":
    out_dir = Path("tests/fixtures")
    video = create_test_video(out_dir)
    print(f"✅ Created: {video}")
