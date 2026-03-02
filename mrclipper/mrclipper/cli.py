"""CLI entry point using Typer."""

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import typer
from typing_extensions import Annotated

from . import __version__
from .aspect import process_aspect_ratio
from .clip import clip_video
from .config import load_config
from .config_models import deep_update
from .download import download_video, find_subtitle_file
from .exceptions import MrClipperError
from .highlights import detect_highlights
from .logging_config import setup_logging
from .manifest import DownloadManifest, manifest
from .subtitles import burn_subtitles
from .utils import ensure_deps, temp_workdir

app = typer.Typer(
    name="mrclipper",
    help="Mr. Clipper — Advanced video clipper for OpenClaw",
    add_completion=True,
)


@dataclass
class RuntimeContext:
    """Shared runtime context for all CLI commands."""

    config: dict[str, Any]
    manifest: DownloadManifest
    verbose: bool
    quiet: bool


@app.command()
def manifest_recent(
    limit: int = typer.Option(20, "--limit", "-n", help="Number of entries to show"),
    operation: str | None = typer.Option(
        None, "--operation", "-o", help="Filter by operation type"
    ),
):
    """Show recent operations from manifest."""
    entries = manifest.recent(limit=limit, operation=operation)
    if not entries:
        typer.echo("No manifest entries found.")
        return
    for entry in entries:
        ts = entry.get("timestamp", "")[:19].replace("T", " ")
        op = entry.get("operation", "?")
        success = "✓" if entry.get("success") else "✗"
        out = entry.get("output_file", "")
        url = entry.get("url", "")
        typer.echo(f"{ts} [{op}] {success} {out or url}")


@app.command()
def manifest_stats(
    days: int = typer.Option(7, "--days", "-d", help="Number of days to include in stats"),
):
    """Show statistics from manifest."""
    stats = manifest.stats(days=days)
    typer.echo(f"📊 Mr. Clipper Manifest Statistics (last {days} days)")
    typer.echo(f"   Total entries: {stats['total_entries']}")
    typer.echo(f"   Successful: {stats['successful']}")
    typer.echo(f"   Failed: {stats['failed']}")
    typer.echo(f"   Success rate: {stats['success_rate']}%")
    typer.echo(f"   Avg duration: {stats['avg_duration_seconds']}s")


def version_callback(value: bool):
    if value:
        typer.echo(f"mrclipper {__version__}")
        raise typer.Exit()


def get_config_path(config: Optional[Path]) -> Optional[Path]:
    """Resolve config path from CLI option."""
    if config is None:
        default_path = Path.home() / ".config" / "mrclipper" / "config.toml"
        return default_path if default_path.exists() else None
    return config


@app.callback(invoke_without_command=True)
def common(
    ctx: typer.Context,
    version: bool = typer.Option(
        False, "--version", "-V", callback=version_callback, help="Show version and exit"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable debug logging"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress info logs"),
    config: Annotated[
        Optional[Path], typer.Option("-c", "--config", help="Config file path")
    ] = None,
):
    """Common options for all commands."""
    ctx.obj = {"verbose": verbose, "quiet": quiet, "config_path": get_config_path(config)}


def get_runtime(ctx: typer.Context) -> RuntimeContext:
    """Get or initialize runtime context.

    Uses lazy initialization to avoid loading config for commands that don't need it
    (like manifest commands).
    """
    if "runtime" not in ctx.obj:
        verbose = ctx.obj.get("verbose", False)
        quiet = ctx.obj.get("quiet", False)
        config_path = ctx.obj.get("config_path")

        # Setup console logging first
        log_file_path = None
        if config_path and config_path.exists():
            try:
                cfg = load_config(config_path)
                log_file_path = cfg.get("paths", {}).get("log_file")
            except Exception:
                pass

        if log_file_path:
            log_file = Path(log_file_path).expanduser()
        else:
            log_file = Path.home() / ".local" / "share" / "mrclipper" / "mrclipper.log"
        setup_logging(verbose=verbose, quiet=quiet, log_file=log_file)

        # Load config and initialize manifest
        cfg = load_config(config_path) if config_path else load_config(None)

        manifest_enabled = cfg.get("manifest", {}).get("enabled", True)
        manifest_path = cfg.get("manifest", {}).get("path")
        if manifest_enabled:
            if manifest_path:
                manifest.path = Path(manifest_path).expanduser()
            else:
                manifest.path = Path.home() / ".local" / "share" / "mrclipper" / "manifest.jsonl"
            logger = logging.getLogger("mrclipper")
            logger.info("Manifest logging enabled: %s", manifest.path)
        else:
            logger = logging.getLogger("mrclipper")
            logger.info("Manifest logging disabled")

        ctx.obj["runtime"] = RuntimeContext(
            config=cfg,
            manifest=manifest,
            verbose=verbose,
            quiet=quiet,
        )

    return ctx.obj["runtime"]


