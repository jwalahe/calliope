"""Tests for configuration management."""

from __future__ import annotations

from calliope.config import DEFAULT_CONFIG, load_config, save_config


def test_load_default_config(project_paths) -> None:
    config = load_config(project_paths)
    assert config["project"]["name"] == DEFAULT_CONFIG["project"]["name"]


def test_save_config(project_paths) -> None:
    config = load_config(project_paths)
    config["project"]["name"] = "Test Novel"
    save_config(project_paths, config)
    updated = load_config(project_paths)
    assert updated["project"]["name"] == "Test Novel"
