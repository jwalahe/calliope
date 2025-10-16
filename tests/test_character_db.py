"""Tests for character store functionality."""

from __future__ import annotations

import pytest

from calliope.character_db import CharacterStore


def test_add_and_get_character(project_paths) -> None:
    store = CharacterStore(project_paths)
    character = {"name": "Elena", "age": 28, "personality": ["witty"]}
    store.add(character)
    loaded = store.get("Elena")
    assert loaded is not None
    assert loaded["age"] == 28


def test_update_character(project_paths) -> None:
    store = CharacterStore(project_paths)
    store.add({"name": "Marcus"})
    store.update("Marcus", {"role": "love interest"})
    updated = store.get("Marcus")
    assert updated["role"] == "love interest"


def test_add_duplicate_character_raises(project_paths) -> None:
    store = CharacterStore(project_paths)
    store.add({"name": "Elena"})
    with pytest.raises(ValueError):
        store.add({"name": "Elena"})
