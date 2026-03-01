"""Custom exception hierarchy."""


class MrClipperError(RuntimeError):
    """Base exception for mrclipper errors."""


class ConfigurationError(MrClipperError):
    """Configuration loading/validation error."""


class DownloadError(MrClipperError):
    """Video download failed."""


class ProcessingError(MrClipperError):
    """Video processing (ffmpeg) failed."""