@app.command()
def clip(
    ctx: typer.Context,
    url: str = typer.Argument(..., help="Video URL (YouTube or supported site)"),
    start: str = typer.Option(..., "--start", "-s", help="Start time (HH:MM:SS)"),
    duration: int = typer.Option(30, "--duration", "-d", help="Clip duration in seconds"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Output file path"),
    config: Path | None = typer.Option(None, "--config", "-c", help="Job-specific TOML config"),
    aspect: str | None = typer.Option(
        None, "--aspect", "-a", help="Target aspect ratio (16:9, 9:16, 1:1, 4:3, auto)"
    ),
    burn_subs: bool = typer.Option(
        False, "--burn-subs", help="Burn subtitles into video (re-encode)"
    ),
    caption: str | None = typer.Option(
        None, "--caption", help="Custom caption for metadata (overrides config)"
    ),
    tags: str | None = typer.Option(
        None, "--tags", help="Comma-separated tags for metadata (overrides config)"
    ),
):
    """Clip a video from URL."""
    try:
        # Handle config override from CLI
        if config:
            ctx.obj["config_path"] = config

        runtime = get_runtime(ctx)
        ensure_deps()
        cfg = runtime.config

        # Merge job-specific config if provided
        if config and config.exists():
            job_cfg = load_config(config)
            cfg = deep_update(cfg.copy(), job_cfg)

        workdir_base = Path(cfg["paths"].get("workdir", "/tmp/vr-clipper"))
        with temp_workdir(workdir_base) as workdir:
            video_file = download_video(url, workdir, cfg)
            typer.echo(f"Downloaded: {video_file}", err=True)
            processed_video: Path = video_file
            # Aspect ratio processing
            target_aspect = aspect or cfg["aspect"].get("default", "auto")
            if target_aspect not in ["auto", "source"]:
                aspect_out = workdir / f"aspect_{video_file.name}"
                processed_video = process_aspect_ratio(
                    video_file, aspect_out, target_aspect, cfg["aspect"].get("pad_color", "black")
                )
            # Subtitles
            sub_file: Path | None = None
            subs_mode = cfg["subtitles"].get("mode", "soft")
            if subs_mode != "none":
                sub_file = find_subtitle_file(video_file)
                if not sub_file:
                    typer.echo("No subtitle file found", err=True)
            if burn_subs and sub_file:
                burned_out = workdir / f"burned_{processed_video.name}"
                processed_video = burn_subtitles(processed_video, sub_file, burned_out)
                sub_file = None  # already burned, don't pass to clip
            # Determine output path
            if output is None:
                output_dir = Path(cfg["paths"].get("output", "/tmp/vr-clipper"))
                output_dir.mkdir(parents=True, exist_ok=True)
                vid_name = processed_video.stem
                output = output_dir / f"{vid_name}_clip_{start.replace(':', '-')}.mp4"
            # Parse tags if provided
            tag_list = None
            if tags:
                tag_list = [t.strip() for t in tags.split(",") if t.strip()]
            # Clip
            clip_video(
                processed_video,
                start,
                duration,
                output,
                sub_file,
                cfg=cfg,
                source_url=url,
                caption=caption,
                tags=tag_list,
            )
            typer.echo(str(output))
    except MrClipperError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(2)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        raise typer.Exit(2)


@app.command()
def auto_highlight(
    ctx: typer.Context,
    url: str = typer.Argument(..., help="Video URL"),
    output: Path | None = typer.Option(
        None, "--output", "-o", help="Output directory for highlights"
    ),
    config: Path | None = typer.Option(None, "--config", "-c", help="Job-specific TOML config"),
    caption: str | None = typer.Option(
        None, "--caption", help="Custom caption template for highlights"
    ),
    tags: str | None = typer.Option(None, "--tags", help="Comma-separated tags for highlights"),
):
    """Auto-detect highlights from a video."""
    try:
        if config:
            ctx.obj["config_path"] = config

        runtime = get_runtime(ctx)
        ensure_deps()
        cfg = runtime.config

        if config and config.exists():
            job_cfg = load_config(config)
            cfg = deep_update(cfg.copy(), job_cfg)

        workdir_base = Path(cfg["paths"].get("workdir", "/tmp/vr-clipper"))
        with temp_workdir(workdir_base) as workdir:
            video_file = download_video(url, workdir, cfg)
            typer.echo(f"Downloaded: {video_file}", err=True)
            processed_video: Path = video_file
            target_aspect = cfg["aspect"].get("default", "auto")
            if target_aspect not in ["auto", "source"]:
                aspect_out = workdir / f"aspect_{video_file.name}"
                processed_video = process_aspect_ratio(
                    video_file, aspect_out, target_aspect, cfg["aspect"].get("pad_color", "black")
                )
            # Parse tags if provided
            tag_list = None
            if tags:
                tag_list = [t.strip() for t in tags.split(",") if t.strip()]
            # Add publisher overrides to cfg
            if caption or tags:
                cfg.setdefault("publisher", {})
                if caption:
                    cfg["publisher"]["caption_template"] = caption
                if tag_list:
                    cfg["publisher"]["default_tags"] = tag_list
                    cfg["publisher"]["auto_generate_tags"] = False
            # Determine output dir
            if output is None:
                output_dir = Path(cfg["paths"].get("output", "/tmp/vr-clipper"))
                output_dir = output_dir / f"highlights_{int(time.time())}"
            else:
                output_dir = output
            result_dir = detect_highlights(processed_video, output_dir, cfg=cfg)
            typer.echo(str(result_dir))
    except MrClipperError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(2)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        raise typer.Exit(2)


@app.command()
def config_validate(
    path: Path = typer.Argument(
        Path.home() / ".config" / "mrclipper" / "config.toml", help="Path to config TOML"
    ),
):
    """Validate a configuration file."""
    if not path.exists():
        typer.echo(f"Config file not found: {path}", err=True)
        raise typer.Exit(1)
    try:
        load_config(path)  # Just validate, don't need to store
        typer.echo("Config is valid")
    except Exception as e:
        typer.echo(f"Config error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def search(
    ctx: typer.Context,
    query: str = typer.Argument(..., help="Search query (e.g., 'AI trends 2024')"),
    limit: int = typer.Option(5, "--limit", "-l", help="Number of results to download"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Output directory"),
    config: Path | None = typer.Option(None, "--config", "-c", help="Job-specific TOML config"),
):
    """Search YouTube and download top results.

    Uses yt-dlp's ytsearch: prefix to find videos by query.
    Downloads up to `limit` videos matching the search.
    """
    try:
        if config:
            ctx.obj["config_path"] = config

        runtime = get_runtime(ctx)
        ensure_deps()
        cfg = runtime.config

        if config and config.exists():
            job_cfg = load_config(config)
            cfg = deep_update(cfg.copy(), job_cfg)

        output_dir = output or Path(cfg["paths"].get("output", "/tmp/vr-clipper"))
        output_dir.mkdir(parents=True, exist_ok=True)

        typer.echo(f"Searching YouTube for: {query}", err=True)
        yt_opts = cfg.get("yt-dlp", {}).get("format", "best[ext=mp4]")

        # Build yt-dlp command with ytsearch:
        search_template = f"ytsearch{limit}:{yt_opts}:{query}"
        cmd = [
            "yt-dlp",
            "--output",
            str(output_dir / "%(title)s.%(ext)s"),
            "--no-playlist",
            "--restrict-filenames",
            search_template,
        ]
        subs_mode = cfg.get("subtitles", {}).get("mode", "soft")
        langs = cfg.get("subtitles", {}).get("languages", ["en"])
        if subs_mode != "none":
            cmd.extend(["--write-subs", "--sub-lang", ",".join(langs)])

        typer.echo(f"Downloading up to {limit} videos...", err=True)
        import subprocess as _subprocess

        result = _subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise MrClipperError(f"Search download failed: {result.stderr}")

        downloaded = []
        for line in result.stderr.split("\n"):
            if "Destination:" in line:
                path = line.split("Destination:", 1)[1].strip()
                downloaded.append(Path(path))

        typer.echo(f"Downloaded {len(downloaded)} video(s) to: {output_dir}")
        for p in downloaded:
            typer.echo(f"  - {p.name}", err=True)

    except MrClipperError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(2)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        raise typer.Exit(2)


if __name__ == "__main__":
    app()
