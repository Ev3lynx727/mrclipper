"""Regression tests for CLI config loading."""

import pytest
from pathlib import Path
from typer.testing import CliRunner
from mrclipper.cli import app
from unittest.mock import patch

runner = CliRunner()

def test_clip_with_custom_config_does_not_crash(tmp_path):
    """Verify that providing --config does not crash the clip command."""
    # Create a custom config that overrides something observable
    custom_config = tmp_path / "custom_config.toml"
    custom_config.write_text('[paths]\noutput = "/tmp/custom_output"')

    # Mock dependencies to avoid actual download/clipping
    with patch("mrclipper.cli.ensure_deps"), \
         patch("mrclipper.cli.download_video") as mock_download, \
         patch("mrclipper.cli.clip_video") as mock_clip, \
         patch("mrclipper.cli.temp_workdir") as mock_workdir:

        mock_workdir.return_value.__enter__.return_value = tmp_path
        mock_download.return_value = tmp_path / "video.mp4"

        # Run command
        result = runner.invoke(app, [
            "clip",
            "https://youtube.com/watch?v=123",
            "--start", "00:00:10",
            "--config", str(custom_config)
        ])

        # Check for crash (TypeError)
        assert result.exit_code == 0
        assert "Error" not in result.stderr

        # Verify custom config was used (injected via RuntimeContext)
        # clip_video is called with the merged cfg
        args, kwargs = mock_clip.call_args
        assert kwargs["cfg"]["paths"]["output"] == "/tmp/custom_output"

def test_auto_highlight_with_custom_config_does_not_crash(tmp_path):
    """Verify that providing --config does not crash the auto-highlight command."""
    custom_config = tmp_path / "custom_config.toml"
    custom_config.write_text('[clips]\nmax_highlights = 42')

    with patch("mrclipper.cli.ensure_deps"), \
         patch("mrclipper.cli.download_video") as mock_download, \
         patch("mrclipper.cli.detect_highlights") as mock_detect, \
         patch("mrclipper.cli.temp_workdir") as mock_workdir:

        mock_workdir.return_value.__enter__.return_value = tmp_path
        mock_download.return_value = tmp_path / "video.mp4"

        result = runner.invoke(app, [
            "auto-highlight",
            "https://youtube.com/watch?v=123",
            "--config", str(custom_config)
        ])

        if result.exit_code != 0:
            print(result.stdout)
            print(result.stderr)
        assert result.exit_code == 0
        args, kwargs = mock_detect.call_args
        assert kwargs["cfg"]["clips"]["max_highlights"] == 42
