"""Video probing utilities."""

from pathlib import Path

from .utils import run_cmd


def get_video_dimensions(video: Path) -> tuple[int, int]:
    """Return (width, height) using ffprobe."""
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height",
        "-of",
        "csv=s=x:p=0",
        str(video),
    ]
    out = run_cmd(cmd, "ffprobe dimensions").strip()
    w, h = out.split("x")
    return int(w), int(h)


def get_video_duration(video: Path) -> float:
    """Return duration in seconds using ffprobe."""
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(video),
    ]
    out = run_cmd(cmd, "ffprobe duration").strip()
    return float(out)


def get_aspect_ratio(video: Path) -> str:
    """Return aspect ratio as 'W:H' string."""
    w, h = get_video_dimensions(video)
    a, b = w, h
    while b:
        a, b = b, a % b
    gcd = a
    ar_w = w // gcd
    ar_h = h // gcd
    return f"{ar_w}:{ar_h}"
