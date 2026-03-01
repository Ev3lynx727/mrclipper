"""Configuration loading (now powered by Pydantic)."""

from pathlib import Path

from .config_models import MrClipperConfig


def load_config(config_path: Path | None = None) -> dict:
    """Load global config, optionally overridden by job config. Returns plain dict."""
    cfg = MrClipperConfig.load(job_path=config_path)
    return cfg.model_dump()
