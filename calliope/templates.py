"""Template loading utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

import yaml

from .character_db import CharacterStore
from .config import ProjectPaths


class TemplateError(RuntimeError):
    """Raised when template operations fail."""


def _templates_dir(paths: ProjectPaths, category: str) -> Path:
    directory = paths.root / "templates" / category
    if not directory.exists():
        raise TemplateError(f"No templates found for '{category}'.")
    return directory


def list_templates(paths: ProjectPaths) -> Dict[str, List[str]]:
    """Return dictionary of templates grouped by category."""
    base = paths.root / "templates"
    if not base.exists():
        raise TemplateError("Templates directory not found.")
    result: Dict[str, List[str]] = {}
    for category_dir in base.iterdir():
        if category_dir.is_dir():
            result[category_dir.name] = [file.stem for file in category_dir.glob("*.yaml")]
    return result


def load_template(paths: ProjectPaths, category: str, name: str) -> Tuple[Path, Dict[str, object]]:
    """Load template YAML file and return path plus data."""
    directory = _templates_dir(paths, category)
    template_path = directory / f"{name}.yaml"
    if not template_path.exists():
        raise TemplateError(f"Template '{name}' not found in {category}.")
    with template_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
        if not isinstance(data, dict):
            raise TemplateError(f"Template {template_path} has invalid structure.")
    return template_path, data


def apply_character_template(store: CharacterStore, data: Dict[str, object]) -> Dict[str, object]:
    """Fill character template into the store."""
    name = data.get("name")
    if not name:
        raise TemplateError("Character template must include a name.")
    store.add(data)
    return data
