# Refactor Plan: video-clipper → mrclipper

**Started:** 2026-03-01  
**Status:** v1.0.1 Released — Mode B Complete  
**Goal:** Transform monolith `clip.py` into maintainable, testable, extensible Python package  
**Target:** Production-ready skill with modular architecture, typed config, intelligent highlights, CI/CD

---

## 📋 Master Checklist

- [x] **Phase 0: Preparation** — Safety net and tooling ✅
- [x] **Phase 1: Modular Extraction** — Split into package ✅
- [x] **Phase 2: Typed Config & Validation** — Pydantic models ✅
- [x] **Phase 3: CLI Polish** — Typer + subcommands ✅
- [x] **Phase 4: Highlights Intelligence** — Scene/audio detection ✅ (v1.0.1)
- [ ] **Phase 5: Robustness & Observability** — Partial ✅ (missing: retry)
- [x] **Phase 6: Testing & CI** — Full test suite + GitHub Actions ✅
- [x] **Phase 7: Packaging & Distribution** — Build + install ✅
- [x] **Phase 8: Documentation Refresh** — Update all docs ✅

**Overall:** v1.0.1 shipped with Mode B (intelligent highlights). Phase 5 retry logic optional.

---

## 🟡 Phase 0: Preparation (Baseline)

**Objective:** Establish safety net, modern tooling, and verified baseline.

### Tasks
- [ ] Create git snapshot (if not already tracked)
- [ ] Write smoke test harness:
  - [ ] fixture: small sample video (10s)
  - [ ] test_current_clip_basic() — verify basic clip works
  - [ ] test_current_auto_highlights() — verify auto mode runs
  - [ ] test_current_aspect_ratio() — verify aspect conversion
  - [ ] test_current_subtitles() — verify soft-subs handling
- [ ] Set up pre-commit config (`.pre-commit-config.yaml`):
  - [ ] black
  - [ ] ruff
  - [ ] mypy (basic, strict later)
- [ ] Create `pyproject.toml` with build system (hatchling/setuptools)
- [ ] Verify: `pre-commit run --all-files` passes on current code
- [ ] Document baseline: capture current CLI output for comparison

**Success Criteria:** Smoke tests pass; pre-commit installed; baseline behavior documented.

---

## 🟢 Phase 1: Modular Extraction (Biggest Push)

**Objective:** Split `clip.py` monolith into `src/mrclipper/` package without behavior change.

### Tasks
- [ ] **1.1 Create package skeleton**
  - [ ] `mkdir -p src/mrclipper`
  - [ ] `touch src/mrclipper/__init__.py`
  - [ ] Update `pyproject.toml` with `[tool.setuptools] package-dir = {"" = "src"}`

- [ ] **1.2 Extract Config (`config.py`)**
  - [ ] Move `DEFAULT_CONFIG` → `DEFAULT_CONFIG` constant
  - [ ] Move `load_config`, `deep_update` → functions
  - [ ] Keep global `~/.config/mrclipper/config.toml` loading identical
  - [ ] Add module docstring

- [ ] **1.3 Extract Video (`video.py`)**
  - [ ] Move `get_video_dimensions`, `get_video_duration`, `get_aspect_ratio`
  - [ ] Return typed tuples (width, height) or dataclass
  - [ ] Add GCD helper function

- [ ] **1.4 Extract Download (`download.py`)**
  - [ ] Move `download_video`, `find_subtitle_file`
  - [ ] Ensure workdir handling stays same

- [ ] **1.5 Extract Subtitles (`subtitles.py`)**
  - [ ] Move `burn_subtitles`
  - [ ] Document soft-subs as "no operation" in this module

- [ ] **1.6 Extract Aspect (`aspect.py`)**
  - [ ] Move `process_aspect_ratio`

- [ ] **1.7 Extract Highlights (`highlights.py`)**
  - [ ] Move `detect_highlights` (keep naive even-spacing for now)
  - [ ] Add docstring noting it's a placeholder

- [ ] **1.8 Extract Utils (`utils.py`)**
  - [ ] Move `log`, `run_cmd`, `ensure_deps`
  - [ ] Replace `die()` with custom exceptions: raise `ClipperError` or subclass
  - [ ] Add `temp_workdir()` context manager stub (will implement in Phase 5)

