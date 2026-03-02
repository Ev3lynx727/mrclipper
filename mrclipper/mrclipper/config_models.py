"""Typed configuration models using Pydantic v2."""

from pathlib import Path

from pydantic import BaseModel, Field, field_validator


class OutputConfig(BaseModel):
    format: str = Field("mp4", pattern=r"^(mp4|mov|mkv)$")
    codec: str = Field("libx264", description="Video codec")
    crf: int = Field(23, ge=18, le=28, description="Quality (lower=better)")
    preset: str = Field("fast", description="Encoding preset")


class PathsConfig(BaseModel):
    workdir: str = Field("/tmp/vr-clipper", description="Temporary work directory")
    output: str = Field(str(Path.home() / "Videos" / "MrClipper"), description="Output directory")
    log_file: str = Field(
        default_factory=lambda: str(
            Path.home() / ".local" / "share" / "mrclipper" / "mrclipper.log"
        ),
        description="Log file path for persistent logging",
    )

    @field_validator("workdir", "output", "log_file")
    @classmethod
    def expand_user(cls, v: str) -> str:
        return str(Path(v).expanduser())


class SubtitlesConfig(BaseModel):
    mode: str = Field("soft", pattern=r"^(soft|burn|none)$")
    languages: list[str] = Field(default_factory=lambda: ["en"])
    auto_generate: bool = False


class AspectConfig(BaseModel):
    default: str = Field("auto", pattern=r"^(auto|source|16:9|9:16|1:1|4:3)$")
    pad_color: str = Field("black", pattern=r"^(black|white|blur)$")


class ClipsConfig(BaseModel):
    default_duration: int = Field(30, gt=0)
    max_highlights: int = Field(5, gt=0)
    highlight_length: int = Field(30, gt=0)


class YtDlpConfig(BaseModel):
    format: str = Field("best[ext=mp4]")


class PublisherConfig(BaseModel):
    """Configuration for mrpublisher integration."""

    caption_template: str | None = Field(
        None,
        description="Template for auto-generated captions. Placeholders: {title}, {start}, {duration}, {url}",
    )
    default_tags: list[str] = Field(
        default_factory=list, description="Default tags to add to every clip"
    )
    auto_generate_tags: bool = Field(True, description="Generate tags from title if true")


class ManifestConfig(BaseModel):
    """Downloads manifest settings."""

    enabled: bool = Field(True, description="Enable manifest tracking")
    path: str = Field(
        default_factory=lambda: str(
            Path.home() / ".local" / "share" / "mrclipper" / "manifest.jsonl"
        ),
        description="Path to manifest JSONL file",
    )


class HighlightsConfig(BaseModel):
    """Not yet used in config; placeholder for Phase 4."""

    strategy: list[str] = Field(default_factory=lambda: ["scene", "audio"])
    num_clips: int = Field(5, gt=0)
    clip_length: int = Field(30, gt=0)
    scene_threshold: float = Field(0.4, ge=0.0, le=1.0)
    audio_min_peak_db: float = Field(-20.0)


class MrClipperConfig(BaseModel):
    output: OutputConfig = OutputConfig()
    paths: PathsConfig = PathsConfig()
    subtitles: SubtitlesConfig = SubtitlesConfig()
    aspect: AspectConfig = AspectConfig()
    clips: ClipsConfig = ClipsConfig()
    yt_dlp: YtDlpConfig = YtDlpConfig()
    manifest: ManifestConfig = ManifestConfig()
    publisher: PublisherConfig = PublisherConfig()  # New: mrpublisher integration
    highlights: HighlightsConfig = HighlightsConfig()

    model_config = {"extra": "ignore"}  # Allow unknown keys for forward compatibility

    @classmethod
    def load(
        cls, global_path: Path | None = None, job_path: Path | None = None
    ) -> "MrClipperConfig":
        """Load config from global and optional job file, with merging."""
        # Start with defaults
        cfg_data = cls.model_dump(cls())

        # Load global
        if global_path is None:
            global_path = Path.home() / ".config" / "mrclipper" / "config.toml"
        if global_path.exists():
            import toml

            with open(global_path) as f:
                global_cfg = toml.load(f)
                deep_update(cfg_data, global_cfg)

        # Load job (overrides global)
        if job_path and job_path.exists():
            import toml

            with open(job_path) as f:
                job_cfg = toml.load(f)
                deep_update(cfg_data, job_cfg)

        return cls(**cfg_data)


def deep_update(base: dict, override: dict) -> dict:
    """Recursively merge override into base. Returns the updated base."""
    for k, v in override.items():
        if isinstance(v, dict) and k in base and isinstance(base[k], dict):
            deep_update(base[k], v)
        else:
            base[k] = v
    return base
