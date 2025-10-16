"""Calliope CLI entrypoint."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import List, Optional

import click
from rich.table import Table

from .ai_providers import ProviderError, provider_from_config
from .character_db import CharacterStore, character_to_rich_table
from .config import (
    DEFAULT_CONFIG,
    ProjectPaths,
    bootstrap_project,
    ensure_project_structure,
    get_project_paths,
    load_config,
    load_metadata,
    resolve_project_root,
    save_config,
)
from .consistency import run_consistency_check
from .exporter import ExportError, export_project
from .git_ops import GitError, commit, create_branch, diff, ensure_repo, human_status, show_log
from .scene_generator import generate_scene
from .templates import TemplateError, apply_character_template, list_templates as list_template_defs, load_template
from .utils import confirm_action, get_console, human_join


console = get_console()


def main() -> None:
    """Console script entry point."""
    cli()


def _write_gitignore(path: Path) -> None:
    contents = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/

# Environment variables
.env
.env.local

# Calliope specific
.calliope/
!.calliope/config.yaml.example
exports/
*.docx
*.pdf

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo
"""
    (path / ".gitignore").write_text(contents, encoding="utf-8")


def _copy_default_templates(destination: Path) -> None:
    templates_src = Path(__file__).resolve().parent.parent / "templates"
    if templates_src.exists():
        shutil.copytree(templates_src, destination / "templates", dirs_exist_ok=True)


def _ensure_project_context(path: Optional[Path] = None) -> ProjectPaths:
    start = path or Path.cwd()
    root, found = resolve_project_root(start)
    if not found:
        raise click.ClickException("Not a Calliope project. Run `calliope init <project>` first.")
    project_paths = get_project_paths(root)
    ensure_project_structure(project_paths)
    return project_paths


def _load_store(paths: ProjectPaths) -> CharacterStore:
    return CharacterStore(paths)


def _autocommit(paths: ProjectPaths, config: dict, message: str) -> None:
    if config.get("git", {}).get("auto_commit", True):
        repo = ensure_repo(paths.root)
        commit_prefix = config.get("git", {}).get("commit_prefix", "")
        commit(repo, f"{commit_prefix} {message}".strip())


@click.group()
@click.version_option(package_name="calliope")
def cli() -> None:
    """Calliope - Git-based version control for fiction writers."""
    pass  # pylint: disable=unnecessary-pass


@cli.command()
@click.argument("project_name")
def init(project_name: str) -> None:
    """Initialize a new Calliope project."""
    project_root = Path.cwd() / project_name
    if project_root.exists() and any(project_root.iterdir()):
        raise click.ClickException(f"Directory {project_root} already exists and is not empty.")
    project_root.mkdir(parents=True, exist_ok=True)
    paths = get_project_paths(project_root)
    ensure_project_structure(paths)
    bootstrap_project(paths)
    _copy_default_templates(project_root)
    _write_gitignore(project_root)
    (project_root / "chapters" / "chapter-01.md").write_text("# Chapter 01\n\nWrite your story...", encoding="utf-8")
    (project_root / "notes" / "ideas.md").write_text("# Story Ideas\n\n- ", encoding="utf-8")
    repo = ensure_repo(project_root)
    commit(repo, "Initial commit")
    console.print(f"[green]Initialized Calliope project at {project_root}[/green]")
    console.print("Next steps:\n- Run `cd {}`\n- Add characters with `calliope character add`".format(project_root))


@cli.group()
def character() -> None:
    """Manage characters."""