- [ ] **1.9 Create CLI Wrapper (`cli.py`)**
  - [ ] Use `argparse` initially (simple, no extra dep)
  - [ ] Recreate exact CLI interface: `clip.py [url] --start --duration --output --config --aspect --burn-subs --auto`
  - [ ] Orchestrate: load config → download → process → clip/highlights
  - [ ] Preserve output messages (`[Mr.Clipper v2]` prefix)
  - [ ] Entry point: `mrclipper = mrclipper.cli:main` in `pyproject.toml`

- [ ] **1.10 Install & Verify**
  - [ ] `pip install -e .`
  - [ ] `mrclipper --help` works
  - [ ] Run **all smoke tests** against new package
  - [ ] Manual test: clip a short video
  - [ ] Compare output with baseline (should be identical)

**Success Criteria:** `mrclipper` CLI indistinguishable from old `clip.py` behavior. All smoke tests pass.

---

## 🔵 Phase 2: Typed Config & Validation

**Objective:** Replace loose dicts with Pydantic models for robustness and DX.

### Tasks
- [ ] Add `pydantic>=2.0` to dependencies in `pyproject.toml`
- [ ] Create `config_models.py`:
  - [ ] Define `OutputConfig`, `PathsConfig`, `SubtitlesConfig`, `AspectConfig`, `ClipsConfig`, `YtDlpConfig` as `BaseModel`
  - [ ] Root `MrClipperConfig` with `model_config = ConfigDict(extra='ignore')`
  - [ ] Implement `.load(global_path: Path, job_path: Optional[Path]) -> MrClipperConfig`
  - [ ] Add validation: `crf` range 18-28, `preset` choices, `aspect.default` enum
  - [ ] Add `@field_validator` for path expansion (`os.path.expanduser`)
- [ ] Update all modules to use typed config:
  - [ ] Replace `cfg["aspect"]["default"]` → `cfg.aspect.default`
  - [ ] Update imports
- [ ] Add CLI command: `mrclipper config validate [path]`
  - [ ] Loads TOML, validates against model, prints OK or errors
- [ ] Test config validation:
  - [ ] Invalid `crf` (e.g., 100) → error
  - [ ] Unknown key → warning (if `extra='forbid'`) or ignore

**Success Criteria:** Config errors produce clear messages; IDE autocomplete works.

---

## 🟣 Phase 3: CLI Polish with Typer

**Objective:** Upgrade from `argparse` to `typer` for modern UX.

### Tasks
- [ ] Add `typer>=0.9` to dependencies
- [ ] Refactor `cli.py` to use `typer.Typer()`:
  - [ ] `@app.command()` for `clip`
  - [ ] `@app.command()` for `auto-highlight`
  - [ ] `@app.command()` for `config validate`
  - [ ] `@app.command()` for `config show`
- [ ] Add global `--verbose` / `--quiet` flags:
  - [ ] Configure `logging` module (replace `log()` function)
  - [ ] Levels: DEBUG (verbose), INFO (normal), WARNING (quiet)
- [ ] Auto-generated `--help` with rich formatting:
  - [ ] Add examples from README to docstrings
- [ ] Proper exit codes:
  - [ ] `0` success
  - [ ] `1` user error (bad args)
  - [ ] `2` system error (ffmpeg missing, download failed)
- [ ] Test all subcommands: `mrclipper clip --help`, `mrclipper auto-highlight --help`

**Success Criteria:** `mrclipper --help` looks professional; users can discover features easily.

---

## 🟤 Phase 4: Highlights Intelligence Upgrade

**Objective:** Replace even-spacing heuristic with content-aware detection.

### Tasks
- [ ] **4.1 Scene Change Detection**
  - [ ] Research ffmpeg `scene` filter: `select='gt(scene,THRESH)'`
  - [ ] Implement `detect_scene_changes(video: Path, threshold: float = 0.4) -> List[float]` → list of timestamps
  - [ ] Cluster adjacent timestamps (within 1s) to avoid duplicates
  - [ ] Return representative scene start times

