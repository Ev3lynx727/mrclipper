"""Basic CLI tests."""

from typer.testing import CliRunner

from mrclipper.cli import app

runner = CliRunner()


def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "mrclipper 1.0.1" in result.stdout


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Mr. Clipper" in result.stdout
    assert "clip" in result.stdout
    assert "auto-highlight" in result.stdout
    assert "config-validate" in result.stdout


def test_config_validate_missing():
    # Should error if config file doesn't exist
    result = runner.invoke(app, ["config-validate", "/nonexistent/config.toml"])
    assert result.exit_code == 1
    output = result.stdout + result.stderr
    assert "not found" in output.lower() or "Config error" in output
