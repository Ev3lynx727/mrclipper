# 🚀 Mr. Clipper — Implementation: Next & Future

**Current Version:** v1.0.0 (Production-Ready)  
**Target Horizon:** v2.x (Mode B + Intelligent Workflows)  
**Status:** v1.0.0 complete — future planning in progress  
**Last Updated:** 2026-03-02 GMT+7

---

## 📌 Executive Summary

Mr. Clipper v1.0.0 is **live and operational** with:
- Soft subtitle extraction
- Aspect ratio control (auto + forcing)
- TOML configuration system
- Full OpenClaw integration (agent, cron, spawn)
- Comprehensive documentation

**Next frontier:** Transform from **even-spacing heuristics** to **content-aware intelligent highlights** (codenamed "Mode B"), plus architectural polish for maintainability and extensibility.

---

## 🎯 What We Have (v1.0.0)

### Core Features
| Feature | Implementation | Status |
|---------|----------------|--------|
| Video download | `yt-dlp` wrapper | ✅ Stable |
| Clipping | `ffmpeg` stream copy + re-encode | ✅ Stable |
| Auto-highlights | Even spacing heuristic | ✅ Works, basic |
| Subtitles | Soft (`--write-subs`) + burn option | ✅ Stable |
| Aspect ratio | Auto-detect + force (9:16, 16:9, 1:1, 4:3) | ✅ Stable |
| Configuration | Global + per-job TOML | ✅ Stable |
| OpenClaw agent | Registered `mrclipper` | ✅ Live |
| Cron support | OpenClaw `cron/jobs.json` | ✅ Working |
| Documentation | 9-guide suite in `docs/` | ✅ Complete |

### Known Limitations (v1.0.0)
1. **Highlights are dumb** — evenly spaced, no content awareness
2. **Monolithic code** — single `clip.py` (12.7 KB), hard to test/maintain
3. **No typed config** — loose dicts, no validation
4. **Basic CLI** — `argparse`, limited UX
5. **No structured logging** — `print()` statements
6. **No retry logic** — network failures fail immediately
7. **No exception hierarchy** — generic errors
8. **No test coverage** — manual testing only
9. **No CI/CD** — no automated quality gates
10. **No metadata reports** — no insight into why clips were chosen

---

## 🔮 Vision: Mode B — Intelligent Highlights

### The Jump: Heuristic → AI-Enhanced Detection

**Mode A (current):**
```
Video: 60 minutes → evenly split → 5 clips @ 12min intervals
```

**Mode B (target):**
```
Video: 60 minutes
↓ Scene change detection (visual transitions)
↓ Audio peak detection (loudest moments)
↓ Motion analysis (optional: optical flow)
↓ Engagement scoring (weighted combination)
↓ Spread enforcement (avoid clustering)
↓ 5 clips @ most interesting moments, distributed across video
```

### Why Mode B Matters
- **Better UX:** Clips feel "smart" — captures intros, punchlines, action peaks
- **Platform optimization:** TikTok/Reels thrive on high-engagement moments
- **Time savings:** No manual scrubbing to find highlights
- **Differentiator:** Sets Mr. Clipper apart from basic clipping tools

---

## 🗺️ Roadmap: Phases 0–8 (from TODO.md)

The existing `TODO.md` outlines a **comprehensive refactor** that includes Mode B as Phase 4. Here's the integrated plan:

### Phase 0: Preparation (Baseline)
**Goal:** Safety net before major changes.

**Tasks:**
- [ ] Git snapshot (tag `v1.0.0`)
- [ ] Smoke test harness with fixture video
- [ ] Pre-commit hooks (black, ruff, mypy)
- [ ] Verify baseline behavior

**Success:** All smoke tests pass against current `clip.py`

---

### Phase 1: Modular Extraction
**Goal:** Split monolith into testable package without behavior change.

**Structure:**
```
src/mrclipper/
├── __init__.py
├── config.py          # load_config, deep_update
├── video.py           # get_video_dimensions, duration, aspect
├── download.py        # download_video, find_subtitle_file
├── subtitles.py       # burn_subtitles
├── aspect.py          # process_aspect_ratio
├── highlights.py      # detect_highlights (current + new)
├── utils.py           # log, run_cmd, ensure_deps
└── cli.py             # Typer CLI entrypoint
```

**Process:**
1. Copy existing functions from `clip.py` into appropriate modules
2. Preserve exact behavior (no logic changes)
3. Install package: `pip install -e .`
4. Verify: `mrclipper --help` works, smoke tests pass

**Success:** `mrclipper` CLI indistinguishable from old `clip.py`

