# Mr. Clipper: Architectural Deep-Dive Analysis

## 1. Executive Summary
Mr. Clipper (v1.0.1) is a sophisticated, modular video processing system designed for intelligent highlight extraction and clipping. It follows a "Core Engine + CLI + Skill Wrapper" architectural pattern, prioritizing maintainability, typed configuration, and robust integration with external multimedia tools like `ffmpeg` and `yt-dlp`. Recent refactoring has further streamlined command initialization and content analysis.

## 2. High-Level Architecture

### 2.1 Component Overview
The repository is organized into three primary layers:
1.  **Core Engine (`mrclipper/mrclipper/`):** A modular Python package containing the domain logic for downloading, probing, clipping, and intelligent analysis.
2.  **CLI Layer (`mrclipper/mrclipper/cli.py`):** A `Typer`-powered interface that orchestrates the core components into user-facing commands (`clip`, `auto_highlight`, `search`). It uses a centralized `RuntimeContext` for shared state management.
3.  **Integration Layer (`skills/video-clipper/`):** A thin delegation wrapper that exposes the CLI as an OpenClaw skill, allowing for agentic and cron-based automation.

### 2.2 Data Flow
1.  **Initialization:** The CLI initializes a `RuntimeContext` which lazily loads configuration (Pydantic models) and sets up manifest/logging. It merges defaults, global settings (`~/.config/mrclipper/config.toml`), and job-specific overrides.
2.  **Ingestion:** `download_video` uses `yt-dlp` to fetch content. Operations are recorded in a persistent `manifest.jsonl`.
3.  **Processing:**
    *   **Probing:** `ffprobe` extracts dimensions, duration, and aspect ratio.
    *   **Analysis (Mode B):** For highlights, `ffmpeg` filters (`scene`, `astats`) are used to detect visual transitions and audio peaks. Audio analysis is optimized to a single pass.
    *   **Transformation:** `ffmpeg` handles aspect ratio conversion (padding/scaling), subtitle burning, and stream-copy clipping.
4.  **Output:** Clips are saved alongside `.metadata.json` sidecar files, which contain generated captions and tags for downstream publishing.

## 3. Core Architectural Pillars

### 3.1 Typed & Validated Configuration
The system leverages **Pydantic v2** (`config_models.py`) to enforce strict validation rules:
*   **Safety:** CRF values, presets, and aspect ratios are validated at load time.
*   **Flexibility:** Recursive merging allows for global defaults with granular job-level overrides.
*   **DX:** Path expansion and type-hinting improve developer experience and reduce runtime errors.

### 3.2 Intelligent Highlights (Mode B)
The highlight detection engine (`highlights.py`, `scene_detector.py`) implements a multi-stage pipeline:
*   **Detection:** Parallel analysis of scene changes and optimized single-pass audio peaks.
*   **Clustering:** Temporal grouping of detection points to identify "activity zones."
*   **Scoring & Selection:** A strategy-based selector picks the best segments while enforcing spatial spread across the video duration.
*   **Fallback:** Graceful degradation to even-spacing heuristics if signals are insufficient.

### 3.3 Robustness & Observability
*   **Manifesting:** A singleton `DownloadManifest` tracks the lifecycle of every operation, enabling statistics and history tracking.
*   **Retry Logic:** A custom `@retry` decorator with exponential backoff handles transient network failures during downloads.
*   **Exception Handling:** A dedicated hierarchy (`MrClipperError`, `ProcessingError`, etc.) ensures that external tool failures (ffmpeg/yt-dlp) are captured with full context (stderr) and reported cleanly.
*   **Structured Logging:** Multi-level logging (DEBUG/INFO/WARNING) with both console and rotating file handlers.

## 4. External Dependencies
The architecture relies on a "subprocess-as-engine" model:
*   **yt-dlp:** For robust video and subtitle ingestion across 1000+ sites.
*   **ffmpeg/ffprobe:** For all multimedia transformations and content analysis.
The system is "engine-agnostic" in its interface but highly optimized for these specific tools, validating their presence via `ensure_deps()` at startup.

## 5. Integration Patterns
*   **mrpublisher Ready:** By generating `.metadata.json` sidecars, Mr. Clipper enables a decoupled "Clip -> Publish" workflow.
*   **OpenClaw Skill:** The skill wrapper uses a simple delegation pattern (`subprocess.run(["mrclipper"] + sys.argv[1:])`), ensuring that the skill remains thin while the core package evolves independently.

## 6. Testing Strategy
The repository maintains a high-quality test suite (`tests/`):
*   **Unit Tests:** Coverage for config merging, metadata generation, and the retry mechanism.
*   **Integration Tests:** End-to-end verification of the clipping pipeline using synthetic fixtures.
*   **CLI Tests:** Verification of command-line arguments and exit codes using `CliRunner`.

## 7. Future Architectural Evolution
The architecture is primed for:
*   **GPU Acceleration:** Further optimization of the `ffmpeg` pipeline for hardware-accelerated encoding.
*   **Advanced Signals:** Integration of optical flow or face detection into the highlight scorer.
*   **Distributed Workers:** The modular CLI/package split allows for moving the processing to remote worker nodes in a cluster.

---
**Analyst:** Jules (Senior Systems Architect)
**Date:** 2024-05-23 (Updated)
