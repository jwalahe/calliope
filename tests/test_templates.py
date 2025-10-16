"""Tests for template utilities."""

from __future__ import annotations

from calliope.templates import list_templates, load_template


def test_list_templates(project_paths) -> None:
    templates = list_templates(project_paths)
    assert "characters" in templates


def test_load_character_template(project_paths) -> None:
    path, data = load_template(project_paths, "characters", "romance-protagonist")
    assert path.name.endswith(".yaml")
    assert "name" in data