---

### Phase 2: Typed Config & Validation
**Goal:** Replace loose dicts with Pydantic v2 models.

**Add:** `pydantic>=2.0` to dependencies

**New file:** `config_models.py` (already exists from recent work!)
```python
class MrClipperConfig(BaseModel):
    output: OutputConfig
    paths: PathsConfig
    subtitles: SubtitlesConfig
    aspect: AspectConfig
    clips: ClipsConfig
    yt_dlp: YtDlpConfig
    highlights: HighlightsConfig  # ← new fields for Mode B
```

**Enhance `HighlightsConfig`:**
```python
class HighlightsConfig(BaseModel):
    strategy: List[str] = Field(
        default_factory=lambda: ["scene+audio", "scene", "audio", "even"]
    )
    num_clips: int = Field(5, gt=0)
    clip_length: int = Field(30, gt=0)
    scene_threshold: float = Field(0.4, ge=0.0, le=1.0)
    audio_min_peak_db: float = Field(-20.0)
    audio_min_peak_separation: float = Field(5.0)  # seconds
```

**CLI command:** `mrclipper config validate ~/.config/mrclipper/config.toml`

**Success:** Config errors produce clear messages; IDE autocomplete works.

---

### Phase 3: CLI Polish with Typer
**Goal:** Modern UX with subcommands and auto-help.

**Replace:** `argparse` with `typer.Typer()`

**Commands:**
```bash
mrclipper clip URL --start --duration --aspect --burn-subs
mrclipper auto-highlight URL --output --config --strategy
mrclipper config validate PATH
mrclipper config show
```

**Features:**
- Global `--verbose` / `--quiet` flags
- Structured logging (`logging` module)
- Proper exit codes (0 success, 1 user error, 2 system error)
- Rich help text with examples

**Success:** `mrclipper --help` looks professional; subcommands discoverable.

---

### Phase 4: Highlights Intelligence (Mode B) ⭐
**Goal:** Content-aware clip selection.

#### 4.1 Scene Change Detection
```python
# src/mrclipper/highlights/detectors.py

def detect_scene_changes(video: Path, threshold: float = 0.4) -> List[float]:
    """
    FFmpeg: -vf "select='gt(scene,THRESH)',metadata=print"
    Parse stderr for scene timestamps.
    Returns: sorted list of scene change times (seconds)
    """
```

#### 4.2 Audio Peak Detection
```python
def detect_audio_peaks(video: Path, min_db: float = -20.0) -> List[float]:
    """
    FFmpeg: -af "astats=metadata=1:reset=1"
    Parse metadata for frames where max_sample > threshold.
    Returns: sorted list of peak times (seconds)
    """
```

#### 4.3 Scoring & Selection
```python
# src/mrclipper/highlights/scorer.py

def select_highlights(
    duration: float,
    scene_times: List[float],
    audio_times: List[float],
    cfg: HighlightsConfig
) -> List[ClipSpec]:
    """
    1. Cluster nearby timestamps (±2s) → candidate starts
    2. Score each candidate:
       - Near scene? +0.5
       - Near audio peak? +0.5
       - Bonus if both (max 1.0)
    3. Greedy select top candidates, avoiding overlap
    4. Enforce spread: if all clips in first 10% of video, reject and retry
    5. Fallback to even spacing if < desired count
    """
```

#### 4.4 Strategy Engine
```python
STRATEGIES = {
    "scene+audio": lambda: combined_detection(scene, audio),
    "scene": lambda: detection_only(scene),
    "audio": lambda: detection_only(audio),
    "even": lambda: even_spacing(duration, cfg.num_clips, cfg.clip_length),
}
```

**Config-driven selection order:**
```toml
[highlights]
strategy = ["scene+audio", "even"]  # try scene+audio first, fallback to even
```

#### 4.5 Metadata Report
```json
{
  "video": "input.mp4",
  "duration": 3627.5,
  "strategy": "scene+audio",
  "detectors": {
    "scene": {"threshold": 0.4, "detected": 342, "clustered": 28},
    "audio": {"min_db": -20, "detected": 156, "clustered": 22}
  },
  "clips": [
    {
      "index": 0,
      "start": 45.2,
      "duration": 30.0,
      "confidence": 0.87,
      "reasons": ["scene_change", "audio_peak"],
      "output": "clip_001.mp4"
    }
  ]
}
```

