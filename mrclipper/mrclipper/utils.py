"""Utilities: command execution, deps, temp dirs, retry."""

import functools
import logging
import shutil
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path

logger = logging.getLogger("mrclipper")


def run_cmd(cmd: list[str], desc: str = "", raise_on_error: bool = True) -> str:
    """Run subprocess command, return stdout. Optionally raise exception."""
    logger.debug("Running: %s", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error("%s failed: %s", desc, result.stderr)
        if raise_on_error:
            raise subprocess.CalledProcessError(result.returncode, cmd, result.stderr)
    return result.stdout


def ensure_deps():
    """Check required binaries exist."""
    for bin in ["yt-dlp", "ffmpeg", "ffprobe"]:
        try:
            subprocess.run([bin, "--version"], capture_output=True, check=False)
        except FileNotFoundError:
            logger.error("Missing required binary: %s", bin)
            sys.exit(1)


@contextmanager
def temp_workdir(base: Path):
    """Temporary workdir that auto-cleans."""
    import uuid

    run_id = uuid.uuid4().hex[:8]
    workdir = base / f"run_{run_id}"
    workdir.mkdir(parents=True, exist_ok=True)
    try:
        yield workdir
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def retry(
    tries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (subprocess.CalledProcessError, ConnectionError, TimeoutError),
):
    """Retry decorator for functions that may fail transiently."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _tries, _delay = tries, delay
            for i in range(tries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if i == tries - 1:
                        raise
                    logger.warning("Retry %d/%d after error: %s", i + 1, tries, e)
                    time.sleep(_delay)
                    _delay *= backoff
            return None  # shouldn't get here

        return wrapper

    return decorator