@character.command("add")
@click.argument("name")
def character_add(name: str) -> None:
    """Add a new character."""
    paths = _ensure_project_context()
    store = _load_store(paths)
    config = load_config(paths)
    character = {
        "name": name,
        "age": click.prompt("Age", default="", show_default=False),
        "physical": click.prompt("Physical description", default="", show_default=False),
        "personality": [
            trait.strip()
            for trait in click.prompt("Personality traits (comma separated)", default="", show_default=False).split(",")
            if trait.strip()
        ],
        "backstory": click.prompt("Backstory", default="", show_default=False),
        "role": click.prompt("Role in story", default="", show_default=False),
    }
    relationships: List[dict] = []
    while click.confirm("Add relationship?", default=False):
        rel_character = click.prompt("Related character name")
        rel_type = click.prompt("Relationship type", default="relationship")
        rel_notes = click.prompt("Notes", default="", show_default=False)
        relationships.append({"character": rel_character, "type": rel_type, "notes": rel_notes})
    if relationships:
        character["relationships"] = relationships
    custom_entries = {}
    while click.confirm("Add custom attribute?", default=False):
        key = click.prompt("Attribute name")
        value = click.prompt("Attribute value")
        custom_entries[key] = value
    if custom_entries:
        character["custom"] = custom_entries
    try:
        store.add(character)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    _autocommit(paths, config, f"Add character: {name}")
    console.print(f"[green]Character '{name}' added.[/green]")


@character.command("list")
def character_list() -> None:
    """List all characters."""
    paths = _ensure_project_context()
    store = _load_store(paths)
    names = store.list_names()
    if not names:
        console.print("[yellow]No characters found. Add one with `calliope character add`.[/yellow]")
        return
    table = Table(title="Characters")
    table.add_column("Name")
    for name in names:
        table.add_row(name)
    console.print(table)


@character.command("show")
@click.argument("name")
def character_show(name: str) -> None:
    """Show character details."""
    paths = _ensure_project_context()
    store = _load_store(paths)
    character = store.get(name)
    if not character:
        raise click.ClickException(f"Character '{name}' not found.")
    lines = character_to_rich_table(character)
    console.print("\n".join(lines))


@character.command("edit")
@click.argument("name")
def character_edit(name: str) -> None:
    """Edit character attributes."""
    paths = _ensure_project_context()
    store = _load_store(paths)
    config = load_config(paths)
    character = store.get(name)
    if not character:
        raise click.ClickException(f"Character '{name}' not found.")
    for field in ["age", "physical", "backstory", "role"]:
        current = character.get(field, "")
        new_value = click.prompt(f"{field.title()} [{current}]", default=current or "", show_default=False)
        character[field] = new_value
    current_traits = ", ".join(character.get("personality", []))
    traits_string = click.prompt(
        f"Personality traits (comma separated) [{current_traits}]",
        default=current_traits,
        show_default=False,
    )
    character["personality"] = [trait.strip() for trait in traits_string.split(",") if trait.strip()]
    store.update(name, character)
    _autocommit(paths, config, f"Update character: {name}")
    console.print(f"[green]Character '{name}' updated.[/green]")


@cli.command()
@click.argument("files", nargs=-1, type=click.Path(path_type=Path))
@click.option("--all", "check_all", is_flag=True, help="Check all chapters and scenes.")
def check(files: List[Path], check_all: bool) -> None:
    """Run character consistency checker on files."""
    paths = _ensure_project_context()
    config = load_config(paths)
    store = _load_store(paths)
    try:
        provider = provider_from_config(config)
    except ProviderError as exc:
        raise click.ClickException(str(exc)) from exc

    targets: List[Path] = []
    if check_all:
        targets.extend(paths.chapters_dir.glob("*.md"))
        targets.extend(paths.scenes_dir.glob("*.md"))
    else:
        targets.extend(files)
    if not targets:
        raise click.ClickException("Provide files or use --all.")
    report_path = run_consistency_check(provider, paths, store, targets)
    console.print(f"[green]Report saved to {report_path}[/green]")


@cli.group()
def generate() -> None:
    """AI generation commands."""