**Deliverables:**
- [ ] `detectors.py` with scene + audio functions
- [ ] `scorer.py` with clustering + selection logic
- [ ] `strategies.py` strategy registry
- [ ] `metadata.py` report generation
- [ ] Unit tests for each component (mock FFmpeg output)
- [ ] Integration test with real short video
- [ ] Update `highlights.py` to use new engine
- [ ] Update `config_models.py` with new fields
- [ ] Update CLI `auto-highlight` to pass config

**Success:** 10 YouTube videos tested — Mode B clips feel noticeably smarter than even spacing.

---

### Phase 5: Robustness & Observability
**Goal:** Production-ready stability.

#### 5.1 Temp Workdir Context Manager
```python
@contextmanager
def temp_workdir(base: Path) -> Iterator[Path]:
    workdir = base / f"run_{uuid4().hex[:8]}"
    workdir.mkdir(parents=True)
    try:
        yield workdir
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
```

#### 5.2 Retry Logic (Network)
```python
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(wait=wait_exponential(min=1, max=10), stop=stop_after_attempt(3))
def download_video(url: str, output: Path) -> Path:
    # yt-dlp call
    ...
```

#### 5.3 Structured Logging
```python
import logging

logger = logging.getLogger("mrclipper")

def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        format="[%(levelname)s] %(message)s",
        level=level
    )
```

#### 5.4 Custom Exceptions
```python
class MrClipperError(RuntimeError): ...
class ConfigurationError(MrClipperError): ...
class DownloadError(MrClipperError): ...
class ProcessingError(MrClipperError): ...
```

#### 5.5 Graceful Degradation
- If `ffprobe` missing → fallback to `ffmpeg -i` parsing
- If subtitle download fails → continue with warning (config: `subtitles.ignore_errors=true`)
- If aspect conversion fails → copy original + log warning

**Success:** All edge cases handled; logs provide actionable info; no crashes on missing deps.

---

### Phase 6: Testing & CI/CD
**Goal:** Automated quality gates.

#### 6.1 Unit Tests
```python
tests/unit/
├── test_config.py          # load/merge/validation
├── test_video.py           # aspect math, duration parsing
├── test_aspect.py          # filter generation
├── test_highlights/
│   ├── test_detectors.py   # mock FFmpeg output
│   ├── test_scorer.py      # clustering, selection logic
│   └── test_strategies.py  # strategy fallback
└── test_utils.py           # temp_workdir cleanup, run_cmd
```

#### 6.2 Integration Tests
```python
tests/integration/
├── test_clip_pipeline.py   # end-to-end with fixture video
└── test_auto_highlights.py # verify clip count, durations
```

**Fixture:** Small sample video (Creative Commons, ~5 MB) in `tests/fixtures/`

#### 6.3 CLI Tests
```python
tests/cli/
└── test_cli.py  # using typer.testing.CliRunner
```

#### 6.4 GitHub Actions
`.github/workflows/ci.yml`:
```yaml
jobs:
  test:
    strategy:
      matrix:
        python: ["3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - name: Install
        run: pip install -e .[dev]
      - name: Lint
        run: pre-commit run --all-files
      - name: Type check
        run: mypy src/mrclipper
      - name: Test
        run: pytest --cov=mrclipper --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v4
```

**Success:** CI passes on all Python versions; coverage ≥80%.

---

### Phase 7: Packaging & Distribution
**Goal:** Installable as OpenClaw skill with proper versioning.

#### 7.1 `pyproject.toml` (already exists)
Bump version to `2.1.0` (or `2.0.0` if breaking changes).

#### 7.2 Build Artifacts
```bash
python -m build
# Creates:
# dist/mrclipper-2.1.0-py3-none-any.whl
# dist/mrclipper-2.1.0.tar.gz
```

#### 7.3 Install into OpenClaw Skill Directory
```bash
# Option A: Editable dev
pip install -e .

# Option B: Copy wheel to skill folder
cp dist/*.whl ~/.nvm/versions/node/v24.12.0/lib/node_modules/openclaw/skills/video-clipper/

# Option C: OpenClaw skill manager (if available)
openclaw skills install dist/mrclipper-2.1.0-py3-none-any.whl
```

#### 7.4 Backward Compatibility
- Keep `skills/video-clipper/scripts/clip.py` as wrapper that calls `mrclipper`
- Or document migration: `mrclipper` replaces `clip.py`

**Success:** `mrclipper` command available globally; old scripts still work via wrapper.

---

### Phase 8: Documentation Refresh
**Goal:** Keep docs accurate and comprehensive.

#### 8.1 Update `SKILL.md`
- New architecture diagram (package layout)
- Mode B strategy explained
- Config options reference (with examples)
- Troubleshooting section

