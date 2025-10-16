"""Tests for scene generation."""

from __future__ import annotations

from calliope.character_db import CharacterStore
from calliope.scene_generator import generate_scene


class DummyProvider:
    def generate(self, prompt: str, **kwargs):
        return "Generated scene content."


def test_generate_scene_writes_file(project_paths) -> None:
    store = CharacterStore(project_paths)
    store.add({"name": "Elena", "personality": ["witty"]})
    config = {"project": {"genre": "romance"}, "ai": {"temperature": 0.5}}
    path = generate_scene(
        DummyProvider(),
        project_paths,
        config,
        store,
        scene_name="test scene",
        premise="A chance encounter.",
        characters_involved=["Elena"],
        tone="light",
        pov="Elena",
        word_count=500,
        instructions="Keep dialogue snappy.",
    )
    assert path.exists()
    assert "Generated scene content" in path.read_text(encoding="utf-8")
