"""Export functionality for Calliope projects."""

from __future__ import annotations

import importlib
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from .config import ProjectPaths
from .utils import get_console


class ExportError(RuntimeError):
    """Raised when export operations fail."""


def _collect_chapters(paths: ProjectPaths) -> List[Tuple[str, Path]]:
    """Return list of chapter titles and paths sorted lexicographically."""
    chapters: List[Tuple[str, Path]] = []
    if paths.chapters_dir.exists():
        for file in sorted(paths.chapters_dir.glob("*.md")):
            chapters.append((file.stem.replace("-", " ").title(), file))
    return chapters


def _compose_markdown(chapters: List[Tuple[str, Path]], title: str, author: str = "") -> str:
    """Join chapters into a single markdown string."""
    lines = [f"# {title}"]
    if author:
        lines.append(f"### by {author}")
    lines.append("")
    for chapter_title, chapter_path in chapters:
        lines.append(f"# {chapter_title}")
        lines.append("")
        lines.append(chapter_path.read_text(encoding="utf-8"))
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def export_project(paths: ProjectPaths, config: Dict[str, object], fmt: str) -> Path:
    """Export project into chosen format."""
    console = get_console()
    chapters = _collect_chapters(paths)
    if not chapters:
        raise ExportError("No chapters found to export.")
    project_info = config.get("project", {}) if isinstance(config, dict) else {}
    title = project_info.get("name", paths.root.name)
    author = project_info.get("author", "")

    exports_dir = paths.exports_dir
    exports_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    base_filename = f"{paths.root.name}-{timestamp}"

    markdown_output = _compose_markdown(chapters, title, author)

    if fmt == "markdown":
        output_path = exports_dir / f"{base_filename}.md"
        output_path.write_text(markdown_output, encoding="utf-8")
        console.print(f"[green]Exported Markdown to {output_path}[/green]")
        return output_path

    if fmt == "txt":
        output_path = exports_dir / f"{base_filename}.txt"
        output_path.write_text(markdown_output, encoding="utf-8")
        console.print(f"[green]Exported text to {output_path}[/green]")
        return output_path

    if fmt == "docx":
        try:
            Document = importlib.import_module("docx").Document  # type: ignore[attr-defined]
        except ImportError as exc:
            raise ExportError("python-docx is required for DOCX export.") from exc
        document = Document()
        document.add_heading(title, 0)
        if author:
            document.add_heading(author, level=2)
        for chapter_title, chapter_path in chapters:
            document.add_heading(chapter_title, level=1)
            for paragraph in chapter_path.read_text(encoding="utf-8").split("\n\n"):
                document.add_paragraph(paragraph)
        output_path = exports_dir / f"{base_filename}.docx"
        document.save(str(output_path))
        console.print(f"[green]Exported DOCX to {output_path}[/green]")
        return output_path

    if fmt == "pdf":
        markdown_path = exports_dir / f"{base_filename}.md"
        markdown_path.write_text(markdown_output, encoding="utf-8")
        pdf_path = exports_dir / f"{base_filename}.pdf"
        try:
            subprocess.run(
                ["pandoc", str(markdown_path), "-o", str(pdf_path)],
                check=True,
                capture_output=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            raise ExportError("Pandoc is required for PDF export.") from exc
        console.print(f"[green]Exported PDF to {pdf_path}[/green]")
        return pdf_path

    raise ExportError(f"Unsupported export format '{fmt}'.")