#### 8.2 Update `README.md`
- Quick reference remains concise
- Link to `SKILL.md` for deep dives
- Add badges (build, coverage, version)

#### 8.3 Update `ARCHITECTURE.md` (rename from `IMPLEMENTATION.md`)
- Document modular structure
- Explain config flow
- Describe highlight detection algorithms
- Include sequence diagrams

#### 8.4 Add `CHANGELOG.md`
Follow **Keep a Changelog** format:
```
## [2.1.0] - 2026-03-02
### Added
- Intelligent highlights (Mode B): scene + audio detection
- Typed config with Pydantic v2
- Typer CLI with subcommands
- Structured logging and custom exceptions
- Retry logic for downloads
- Comprehensive test suite
```

#### 8.5 Inline Code Docs
- All public functions/classes have docstrings
- Type hints on all signatures
- Run `pydocstyle` in pre-commit

**Success:** New contributor can understand entire codebase from docs alone.

---

## 📊 Milestones & Timeline

| Milestone | Target | Dependencies |
|-----------|--------|--------------|
| M1: Phase 0 baseline | Day +2 | None |
| M2: Phase 1 package | Day +7 | M1 |
| M3: Phase 2-3 (config + CLI) | Day +10 | M2 |
| M4: Phase 4 Mode B core | Day +17 | M3 |
| M5: Phase 5 robustness | Day +20 | M4 |
| M6: Phase 6 tests + CI | Day +24 | M5 |
| M7: Phase 7 packaging | Day +26 | M6 |
| M8: Phase 8 docs | Day +27 | M7 |

**Total estimated:** ~4 weeks from kickoff (assuming part-time effort)

---

## 🛠️ Technical Decisions & Rationale

| Decision | Options Chosen | Why |
|----------|---------------|-----|
| **FFmpeg filters** | `scene`, `astats` | Native, no extra deps, proven |
| **Clustering tolerance** | 2 seconds | Balances precision & recall |
| **Confidence model** | Binary signals (scene/audio) | Simple, interpretable |
| **Spread enforcement** | Post-selection check + retry | Avoids over-constraining scorer |
| **Fallback order** | Configurable strategy list | Flexible per-user preferences |
| **Metadata format** | JSON | Machine-readable, extensible |
| **Retry library** | `tenacity` | Battle-tested, exponential backoff |
| **Testing doubles** | `unittest.mock` for FFmpeg | No need for actual video processing in unit tests |
| **Config validation** | Pydantic v2 | Type-safe, clear errors, great DX |
| **CLI framework** | Typer | Auto-help, subcommands, built on Click |

---

## 🔬 Open Questions & Research

### Q1: Scene Detection Threshold Calibration
**Problem:** Optimal `scene` threshold varies by video (action movies vs lectures).  
**Options:**
- Per-video auto-calibration (analyze histogram of scene scores, pick elbow)
- User-configurable global default + per-job override
- Adaptive: start with 0.4, if < 5 scenes detected, lower to 0.3, retry

**Recommended:** Start with configurable (0.0–1.0), provide presets:
```toml
[highlights]
scene_sensitivity = "medium"  # low/medium/high → maps to 0.3/0.4/0.5
```

### Q2: Additional Signals?
**Beyond scene + audio:**
- **Optical flow** (motion intensity) → `ffmpeg` `metadata` filter on `mv` stats
- **Face detection** (talking heads) → `opencv` Haar cascades (adds heavy dep)
- **YouTube Most Replayed** → scrape heatmap from page (fragile, requires HTML parsing)

**Recommended:** Phase 4.1 = scene+audio only. Evaluate demand for Phase 4.2 (opt-in advanced signals).

### Q3: Clip Length Strategies
**Current:** Fixed `clip_length` for all clips.  
**Alternative:**
- Variable length based on scene duration (cut to next scene)
- User flag: `--adaptive-length` (clip extends to next scene change, up to max)

**Recommended:** Keep fixed for v2.0; consider adaptive as v2.1 if users request.

### Q4: GPU Acceleration
**Problem:** Mode B adds FFmpeg passes → slower on large videos.  
**Options:**
- No GPU needed for metadata extraction (fast enough on CPU)
- But processing many videos in parallel could benefit from GPU encoding
- OpenClaw sandbox could expose GPU device

**Recommended:** Document that Mode B metadata extraction is CPU-bound but fast (~1–2× realtime). Encoding still benefits from GPU if available (use `ffmpeg -hwaccel` if configured).

---

## 🧪 Testing Strategy

