"""Tests for git operation helpers."""

from __future__ import annotations

from pathlib import Path

from calliope.git_ops import commit, ensure_repo, human_status


def test_commit_adds_file(project_paths) -> None:
    repo = ensure_repo(project_paths.root)
    sample_file = project_paths.root / "chapters" / "chapter-02.md"
    sample_file.write_text("Content", encoding="utf-8")
    commit(repo, "Add chapter 2")
    assert not repo.is_dirty()


def test_human_status_returns_string(project_paths) -> None:
    repo = ensure_repo(project_paths.root)
    status = human_status(repo, project_paths)
    assert "Project Status" in status
