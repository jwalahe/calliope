"""Character database management."""

from __future__ import annotations

from copy import deepcopy
from typing import Dict, List, Optional

from .config import ProjectPaths, load_characters, save_characters
from .utils import now_iso


Character = Dict[str, object]


class CharacterStore:
    """High-level character CRUD operations backed by YAML."""

    def __init__(self, paths: ProjectPaths) -> None:
        self.paths = paths
        self._data = load_characters(paths)

    @property
    def characters(self) -> List[Character]:
        """Return list of characters."""
        return list(self._data.get("characters", []))

    def list_names(self) -> List[str]:
        """Return sorted list of character names."""
        return sorted(char.get("name", "") for char in self.characters if char.get("name"))

    def get(self, name: str) -> Optional[Character]:
        """Return character dict by name."""
        for char in self.characters:
            if str(char.get("name", "")).lower() == name.lower():
                return deepcopy(char)
        return None

    def add(self, character: Character) -> Character:
        """Add a new character, raising if duplicate present."""
        if self.get(str(character.get("name", ""))):
            raise ValueError(f"Character '{character.get('name')}' already exists.")
        character = deepcopy(character)
        timestamp = now_iso()
        character.setdefault("created_at", timestamp)
        character.setdefault("last_modified", timestamp)
        self._data.setdefault("characters", []).append(character)
        save_characters(self.paths, self._data)
        return deepcopy(character)

    def update(self, name: str, updates: Character) -> Character:
        """Update character fields."""
        for index, char in enumerate(self._data.get("characters", [])):
            if str(char.get("name", "")).lower() == name.lower():
                merged = deepcopy(char)
                merged.update(updates)
                merged["last_modified"] = now_iso()
                self._data["characters"][index] = merged
                save_characters(self.paths, self._data)
                return deepcopy(merged)
        raise ValueError(f"Character '{name}' not found.")

    def remove(self, name: str) -> None:
        """Remove character by name."""
        current = self._data.get("characters", [])
        filtered = [char for char in current if str(char.get("name", "")).lower() != name.lower()]
        if len(filtered) == len(current):
            raise ValueError(f"Character '{name}' not found.")
        self._data["characters"] = filtered
        save_characters(self.paths, self._data)


def character_to_rich_table(character: Character) -> List[str]:
    """Return formatted lines describing character for CLI output."""
    lines: List[str] = []
    for key in [
        "name",
        "age",
        "physical",
        "personality",
        "backstory",
        "role",
        "relationships",
        "custom",
        "created_at",
        "last_modified",
    ]:
        if key not in character or character[key] in (None, "", []):
            continue
        value = character[key]
        if isinstance(value, list):
            render = ", ".join(str(item) for item in value)
        elif isinstance(value, dict):
            render = ", ".join(f"{k}: {v}" for k, v in value.items())
        else:
            render = str(value)
        lines.append(f"{key.title()}: {render}")
    return lines