- [ ] **4.2 Audio Peak Detection**
  - [ ] Research ffmpeg `volumedetect` or `astats` filter
  - [ ] Implement `detect_audio_peaks(video: Path, min_peak_db: float = -20) -> List[float]`
  - [ ] Consider audio-only stream extraction: `ffmpeg -i input -af "volumedetect" -f null -`

- [ ] **4.3 Strategy Combiner**
  - [ ] Implement `select_highlights(scenes: List, peaks: List, num_clips: int, duration: int) -> List[ClipSpec]`
  - [ ] Weighted scoring: scene + audio = high confidence
  - [ ] Spread selected highlights evenly across video duration
  - [ ] Fallback to even spacing if both detectors fail

- [ ] **4.4 Configurable Strategy**
  - [ ] Add to config models:
    ```toml
    [highlights]
    strategy = ["scene", "audio"]  # order: first wins, fallback to next
    num_clips = 5
    clip_length = 30
    scene_threshold = 0.4
    audio_min_peak_db = -20.0
    ```
  - [ ] Allow disabling strategies: `strategy = ["even"]` (old behavior)

- [ ] **4.5 Update `highlights.py`**
  - [ ] Replace naive loop with new pipeline
  - [ ] Write metadata JSON for each highlight: `{ "timestamp": 12.34, "confidence": "high", "strategy": "scene+audio" }`
  - [ ] Unit test with synthetic data (mock detectors)

- [ ] **4.6 Documentation**
  - [ ] Update README/SKILL.md with new highlight capabilities
  - [ ] Add `--strategy` CLI flag override (optional)

- [ ] **4.7 (Optional) YouTube Most Replayed**
  - [ ] Investigate feasibility: scrape heatmap data from YouTube page or use third-party API
  - [ ] If feasible, add `strategy = ["most_replayed"]` and implement detector
  - [ ] Mark as experimental; fallback to scene/audio if unavailable

**Success Criteria:** Auto-highlights feel smarter; tests show scene/audio detection works on sample videos.

---

## 🟢 Phase 5: Robustness & Observability

**Objective:** Production-ready stability and debuggability.

### Tasks
- [x] **5.1 Temp Workdir Context Manager** ✅
  - [x] In `utils.py`: `@contextmanager def temp_workdir(base: Path) -> Iterator[Path]:`
  - [x] Creates unique temp dir, auto-cleans
- [x] **5.2 Retry Logic for Downloads** ✅ (implemented, needs tests)
  - [x] Custom `@retry` decorator in `utils.py` (tries=3, delay=2.0, backoff=2.0)
  - [x] Applied to `download_video()` in `download.py`
  - [x] Catches: `CalledProcessError`, `ConnectionError`, `TimeoutError`
  - [x] Logs warnings on retry attempts
  - [ ] **TODO:** Add unit tests for retry decorator (see Phase 6.1 enhancement)
- [x] **5.3 Structured Logging** ✅
  - [x] `logging.getLogger("mrclipper")` throughout
  - [x] `setup_logging()` in `logging_config.py`
  - [x] Respects `--verbose` (DEBUG) and `--quiet` (WARNING)
- [x] **5.4 Graceful Degradation** ✅
  - [x] `ffprobe` fallback to `ffmpeg -i` in `video.py`
  - [x] Subtitle download failures continue with warning
  - [x] Aspect conversion failures fallback to copy + warning
- [x] **5.5 Custom Exception Hierarchy** ✅
  - [x] `exceptions.py`: `MrClipperError`, `ConfigurationError`, `DownloadError`, `ProcessingError`
  - [x] `run_cmd` raises appropriate errors
- [x] **5.6 Better Error Messages** ✅
  - [x] ffmpeg errors include stderr in exception
  - [x] Clear user-facing messages in CLI (typer.echo with ❌ prefix)

**Note:** Phase 5 mostly complete. Retry logic needs unit tests to be fully verified.

---

## 🟡 Phase 6: Testing & CI

**Objective:** Comprehensive test suite and automated quality gates.

### Tasks
- [ ] **6.1 Unit Tests** (`tests/unit/`)
  - [ ] `test_config.py`: load/merge/validation edge cases
  - [ ] `test_video.py`: `get_aspect_ratio` GCD math for various resolutions
  - [ ] `test_aspect.py`: filter string generation for different ratios
  - [ ] `test_highlights.py`: strategy selection, scene clustering
  - [ ] `test_utils.py`: `deep_update`, `temp_workdir` cleanup

