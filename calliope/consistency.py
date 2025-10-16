"""Character consistency checking powered by AI."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from .ai_providers import AIProvider
from .character_db import CharacterStore
from .config import ProjectPaths
from .utils import get_console, now_iso


CONSISTENCY_PROMPT = """You are a fiction writing assistant checking for character consistency.

Character Database:
{character_database}

Text being analyzed:
{text}

Check for:
1. Physical description contradictions
2. Personality inconsistencies
3. Relationship status changes that don't align
4. Timeline issues

Output format:
CONSISTENT: [list any consistent elements]
WARNINGS: [list potential issues]
CONTRADICTIONS: [list clear contradictions with line references]
"""


def extract_mentions(text: str, character_names: Iterable[str]) -> Dict[str, List[int]]:
    """Return dictionary mapping character names to line numbers where they appear."""
    mentions = {name: [] for name in character_names}
    lines = text.splitlines()
    for idx, line in enumerate(lines, start=1):
        for name in character_names:
            pattern = rf"\b{name}\b"
            if re.search(pattern, line, re.IGNORECASE):
                mentions[name].append(idx)
    return {name: nums for name, nums in mentions.items() if nums}


def _character_database_dump(store: CharacterStore) -> str:
    """Return formatted character database text."""
    lines = []
    for character in store.characters:
        lines.append(character.get("name", "Unknown"))
        for key, value in character.items():
            if key == "name":
                continue
            lines.append(f"- {key}: {value}")
        lines.append("")
    return "\n".join(lines).strip()


def run_consistency_check(
    provider: AIProvider,
    paths: ProjectPaths,
    store: CharacterStore,
    files: Iterable[Path],
) -> Path:
    """Run consistency check on provided files and save report."""
    console = get_console()
    snippets: List[str] = []
    mention_report: List[str] = []
    for file in files:
        if not file.exists():
            console.print(f"[yellow]Skipping missing file {file}[/yellow]")
            continue
        text = file.read_text(encoding="utf-8")
        mentions = extract_mentions(text, store.list_names())
        snippet_header = f"# File: {file.relative_to(paths.root)}"
        snippets.append(snippet_header)
        snippets.append(text)
        if mentions:
            mention_report.append(f"{file.name}:")
            for name, lines in mentions.items():
                mention_report.append(f"  - {name}: lines {', '.join(map(str, lines))}")
    if not snippets:
        raise ValueError("No valid files provided for consistency check.")

    character_db = _character_database_dump(store)
    prompt = CONSISTENCY_PROMPT.format(
        character_database=character_db or "No characters defined yet.",
        text="\n\n".join(snippets),
    )
    console.print("[blue]Running AI consistency check...[/blue]")
    output = provider.generate(
        prompt,
        system_prompt="You are an editorial assistant focused on continuity and consistency.",
        temperature=0,
    )

    report_path = paths.consistency_dir / f"{now_iso().replace(':', '').replace('-', '')}.txt"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    content_lines = ["Calliope Character Consistency Report", ""]
    if mention_report:
        content_lines.extend(["Mentions:", *mention_report, ""])
    content_lines.extend([output.strip(), ""])
    report_path.write_text("\n".join(content_lines), encoding="utf-8")
    console.print(f"[green]Saved consistency report to {report_path}[/green]")
    return report_path