### Unit Tests (Fast, Isolated)
- Mock FFmpeg output (pre-captured stderr strings)
- Test detector parsers with known inputs
- Test scorer logic with synthetic timestamps
- Test config validation with TOML edge cases

### Integration Tests (Real Processing)
- Small fixture video (5–10 s, with clear scene changes and audio peaks)
- End-to-end: `mrclipper auto-highlight fixture.mp4`
- Assertions:
  - Number of clips = `config.highlights.num_clips`
  - Each clip duration = `config.highlights.clip_length` (±0.1s)
  - Clips exist on disk
  - Metadata JSON matches expected structure
  - No clips overlap

### Performance Benchmarks
```python
# tests/performance/bench_highlights.py
def test_scene_detection_time(benchmark):
    video = Path("tests/fixtures/sample_720p_60s.mp4")
    result = benchmark(detect_scene_changes, video, threshold=0.4)
    assert result.execution_time < 120  # seconds (1× realtime max)
```

---

## 📦 Deployment & Release Plan

### Versioning
- **v1.0.0** → Current stable (Mode A)
- **v2.0.0** → Modular architecture + PyPI package (no Mode B yet)
- **v2.1.0** → Mode B intelligence (Phases 0–6 complete)
- **v2.2.0** → Optional: GPU support, adaptive length
- **v3.0.0** → Major: Web UI, distributed workers

### Release Channels
1. **Development:** `pip install -e .` from GitHub main
2. **Beta:** Pre-release wheels on GitHub Releases
3. **Stable:** PyPI publish `mrclipper`
4. **OpenClaw skill:** Bundled in `openclaw/skills/video-clipper/` (auto-update via `openclaw skills update`)

### Migration Guide (v1 → v2)
- Old: `python skills/video-clipper/scripts/clip.py ARGS`
- New: `mrclipper ARGS` (installed globally)
- Config unchanged (TOML same format)
- Agent behavior identical for `clip` command
- `auto-highlight` gains `--strategy` flag (backward compatible: defaults to even spacing if config missing)

---

## 📚 Documentation Updates Needed

| File | Changes |
|------|---------|
| `SKILL.md` | Add Mode B section, strategy examples, sandbox notes |
| `README.md` | Updated version, badges, quick Mode B example |
| `ARCHITECTURE.md` | New: module diagram, data flow for Mode B |
| `CONFIGURATION.md` | New `highlights.*` options, strategy syntax |
| `USAGE.md` | New `--strategy` flag, metadata report explanation |
| `EXAMPLES.md` | Add Mode B examples (TikTok viral, podcast highlights) |
| `TROUBLESHOOTING.md` | Scene detection issues, threshold tuning |
| `CHANGELOG.md` | New, maintain per release |

---

## 🎯 Success Metrics

### Quantitative
- [ ] CI green on 3 Python versions (3.10, 3.11, 3.12)
- [ ] Test coverage ≥80%
- [ ] Mode B clip selection time < 1.5× video duration (CPU)
- [ ] 0 critical bugs in first 30 days post-release

### Qualitative
- [ ] User feedback: "Mode B clips feel smarter than random"
- [ ] No manual scrubbing needed to find highlights (subjective)
- [ ] Docs clear enough for new contributor to submit PR

---

## 🚀 Quick Start (Once Implemented)

```bash
# Install v2.1.0
pip install mrclipper

# Mode B: scene+audio highlights (TikTok style)
mrclipper auto-highlight URL \
  --strategy scene+audio \
  --clip-length 30 \
  --num-clips 8 \
  --output ~/Videos/Highlights/

# View metadata
cat ~/Videos/Highlights/report.json | jq '.clips[] | {start, confidence, reasons}'

# Use via OpenClaw agent
/sessions_spawn mrclipper "auto-highlight URL --strategy audio"
```

---

## 📝 Appendix: Glossary

- **Mode A**: Even-spacing highlight heuristic (v1.0.0)
- **Mode B**: Content-aware detection with scene + audio signals (v2.1.0 target)
- **Scene change**: Visual transition detected by FFmpeg `scene` filter
- **Audio peak**: Volume spike detected by FFmpeg `astats` filter
- **Clustering**: Grouping timestamps within tolerance (e.g., ±2s)
- **Spread enforcement**: Ensuring clips aren't all clustered in one video region
- **Strategy**: Ordered list of detection methods with fallback
- **Confidence**: Combined score (0.0–1.0) from available signals

---

**Ready to build the future?** Let's start with Phase 0 and get that safety net in place. The roadmap is clear, the architecture is sound, and the impact will be huge. 🚀

*"Intelligence in every clip."* — Mr. Clipper ✂️
