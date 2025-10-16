"""Tests for exporter functionality."""

from __future__ import annotations

from calliope.config import load_config
from calliope.exporter import export_project


def test_markdown_export(project_paths, tmp_path) -> None:
    chapter = project_paths.chapters_dir / "chapter-01.md"
    chapter.write_text("# Chapter One\n\nSome words here.", encoding="utf-8")
    config = load_config(project_paths)
    output_path = export_project(project_paths, config, "markdown")
    assert output_path.exists()
    assert output_path.suffix == ".md"
