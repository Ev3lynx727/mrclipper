# Mr. Clipper ✂️

**Advanced Video Clipper for OpenClaw**  
Version: 1.0.1 | Family: Mr. Zero Agents

---

## 📦 Installation

### 1. Install CLI Tool

```bash
pip install mrclipper
```

This installs the `mrclipper` command and all Python dependencies.

Verify:
```bash
mrclipper --version  # mrclipper 1.0.1
```

### 2. Install OpenClaw Skill

You have two options:

#### **Option A: Clone Repository (Recommended for developers)**

```bash
# Clone the mrclipper repository
git clone https://github.com/Ev3lynx727/mrclipper.git
cd mrclipper

# Create symlink to skill (keeps skill updated with repo)
ln -s $(pwd)/skills/video-clipper ~/.openclaw/workspace/skills/

# Or copy if you prefer:
# cp -r skills/video-clipper ~/.openclaw/workspace/skills/
```

Now the skill is available in OpenClaw. Use commands like:
```
/clip URL --start 00:01:00 --duration 30
/auto-highlight URL
```

#### **Option B: Download from GitHub Releases**

1. Go to [Releases](https://github.com/Ev3lynx727/mrclipper/releases)
2. Download `mrclipper-skill-v1.0.1.zip`
3. Extract to OpenClaw skills directory:

```bash
unzip mrclipper-skill-v1.0.1.zip -d ~/.openclaw/workspace/skills/
```

The skill files will appear at `~/.openclaw/workspace/skills/video-clipper/`.

#### **Option C: ClawHub (Future)**

```bash
clawhub install mrclipper
```

*(ClawHub integration will be available separately — contact developer for setup.)*

---

## 🚀 Quick Start

### Configure Global Settings

Create config at `~/.config/mrclipper/config.toml`:

```toml
[paths]
output = "~/Videos/MrClipper"

[highlights]
strategy = ["scene", "audio"]
num_clips = 5
clip_length = 30
```

See `mrclipper/config-examples/` for templates.

### Try a Test Clip

```bash
# Manual clip (TikTok style)
/clip https://youtube.com/watch?v=dQw4w9WgXcQ --start 00:00:15 --duration 60 --aspect 9:16

# Auto-highlights
/auto-highlight https://youtube.com/watch?v=xyz --output ~/Highlights/
```

---

## 📚 Documentation

Full documentation in `mrclipper/docs/`:

- `index.md` — Overview
- `usage.md` — User guide
- `configuration.md` — TOML reference
- `examples.md` — Real-world use cases
- `api.md` — CLI reference
- `agent-setup.md` — Sub-agent usage
- `cron.md` — Scheduling
- `troubleshooting.md` — Fix issues

Or view online at: [github.com/Ev3lynx727/mrclipper/docs](https://github.com/Ev3lynx727/mrclipper/tree/main/docs)

---

## 🏗️ Project Structure

```
mrclipper/                    # Repository root
├── mrclipper/                # Python package (import mrclipper)
│   ├── cli.py
│   ├── config_models.py
│   ├── download.py
│   ├── highlights.py
│   └── ...
├── tests/                    # 33 passing tests
├── docs/                     # Full documentation (Markdown)
├── config-examples/          # TOML config templates
├── skills/video-clipper/     # OpenClaw skill wrapper
│   ├── scripts/clip         # Wrapper calling `mrclipper`
│   ├── config/              # Example configs
│   └── SKILL.md
├── pyproject.toml
├── README.md
└── CHANGELOG.md
```

---

## 🧪 Development

```bash
# Clone repo
git clone https://github.com/Ev3lynx727/mrclipper.git
cd mrclipper

# Install in editable mode
pip install -e .

# Run tests
pytest tests/ -v

# Build wheel
python -m build
```

---

## 📦 Release Assets

Each GitHub Release includes:

- `mrclipper-1.0.1-py3-none-any.whl` — PyPI package (install with pip)
- `mrclipper-skill-v1.0.1.zip` — OpenClaw skill (extract to `~/.openclaw/workspace/skills/`)
- Source code (tarball/zip)

---

## 🤝 Contributing

This is a personal project for the Mr. Zero Agents family. For issues, feature requests, or questions:

- Open an issue on GitHub
- Contact: Mr. Zero ✂️

---

## 📄 License

MIT

---

*"Clip it with precision, family."* — Mr. Clipper ✂️