- [ ] **6.2 Integration Tests** (`tests/integration/`)
  - [ ] `test_clip_pipeline.py`:
    - [ ] Use small fixture video (e.g., `tests/fixtures/sample.mp4`)
    - [ ] End-to-end: download → clip → verify output duration
    - [ ] Mock `yt-dlp` to avoid network
    - [ ] Mock `ffmpeg` to avoid heavy processing (use `unittest.mock`)
  - [ ] `test_auto_highlights.py`: verify clip count, durations

- [ ] **6.3 CLI Tests** (`tests/cli/`)
  - [ ] `test_cli.py` using `typer.testing.CliRunner`:
    - [ ] `mrclipper --help` exits 0
    - [ ] `mrclipper config validate` exits 0 with good config
    - [ ] `mrclipper clip` with bad args exits 1

- [ ] **6.4 GitHub Actions** (`.github/workflows/ci.yml`)
  - [ ] Matrix: Python 3.10, 3.11, 3.12
  - [ ] Steps:
    - [ ] Checkout
    - [ ] Setup Python
    - [ ] Install `pip install -e .[dev]`
    - [ ] `pre-commit run --all-files`
    - [ ] `pytest --cov=mrclipper --cov-report=xml`
    - [ ] `mypy src/mrclipper`
  - [ ] Upload coverage to Codecov (optional)

- [ ] **6.5 Test Coverage**
  - [ ] Aim >80% coverage
  - [ ] Identify untested branches (especially error paths)

- [ ] **6.6 Fixtures Management**
  - [ ] Add small sample video (Creative Commons, <5MB) to `tests/fixtures/`
  - [ ] `.gitignore` for large files; provide script to download

**Success Criteria:** CI passes on all matrix; coverage report; tests catch regressions.

---

## 🔴 Phase 7: Packaging & Distribution

**Objective:** Build and installable as OpenClaw skill.

### Tasks
- [ ] **7.1 Complete `pyproject.toml`**
  - [ ] `[project]`:
    - `name = "mrclipper"`
    - `version = "1.0.1"` (bump from v1.0.0)
    - `description = "Advanced video clipper for OpenClaw"`
    - `authors = [{name = "Mr. Clipper", email = "..."}]`
    - `dependencies = ["toml", "pydantic>=2.0", "typer>=0.9"]`
    - `requires-python = ">=3.10"`
  - [ ] `[build-system]`: `requires = ["hatchling"]`, `build-backend = "hatchling.build"`
  - [ ] `[project.scripts]`: `mrclipper = "mrclipper.cli:app"` (if typer) or `main` (if argparse)
  - [ ] `[tool.black]`, `[tool.ruff]`, `[tool.mypy]`

- [ ] **7.2 Build & Test Install**
  - [ ] `python -m pip install --upgrade build`
  - [ ] `python -m build`
  - [ ] `pip install dist/mrclipper-1.0.1-py3-none-any.whl`
  - [ ] `mrclipper --version` → prints `1.0.1`
  - [ ] All CLI commands work

- [ ] **7.3 Install as OpenClaw Skill**
  - [ ] Option A (editable dev): `pip install -e .` (already done)
  - [ ] Option B (global skill):
    ```bash
    cp -r src/mrclipper /home/ev3lynx/.nvm/versions/node/v24.12.0/lib/node_modules/openclaw/skills/video-clipper/
    ```
    (overwrite old skill)
  - [ ] Option C (PyPI): publish (not necessary for personal use)

- [ ] **7.4 Backward Compatibility Check**
  - [ ] Keep `skills/video-clipper/scripts/clip.py` as wrapper that calls `mrclipper` (temporary)
  - [ ] Or document migration: `mrclipper` replaces `clip.py`
  - [ ] Update OpenClaw skill integration if needed (Spawn command: `mrclipper` instead of `clip.py`)

**Success Criteria:** Package builds; `mrclipper` command available; old scripts still work via wrapper.

---

## 🟣 Phase 8: Documentation Refresh

**Objective:** All docs accurate, comprehensive, and maintainable.

