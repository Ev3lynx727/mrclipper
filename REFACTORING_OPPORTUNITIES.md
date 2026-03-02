# Mr. Clipper: Refactoring Opportunities & Technical Debt Analysis

Following a deep-dive architectural review, several areas for refactoring have been identified to improve the robustness, efficiency, and maintainability of the `mrclipper` codebase.

## 1. Scene Detection Optimization (`scene_detector.py`)

### Opportunity: Single-Pass Audio Peak Detection
**Current State:** `detect_audio_peaks` runs `ffmpeg` twice. The first pass finds the global maximum volume, and the second pass collects timestamps that exceed a threshold based on that maximum.
**Technical Debt:** This doubles the processing time for audio analysis.
**Proposed Solution:** Use a single `ffmpeg` pass to extract per-frame `max_volume` data into memory. Calculate the threshold from the extracted data and then filter for peaks in-memory.

### Opportunity: Unified Metadata Extraction
**Current State:** `detect_scene_changes` and `detect_audio_peaks` run separate `ffmpeg` commands.
**Proposed Solution:** Combine scene detection and audio stats into a single `ffmpeg` filtergraph:
```bash
ffmpeg -i input -vf "select='gt(scene,0.4)',metadata=print" -af "astats=metadata=1" -f null -
```
This would allow visual and auditory signals to be processed in parallel during a single read of the video file.

---

## 2. Robustness in Download Handling (`download.py`)

### Opportunity: Explicit File Discovery
**Current State:** `download_video` relies on `workdir.glob("*.mp4")` and sorting by `mtime` to find the downloaded file.
**Technical Debt:** This is fragile if multiple files exist or if `yt-dlp` outputs a different extension (e.g., `.mkv`, `.webm`).
**Proposed Solution:** Use `yt-dlp`'s `--print filename` or the Python API to get the exact output path directly from the tool, rather than guessing based on directory state.

---

## 3. CLI Boilerplate Reduction (`cli.py`)

### Opportunity: Standardized Command Initialization
**Current State:** Every major command (`clip`, `auto_highlight`, `search`) repeats the `ensure_deps()`, `load_config()`, and `initialize_runtime()` sequence.
**Technical Debt:** Violates DRY (Don't Repeat Yourself) principle; making changes to the initialization flow requires updating multiple locations.
**Proposed Solution:** Move this boilerplate into a common decorator or a `typer` callback that populates a context object for all subcommands.

---

## 4. Manifest Lifecycle Management (`manifest.py` & `cli.py`)

### Opportunity: Early Manifest Initialization
**Current State:** The `manifest` singleton has its `path` property set late in the `initialize_runtime` call in `cli.py`.
**Technical Debt:** Modules like `download.py` have to check for `manifest_path` before recording, and the singleton pattern is partially broken by manual path setting at runtime.
**Proposed Solution:** Pass the manifest instance (or its configuration) explicitly through the functional pipeline, or ensure `initialize_runtime` is the absolute first action taken by the CLI before any business logic is invoked.

---

## 5. Subtitle Handling Logic (`subtitles.py`)

### Opportunity: Standardized Subtitle Processing
**Current State:** `burn_subtitles` re-encodes the video to hard-burn subtitles.
**Proposed Solution:** Implement a "Soft-to-Hard" toggle that can be handled during the main clipping `ffmpeg` pass to avoid an extra re-encoding step if both clipping and burning are requested.

---

## Summary of Impact
| Target | Effort | Impact |
|--------|--------|--------|
| `scene_detector` Single-Pass | Medium | **High** (Reduces analysis time by ~50%) |
| `download` Explicit Path | Low | **High** (Eliminates "file not found" edge cases) |
| `cli` DRY Initialization | Low | Medium (Improves maintainability) |
| `ffmpeg` Filtergraph Union | High | **High** (Significant performance gain for Mode B) |

---
**Analyst:** Jules (Senior Systems Architect)
**Date:** 2024-05-23
