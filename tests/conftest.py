"\"\"\"Common pytest fixtures for Calliope.\"\"\""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterator

import pytest

from calliope.config import bootstrap_project, ensure_project_structure, get_project_paths
from calliope.git_ops import ensure_repo


@pytest.fixture()
def project_paths(tmp_path: Path) -> Iterator[Path]:
    """Provide a temporary Calliope project structure."""
    root = tmp_path / "novel"
    root.mkdir()
    paths = get_project_paths(root)
    ensure_project_structure(paths)
    repo_templates = Path(__file__).resolve().parents[1] / "templates"
    if repo_templates.exists():
        shutil.copytree(repo_templates, root / "templates", dirs_exist_ok=True)
    bootstrap_project(paths)
    ensure_repo(root)
    yield paths
    shutil.rmtree(root, ignore_errors=True)
