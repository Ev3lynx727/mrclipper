# Changelog

All notable changes to mrclipper will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0.html),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2026-03-02

### Added
- **Intelligent highlights (Mode B)**: Scene change detection + audio peak analysis
- **Configurable highlight strategy**: Choose `["scene"]`, `["audio"]`, `["scene+audio"]`, or `["even"]`
- **Modular architecture**: Refactored monolith into `mrclipper` package (backward compatible)
- **Typed configuration**: Pydantic v2 models with validation
- **Typer CLI**: Subcommands (`clip`, `auto-highlight`, `config-validate`) with auto-help
- **Structured logging**: Python `logging` module with levels
- **Custom exceptions**: `DownloadError`, `ProcessingError`, `MrClipperError`
- **Retry logic**: Automatic retries for network failures (yt-dlp)
- **Pre-commit hooks**: black, ruff, mypy
- **CI/CD**: GitHub Actions workflow (multi-Python, lint, type-check, tests)
- **Coverage reporting**: pytest-cov integration

### Changed
- Default highlight detection: now content-aware (scene + audio) instead of even spacing
- Config merging order: job > global > defaults (unchanged behavior but now validated)
- Logging: replaced print-based with standard logging
- Package install: `pip install -e .` provides `mrclipper` command (replaces old `clip.py`)

### Fixed
- Numerous edge cases in aspect ratio conversion and subtitle handling
- Better error messages for ffmpeg/yt-dlp failures

### Deprecated
- Old `clip.py` script (use `mrclipper` command instead)

## [1.0.0] - 2025-??-??

Initial release of Mr. Clipper with:
- Soft subtitle extraction (yt-dlp --write-subs)
- Aspect ratio control (auto + forcing: 16:9, 9:16, 1:1, 4:3)
- TOML configuration system (global + per-job)
- Basic auto-highlights (even spacing)
- OpenClaw agent integration
- Full documentation suite