@generate.command("scene")
@click.argument("scene_name")
@click.option("--append-to", type=str, help="Append generated scene to an existing chapter.")
def scene_generate(scene_name: str, append_to: Optional[str]) -> None:
    """Generate a new scene with AI assistance."""
    paths = _ensure_project_context()
    config = load_config(paths)
    store = _load_store(paths)
    try:
        provider = provider_from_config(config)
    except ProviderError as exc:
        raise click.ClickException(str(exc)) from exc
    premise = click.prompt("Scene description/premise")
    characters_involved = []
    available = store.list_names()
    while True:
        if available:
            console.print(f"Available characters: {human_join(available)}")
        character = click.prompt("Include character (leave blank to finish)", default="", show_default=False)
        if not character:
            break
        characters_involved.append(character)
    tone = click.prompt("Tone/Mood", default="romantic tension")
    pov = click.prompt("POV character", default=characters_involved[0] if characters_involved else "")
    word_count = click.prompt("Target word count", default=800, type=int)
    instructions = click.prompt("Additional instructions", default="", show_default=False)
    scene_path = generate_scene(
        provider,
        paths,
        config,
        store,
        scene_name=scene_name,
        premise=premise,
        characters_involved=characters_involved,
        tone=tone,
        pov=pov,
        word_count=word_count,
        instructions=instructions,
        append_to=append_to,
        console=console,
    )
    _autocommit(paths, config, f"Generate scene: {scene_name}")
    console.print(f"[green]Scene saved to {scene_path}[/green]")


@cli.command()
def status() -> None:
    """Show Git status with story context."""
    paths = _ensure_project_context()
    try:
        repo = ensure_repo(paths.root)
    except GitError as exc:
        raise click.ClickException(str(exc)) from exc
    console.print(human_status(repo, paths))


@cli.command(name="commit")
@click.argument("message", required=False)
def commit_cmd(message: Optional[str]) -> None:
    """Commit changes with optional message."""
    paths = _ensure_project_context()
    repo = ensure_repo(paths.root)
    config = load_config(paths)
    prefix = config.get("git", {}).get("commit_prefix", "")
    if not message:
        message = click.prompt("Commit message")
    commit(repo, f"{prefix} {message}".strip())
    console.print("[green]Commit created.[/green]")


@cli.command()
def log() -> None:
    """Show recent commit history."""
    paths = _ensure_project_context()
    repo = ensure_repo(paths.root)
    console.print(show_log(repo))


@cli.command()
@click.argument("name")
def branch(name: str) -> None:
    """Create a new branch for alternate storyline."""
    paths = _ensure_project_context()
    repo = ensure_repo(paths.root)
    try:
        create_branch(repo, name)
    except GitError as exc:
        raise click.ClickException(str(exc)) from exc
    console.print(f"[green]Created branch {name}[/green]")


@cli.command(name="diff")
@click.argument("file", required=False)
def diff_cmd(file: Optional[str]) -> None:
    """Show prose-friendly diff output."""
    paths = _ensure_project_context()
    repo = ensure_repo(paths.root)
    console.print(diff(repo, file))


@cli.command()
@click.argument("fmt", type=click.Choice(["markdown", "docx", "pdf", "txt"], case_sensitive=False))
def export(fmt: str) -> None:
    """Export project into different formats."""
    paths = _ensure_project_context()
    config = load_config(paths)
    try:
        export_project(paths, config, fmt.lower())
    except ExportError as exc:
        raise click.ClickException(str(exc)) from exc


@cli.group(name="config")
def config_group() -> None:
    """Configuration commands."""


