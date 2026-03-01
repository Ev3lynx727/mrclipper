"""Config model validation tests."""

from pathlib import Path

from mrclipper.config_models import AspectConfig, MrClipperConfig, OutputConfig, deep_update


def test_deep_update():
    base = {"a": 1, "b": {"x": 10, "y": 20}}
    override = {"b": {"x": 99}, "c": 3}
    deep_update(base, override)
    assert base["a"] == 1
    assert base["b"]["x"] == 99
    assert base["b"]["y"] == 20
    assert base["c"] == 3


def test_default_model_creation():
    cfg = MrClipperConfig()
    assert cfg.output.format == "mp4"
    assert cfg.aspect.default == "auto"
    assert cfg.clips.default_duration == 30


def test_output_config_validation():
    # Valid defaults
    cfg = OutputConfig()
    assert cfg.crf == 23


def test_aspect_config_validation():
    cfg = AspectConfig()
    assert cfg.default in ["auto", "source", "16:9", "9:16", "1:1", "4:3"]


def test_config_load_with_job(tmp_path):
    job_config = tmp_path / "job.toml"
    job_config.write_text('[paths]\nworkdir = "/tmp/custom"')
    cfg = MrClipperConfig.load(job_path=job_config)
    assert cfg.paths.workdir == "/tmp/custom"


def test_config_load_global_override(tmp_path, monkeypatch):
    home = tmp_path
    config_dir = home / ".config" / "mrclipper"
    config_dir.mkdir(parents=True)
    global_cfg_path = config_dir / "config.toml"
    global_cfg_path.write_text("[output]\ncrf = 18")
    monkeypatch.setattr(Path, "home", lambda: home)
    cfg = MrClipperConfig.load()
    assert cfg.output.crf == 18


def test_config_invalid_crf():

    bad_cfg = {"output": {"crf": 100}}
    try:
        MrClipperConfig(**bad_cfg)
        assert False, "Should have raised ValidationError"
    except Exception as e:
        assert "crf" in str(e).lower()


def test_config_expand_user():
    # Test that paths get expanded
    cfg = MrClipperConfig()
    assert "~" not in cfg.paths.workdir
    assert cfg.paths.workdir.startswith("/tmp") or cfg.paths.workdir.startswith(str(Path.home()))
