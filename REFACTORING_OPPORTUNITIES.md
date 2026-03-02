# Mr. Clipper: Refactoring Opportunities & Technical Debt Analysis

Following a deep-dive architectural review and subsequent refactoring (Commit 2cde237), several areas for improvement have been identified. While some key debts have been cleared, further opportunities remain.

## 1. Scene Detection & Analysis (`scene_detector.py`)

### ✅ COMPLETED: Single-Pass Audio Peak Detection
`detect_audio_peaks` has been refactored to use a single `ffmpeg` pass, extracting all frame data into memory for analysis. This reduces audio analysis time by approximately 50%.

### Opportunity: Unified Metadata Extraction (Visual + Audio)
**Current State:** `detect_scene_changes` and `detect_audio_peaks` still run separate `ffmpeg` commands for visual scene changes and audio volume stats.
**Proposed Solution:** Combine scene detection and audio stats into a single unified `ffmpeg` filtergraph:
```bash
ffmpeg -i input -vf "select='gt(scene,0.4)',metadata=print" -af "astats=metadata=1" -f null -
```
This would allow visual and auditory signals to be processed in parallel during a single read of the video file, further halving the analysis phase duration.

---

## 2. Robustness in Download Handling (`download.py`)

### Opportunity: Explicit File Discovery
**Current State:** `download_video` relies on `workdir.glob("*.mp4")` and sorting by `mtime` to find the downloaded file.
**Technical Debt:** This is fragile if multiple files exist or if `yt-dlp` outputs a different extension (e.g., `.mkv`, `.webm`).
**Proposed Solution:** Use `yt-dlp`'s `--print filename` or the Python API to get the exact output path directly from the tool, rather than guessing based on directory state.

---

## 3. CLI Boilerplate & Context (`cli.py`)

### ✅ COMPLETED: Standardized Command Initialization
The CLI has been refactored to use a centralized `RuntimeContext` and a lazy-loading `get_runtime(ctx)` helper. This eliminated the repetitive initialization sequence across `clip`, `auto_highlight`, and `search` commands.

### Opportunity: Explicit Manifest Injection
**Current State:** The `manifest` object is still used as a global singleton that is configured at runtime.
**Technical Debt:** While `RuntimeContext` holds the manifest, several core modules still import and use the global `manifest` instance directly.
**Proposed Solution:** Inject the manifest instance into core functions (e.g., `download_video`, `clip_video`) to improve testability and reduce reliance on global state.

---

## 4. Subtitle Handling Logic (`subtitles.py`)

### Opportunity: Standardized Subtitle Processing
**Current State:** `burn_subtitles` re-encodes the video to hard-burn subtitles in a separate step.
**Proposed Solution:** Implement a "Soft-to-Hard" toggle that can be handled during the main clipping `ffmpeg` pass to avoid an extra re-encoding step if both clipping and burning are requested.

---

## Summary of Impact
| Target | Effort | Impact | Status |
|--------|--------|--------|--------|
| `scene_detector` Single-Pass | Medium | **High** | ✅ Done |
| `cli` DRY Initialization | Low | Medium | ✅ Done |
| `ffmpeg` Filtergraph Union | High | **High** | Proposed |
| `download` Explicit Path | Low | **High** | Proposed |
| Manifest Dependency Injection | Medium | Medium | Proposed |

---
**Analyst:** Jules (Senior Systems Architect)
**Date:** 2024-05-23 (Updated)