@config_group.command("ai")
def config_ai() -> None:
    """Configure AI providers and credentials."""
    paths = _ensure_project_context()
    config = load_config(paths)
    ai_config = config.get("ai", DEFAULT_CONFIG["ai"])
    provider = click.prompt(
        "Default provider",
        default=ai_config.get("default_provider", "openai"),
        type=click.Choice(["openai", "claude", "local"], case_sensitive=False),
    )
    model = click.prompt("Model", default=ai_config.get("model", "gpt-4"))
    temperature = click.prompt("Temperature", default=ai_config.get("temperature", 0.7), type=float)
    openai_key = click.prompt(
        "OpenAI API key (leave blank to keep current)", default="", show_default=False
    ).strip()
    claude_key = click.prompt(
        "Anthropic Claude API key (leave blank to keep current)", default="", show_default=False
    ).strip()

    ai_config.update({"default_provider": provider, "model": model, "temperature": temperature})
    if openai_key:
        ai_config["openai_api_key"] = openai_key
    if claude_key:
        ai_config["anthropic_api_key"] = claude_key
    config["ai"] = ai_config
    save_config(paths, config)

    env_path = paths.root / ".env"
    env_lines = []
    if openai_key:
        env_lines.append(f"OPENAI_API_KEY={openai_key}")
    if claude_key:
        env_lines.append(f"ANTHROPIC_API_KEY={claude_key}")
    if env_lines:
        with env_path.open("a", encoding="utf-8") as env_file:
            env_file.write("\n".join(env_lines) + "\n")
        console.print(f"[green]Updated {env_path}[/green]")

    console.print("[green]AI configuration saved.[/green]")


@cli.command()
def info() -> None:
    """Show project metadata."""
    paths = _ensure_project_context()
    metadata = load_metadata(paths)
    console.print(metadata)


@cli.command()
def cleanup() -> None:
    """Remove generated exports and reports."""
    paths = _ensure_project_context()
    targets = [paths.exports_dir, paths.consistency_dir]
    to_remove = [target for target in targets if target.exists() and any(target.iterdir())]
    if not to_remove:
        console.print("[yellow]Nothing to clean.[/yellow]")
        return
    if not confirm_action("Delete generated exports and reports?"):
        console.print("[yellow]Aborted.[/yellow]")
        return
    for directory in to_remove:
        for file in directory.iterdir():
            if file.is_file():
                file.unlink()
    console.print("[green]Cleanup complete.[/green]")


@cli.group()
def template() -> None:
    """Template management."""


@template.command("list")
def template_list() -> None:
    """List available templates."""
    paths = _ensure_project_context()
    try:
        templates = list_template_defs(paths)
    except TemplateError as exc:
        raise click.ClickException(str(exc)) from exc
    table = Table(title="Available Templates")
    table.add_column("Category")
    table.add_column("Templates")
    for category, entries in templates.items():
        table.add_row(category, ", ".join(entries) if entries else "None")
    console.print(table)


@template.command("use")
@click.argument("category", type=click.Choice(["character", "scene"], case_sensitive=False))
@click.argument("template_name")
def template_use(category: str, template_name: str) -> None:
    """Apply a template to pre-fill data."""
    paths = _ensure_project_context()
    category = category.lower()
    try:
        _, data = load_template(paths, f"{category}s", template_name)
    except TemplateError as exc:
        raise click.ClickException(str(exc)) from exc

    config = load_config(paths)
    if category == "character":
        store = _load_store(paths)
        default_name = data.get("name", template_name.replace("-", " ").title())
        name = click.prompt("Character name", default=default_name)
        data["name"] = name
        try:
            apply_character_template(store, data)
        except TemplateError as exc:
            raise click.ClickException(str(exc)) from exc
        _autocommit(paths, config, f"Add character: {name}")
        console.print(f"[green]Character template '{template_name}' applied as {name}.[/green]")
        return

    if category == "scene":
        scene_name = click.prompt("Scene file name", default=data.get("name", template_name))
        scene_filename = f"{scene_name.replace(' ', '-').lower()}.md"
        scene_path = paths.scenes_dir / scene_filename
        beats = data.get("beats", [])
        content_lines = [f"# {scene_name}", ""]
        content_lines.append(data.get("premise", ""))
        if beats:
            content_lines.append("")
            content_lines.append("## Story Beats")
            for beat in beats:
                content_lines.append(f"- {beat}")
        scene_path.write_text("\n".join(content_lines).strip() + "\n", encoding="utf-8")
        _autocommit(paths, config, f"Add scene template: {scene_name}")
        console.print(f"[green]Scene template '{template_name}' created at {scene_path}[/green]")
        return

    raise click.ClickException(f"Unknown template category {category}")


if __name__ == "__main__":  # pragma: no cover
    main()
