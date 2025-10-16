"""Configuration management for Calliope projects."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Tuple

import yaml


CONFIG_DIR_NAME = ".calliope"
CONFIG_FILE_NAME = "config.yaml"
CHARACTERS_FILE_NAME = "characters.yaml"
METADATA_FILE_NAME = "metadata.yaml"
CONSISTENCY_DIR_NAME = "consistency_reports"


DEFAULT_CONFIG: Dict[str, Any] = {
    "project": {"name": "My Novel", "genre": "romance", "target_word_count": 80000},
    "ai": {
        "default_provider": "openai",
        "openai_api_key": "${OPENAI_API_KEY}",
        "anthropic_api_key": "${ANTHROPIC_API_KEY}",
        "model": "gpt-4",
        "temperature": 0.7,
    },
    "git": {"auto_commit": True, "commit_prefix": "✍️"},
}


DEFAULT_CHARACTERS: Dict[str, Any] = {"characters": []}

DEFAULT_METADATA: Dict[str, Any] = {
    "project_version": "0.1.0",
    "word_count": 0,
    "created_at": None,
    "last_modified": None,
}


@dataclass(frozen=True)
class ProjectPaths:
    """Convenience container for important project paths."""

    root: Path
    config_dir: Path
    config_file: Path
    characters_file: Path
    metadata_file: Path
    consistency_dir: Path
    chapters_dir: Path
    scenes_dir: Path
    notes_dir: Path
    exports_dir: Path


def get_project_paths(root: Path) -> ProjectPaths:
    """Return strongly-typed project paths for the provided root."""
    config_dir = root / CONFIG_DIR_NAME
    return ProjectPaths(
        root=root,
        config_dir=config_dir,
        config_file=config_dir / CONFIG_FILE_NAME,
        characters_file=config_dir / CHARACTERS_FILE_NAME,
        metadata_file=config_dir / METADATA_FILE_NAME,
        consistency_dir=config_dir / CONSISTENCY_DIR_NAME,
        chapters_dir=root / "chapters",
        scenes_dir=root / "scenes",
        notes_dir=root / "notes",
        exports_dir=root / "exports",
    )


def ensure_project_structure(paths: ProjectPaths) -> None:
    """Create the project directory layout if it does not exist."""
    directories = [
        paths.config_dir,
        paths.consistency_dir,
        paths.chapters_dir,
        paths.scenes_dir,
        paths.notes_dir,
        paths.exports_dir,
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def write_yaml(path: Path, data: Dict[str, Any]) -> None:
    """Write dict data to YAML file with safe dumper."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        yaml.dump(data, stream, sort_keys=False, allow_unicode=False)


def read_yaml(path: Path) -> Dict[str, Any]:
    """Read YAML file returning dict, or empty dict if missing."""
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream) or {}
        if not isinstance(data, dict):
            raise ValueError(f"Invalid YAML structure in {path}")
        return data


def bootstrap_project(paths: ProjectPaths) -> None:
    """Create config, characters, metadata files with defaults if absent."""
    write_yaml(paths.config_file, DEFAULT_CONFIG)
    write_yaml(paths.characters_file, DEFAULT_CHARACTERS)
    write_yaml(paths.metadata_file, DEFAULT_METADATA)


def load_config(paths: ProjectPaths) -> Dict[str, Any]:
    """Load the configuration file, returning defaults if missing."""
    if not paths.config_file.exists():
        write_yaml(paths.config_file, DEFAULT_CONFIG)
    return read_yaml(paths.config_file)


def save_config(paths: ProjectPaths, config: Dict[str, Any]) -> None:
    """Persist configuration changes."""
    write_yaml(paths.config_file, config)


def load_characters(paths: ProjectPaths) -> Dict[str, Any]:
    """Load characters YAML into dictionary."""
    if not paths.characters_file.exists():
        write_yaml(paths.characters_file, DEFAULT_CHARACTERS)
    return read_yaml(paths.characters_file)


def save_characters(paths: ProjectPaths, characters: Dict[str, Any]) -> None:
    """Persist character database to disk."""
    write_yaml(paths.characters_file, characters)


def load_metadata(paths: ProjectPaths) -> Dict[str, Any]:
    """Load metadata YAML into dictionary."""
    if not paths.metadata_file.exists():
        write_yaml(paths.metadata_file, DEFAULT_METADATA)
    return read_yaml(paths.metadata_file)


def save_metadata(paths: ProjectPaths, metadata: Dict[str, Any]) -> None:
    """Persist metadata to disk."""
    write_yaml(paths.metadata_file, metadata)


def resolve_project_root(start: Path) -> Tuple[Path, bool]:
    """
    Resolve the Calliope project root by looking for the config directory.

    Returns the resolved root path and a boolean indicating whether the root
    was discovered (True) or the start directory should be treated as the root (False).
    """
    current = start
    for _ in range(5):
        if (current / CONFIG_DIR_NAME).exists():
            return current, True
        if current.parent == current:
            break
        current = current.parent
    return start, False