### Tasks
- [ ] **8.1 Update `SKILL.md`**
  - [ ] New package structure diagram
  - [ ] Configuration examples (Pydantic-validated)
  - [ ] Highlight strategies explained
  - [ ] Troubleshooting section (common errors + fixes)
  - [ ] Development guide: "Contributing to mrclipper"

- [ ] **8.2 Update `README.md`**
  - [ ] Quick reference remains concise
  - [ ] Link to `SKILL.md` for deep dives
  - [ ] Add badge: build, coverage, version
  - [ ] Update installation instructions (pip install vs manual copy)
  - [ ] Update usage examples to new CLI if changed

- [ ] **8.3 Update `IMPLEMENTATION.md` → `ARCHITECTURE.md`**
  - [ ] Document new module layout
  - [ ] Explain config flow
  - [ ] Describe highlight detection algorithms
  - [ ] Include sequence diagrams (optional)

- [ ] **8.4 Add `CHANGELOG.md`**
  - [ ] Follow Keep a Changelog format
  - [ ] Entry for `1.0.1`: Modularization, typed config, typer CLI, intelligent highlights (Mode B)
  - [ ] Credit ghostclaw review as catalyst (if applicable)

- [ ] **8.5 Update `USER.md` and `TOOLS.md`** (workspace docs)
  - [ ] Note: `mrclipper` command available
  - [ ] Any environment variables? (`MRCLIPPER_CONFIG` override?)

- [ ] **8.6 Inline Code Documentation**
  - [ ] Ensure all public functions/classes have docstrings (Google or NumPy style)
  - [ ] Add type hints to all function signatures
  - [ ] Run `pydocstyle` in pre-commit

**Success Criteria:** New contributor can understand codebase from docs alone.

---

## 📊 Progress Tracking

### Milestones

| Milestone | Target Date | Dependencies | Done |
|-----------|-------------|--------------|------|
| M1: Baseline established | Day 2 | Phase 0 | [x] |
| M2: Modular package | Day 7 | Phase 1 | [x] |
| M3: Typed config + Typer CLI | Day 10 | Phase 2, 3 | [x] |
| M4: Intelligent highlights (Mode B) | Day 17 | Phase 4 | [x] ✅ v1.0.1 |
| M5: Robustness hardening | Day 20 | Phase 5 | [~] Partial (retry optional) |
| M6: CI/CD + tests | Day 24 | Phase 6 | [x] |
| M7: Package ready | Day 26 | Phase 7 | [x] |
| M8: Docs complete | Day 27 | Phase 8 | [x] |

### Current Phase: Complete (v1.0.1 Released)

**Released:** 2026-03-02 GMT+7  
**Status:** Production-ready with Mode B intelligent highlights

---

## 🧠 Notes & Decisions

- **Backward compatibility:** Maintained through Phase 3. Wrapper script may keep old `clip.py` name alive temporarily.
- **Highlight strategy default:** `["scene", "audio"]` with fallback to even spacing. Conservative.
- **Dependencies:** Will add `pydantic`, `typer`. Keep `toml` (stdlib in 3.11? Use `tomllib` if py3.11+, else keep `toml` package). Decision: support 3.10+ → keep `toml` package for now.
- **Testing fixtures:** Need small sample video. Option: download ~10s from YouTube using `yt-dlp` in test setup, or commit a tiny video (ensure license OK).
- **OpenClaw integration:** Skill will live at `skills/video-clipper/`. After packaging, we can replace the skill content with the built package.

---

**Last updated:** 2026-03-01 06:12 GMT+7  
**Next review:** After Phase 0 completion

---

**Last updated:** 2026-03-02 04:40 GMT+7  
**Next review:** N/A — All phases complete, v1.0.1 released

---

## ✅ Final Status: v1.0.1 Released — Mode B Complete!

**Release Date:** 2026-03-02 GMT+7  
**Version:** mrclipper 1.0.1  
**Status:** Production-ready ✅

### All Phases Completed

