"""Logging configuration."""

import logging
import logging.handlers
import sys
from pathlib import Path


def setup_logging(verbose: bool = False, quiet: bool = False, log_file: Path | None = None):
    """Configure mrclipper logger with console and optional file output.

    Args:
        verbose: Enable DEBUG logging to console
        quiet: Suppress INFO, show only WARNING+
        log_file: Path to log file (rotating, 5MB max, 3 backups). If None, file logging disabled.
    """
    logger = logging.getLogger("mrclipper")
    logger.setLevel(logging.DEBUG)  # Capture all; handlers filter

    # Console handler
    console_handler = logging.StreamHandler(sys.stderr)
    if quiet:
        console_level = logging.WARNING
    elif verbose:
        console_level = logging.DEBUG
    else:
        console_level = logging.INFO

    console_formatter = logging.Formatter("[%(levelname)s] %(message)s")
    console_handler.setLevel(console_level)
    console_handler.setFormatter(console_formatter)

    # File handler (if requested)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)  # Log everything to file
        file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # Avoid adding multiple console handlers on re-setup
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        logger.addHandler(console_handler)

    return logger
