"""Tests for consistency checker."""

from __future__ import annotations

from pathlib import Path

from calliope.character_db import CharacterStore
from calliope.consistency import run_consistency_check


class FakeProvider:
    def generate(self, prompt: str, **kwargs):  # noqa: D401,ANN001 for test stub
        return "CONSISTENT: []\nWARNINGS: []\nCONTRADICTIONS: []"


def test_consistency_creates_report(project_paths, tmp_path) -> None:
    store = CharacterStore(project_paths)
    store.add({"name": "Elena"})
    scene = project_paths.scenes_dir / "scene.md"
    scene.write_text("Elena walks into the room.", encoding="utf-8")
    provider = FakeProvider()
    report_path = run_consistency_check(provider, project_paths, store, [scene])
    assert report_path.exists()