| Phase | Feature | Tests | Docs | Status |
|-------|---------|-------|------|--------|
| 0 | Baseline | ✅ | ✅ | Done |
| 1 | Modular package | ✅ | ✅ | Done |
| 2 | Typed config (Pydantic) | ✅ | ✅ | Done |
| 3 | Typer CLI | ✅ | ✅ | Done |
| 4 | **Mode B Intelligence** | ✅ | ✅ | Done (v1.0.1) |
| 5 | Robustness | ✅ | ✅ | Done (retry tested) |
| 6 | CI/CD + Tests | ✅ | ✅ | Done (30 tests passing) |
| 7 | Packaging | ✅ | ✅ | Done (1.0.1) |
| 8 | Docs refresh | ✅ | ✅ | Done |

### What Was Built (v1.0.1)

- ✅ **Scene change detection** (ffmpeg `scene` filter)
- ✅ **Audio peak detection** (ffmpeg `astats` filter)
- ✅ **Configurable strategies**: `["scene"]`, `["audio"]`, `["scene+audio"]`, `["even"]`
- ✅ **Clustering + spread enforcement** for smart clip selection
- ✅ **Retry logic** (3 attempts, exponential backoff) — fully tested
- ✅ **Custom exceptions** (`DownloadError`, `ProcessingError`, etc.)
- ✅ **Structured logging** (DEBUG/INFO/WARNING levels)
- ✅ **Pydantic v2 config validation**
- ✅ **Typer CLI** with `--verbose/--quiet` and proper exit codes
- ✅ **10 new unit tests** for retry decorator (all passing)
- ✅ **30 total tests** passing (unit + integration)
- ✅ **GitHub Actions CI** (Black, Ruff, Mypy, Pytest, Coverage)
- ✅ **Documentation** updated: SKILL.md, CHANGELOG.md, SETUP_COMPLETE.md, config examples

### Verification

```bash
$ mrclipper --version
mrclipper 1.0.1

$ /usr/bin/python3.10 -m pytest tests/ -v
30 passed in 2.73s

$ pre-commit run --all-files
All checks passed ✅
```

### Files Added/Modified (v1.0.1)

- **tests/unit/test_retry.py** — New comprehensive retry tests (10 test cases)
- **CHANGELOG.md** — Rewritten with proper v1.0.1 and v1.0.0 entries
- **SETUP_COMPLETE.md** — Updated to v1.0.1, highlights Mode B
- **SKILL.md** — Version 1.0.1, added `[highlights]` config section
- **docs/configuration.md** — Added `[highlights]` options table
- **skills/video-clipper/config/*.toml.example** — All include Mode B settings
- **TODO.md** — Updated with completion notes
- **src/mrclipper/__init__.py** — `__version__ = "1.0.1"`
- **pyproject.toml** — Version bump to 1.0.1
- **tests/test_cli_basic.py** — Updated expected version string

---

**Phase 5.2 officially complete:** Retry logic implemented, tested, and verified.  
**Mr. Clipper v1.0.1 is production-ready with Mode B intelligence.** 🎉🚀

*"Clip it with precision, family."* — Mr. Clipper ✂️

---

## 📦 v1.0.1 Feature Addendum (2026-03-02)

### Metadata Embedding for mrpublisher (Completed)

**New files:**
- `src/mrclipper/metadata.py` — Caption/tag generation + sidecar writer

**Modified:**
- `src/mrclipper/clip.py` — Pass cfg, source_url, caption, tags; write metadata
- `src/mrclipper/highlights.py` — Pass publisher config; write metadata per highlight
- `src/mrclipper/config_models.py` — Added `PublisherConfig`
- `skills/video-clipper/config/*.toml.example` — Added `[publisher]` sections
- `skills/video-clipper/docs/configuration.md` — Documented `[publisher]`
- `SKILL.md` — Added metadata section, search/manifest logging
- `SETUP_COMPLETE.md` — v1.0.1 enhancements
- `tests/unit/test_metadata.py` — New: 3 tests for metadata generation

**Features:**
- ✅ Sidecar `.metadata.json` for every clip
- ✅ Caption template with placeholders (`{title}`, `{start}`, `{duration}`, `{url}`)
- ✅ Auto tag generation from video title
- ✅ Default tags from config
- ✅ CLI overrides (`--caption`, `--tags`)
- ✅ Works for both `clip` and `auto-highlight`

**Total tests:** 33 passing

---

**v1.0.1 is now feature-complete with full observability and mrpublisher integration.**
