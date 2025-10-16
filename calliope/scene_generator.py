"""Scene generation utilities using AI providers."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from rich.console import Console

from .ai_providers import AIProvider
from .character_db import CharacterStore
from .config import ProjectPaths
from .utils import get_console


PROMPT_TEMPLATE = """Write a scene for a {genre} novel with the following details:

Characters involved:
{characters_block}

Scene premise: {premise}
Tone: {tone}
POV: {pov}
Target length: ~{word_count} words

Write in a natural, engaging style. Maintain character consistency with the provided details. Focus on showing rather than telling. Include sensory details and emotional depth.

Additional instructions:
{instructions}
"""


def build_character_context(store: CharacterStore, character_names: List[str]) -> str:
    """Return formatted character descriptions from the database."""
    characters_block = []
    for name in character_names:
        character = store.get(name)
        if not character:
            continue
        summary_lines = [f"- {character.get('name', name)}"]
        for field in ("age", "physical", "personality", "backstory", "role"):
            value = character.get(field)
            if value:
                summary_lines.append(f"  {field.title()}: {value}")
        relationships = character.get("relationships")
        if relationships:
            summary_lines.append("  Relationships:")
            for rel in relationships:
                partner = rel.get("character", "Unknown")
                rel_type = rel.get("type", "relationship")
                notes = rel.get("notes", "")
                summary_lines.append(f"    - {partner} ({rel_type}) {notes}")
        characters_block.append("\n".join(summary_lines))
    return "\n".join(characters_block) if characters_block else "No character details available."


def generate_scene(
    provider: AIProvider,
    paths: ProjectPaths,
    config: Dict[str, object],
    store: CharacterStore,
    *,
    scene_name: str,
    premise: str,
    characters_involved: List[str],
    tone: str,
    pov: str,
    word_count: int,
    instructions: str = "",
    append_to: Optional[str] = None,
    console: Optional[Console] = None,
) -> Path:
    """Generate a scene using AI provider and write to disk."""
    console = console or get_console()
    characters_block = build_character_context(store, characters_involved)
    genre = config.get("project", {}).get("genre", "romance") if isinstance(config, dict) else "romance"
    prompt = PROMPT_TEMPLATE.format(
        genre=genre,
        characters_block=characters_block,
        premise=premise,
        tone=tone or "emotional",
        pov=pov or "third-person limited",
        word_count=word_count or 800,
        instructions=instructions or "None",
    )
    console.print("[blue]Generating scene...[/blue]")
    output = provider.generate(
        prompt,
        system_prompt="You are a fiction writing assistant crafting emotionally resonant scenes.",
        temperature=config.get("ai", {}).get("temperature", 0.7) if isinstance(config, dict) else 0.7,
    )

    scene_filename = f"{scene_name.replace(' ', '-').lower()}.md"
    scene_path = paths.scenes_dir / scene_filename
    scene_path.write_text(output + "\n", encoding="utf-8")

    if append_to:
        chapter_path = (paths.root / append_to).resolve()
        chapter_path.parent.mkdir(parents=True, exist_ok=True)
        with chapter_path.open("a", encoding="utf-8") as chapter_file:
            chapter_file.write(f"\n\n# Scene: {scene_name}\n\n")
            chapter_file.write(output + "\n")

    return scene_path
