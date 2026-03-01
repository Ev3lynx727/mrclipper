"""Pytest configuration and fixtures."""

from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def sample_video() -> Path:
    """Provide a small synthetic test video."""
    fixture_path = Path(__file__).parent / "fixtures" / "synthetic_1s.mp4"
    if not fixture_path.exists():
        pytest.skip(
            f"Test fixture not found: {fixture_path}. Run scripts/create_test_video.py to generate."
        )
    return fixture_path
