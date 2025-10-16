# Calliope

Calliope is a CLI-first writing companion that combines Git-powered version control with AI assistance for romance and adult-fiction authors. Track character arcs, generate new scenes, and export polished drafts without leaving the terminal.

## Features
- **Project scaffolding** – `calliope init` bootstraps a novel workspace with Git, config, and folders for chapters, scenes, and notes.
- **Character management** – Add, edit, and template characters backed by YAML and auto-committed to Git.
- **Consistency checking** – Run AI-powered reviews of chapters or scenes to catch contradictions in character details.
- **Scene generation** – Prompt an LLM with character context to draft new scenes or append to chapters.
- **Git insights** – Friendly wrappers around status, log, diff, branch, and commit with word-count awareness.
- **Exports** – Compile chapters into Markdown, DOCX, PDF (via pandoc), or plain text.
- **Templates** – Ship with archetype and scene templates tailored to romance storytelling.

## Installation
```bash
pip install -e .
# or
pip install calliope
```

Calliope requires Python 3.10+.

## Quick Start
```bash
calliope init my-novel
cd my-novel
calliope character add "Elena Martinez"
calliope generate scene "first-kiss"
calliope status
calliope export markdown
```

## Commands
- `calliope init <project>` – Create a new project directory and initialize Git.
- `calliope character add|list|show|edit` – Manage your character database stored in `.calliope/characters.yaml`.
- `calliope check --all | <files...>` – Run character consistency checks across scenes or chapters.
- `calliope generate scene <name>` – Interactive AI scene generation with optional chapter appends.
- `calliope status|commit|log|branch|diff` – Git utilities optimized for prose workflows.
- `calliope export <markdown|docx|pdf|txt>` – Assemble and export chapters to multiple formats.
- `calliope config ai` – Configure provider, model, and API keys (stored in `.env`).
- `calliope template list|use` – Explore and apply built-in character and scene templates.

Run `calliope --help` for the full command tree.

## Configuration
- Project settings live in `.calliope/config.yaml`.
- Characters and metadata are tracked in `.calliope/characters.yaml` and `.calliope/metadata.yaml`.
- API keys are stored in `.env` (ignored by Git). Use `calliope config ai` to update providers.
- Commit automation and prefixes are configured under the `git` section of the config.

## AI Providers
Calliope ships with provider abstractions for OpenAI, Anthropic Claude, and a stubbed local provider. Configure defaults and credentials via `calliope config ai`. The scene generator and consistency checker respect the chosen provider.

## Development
```bash
pip install -r requirements.txt
pytest
```

To contribute:
1. Fork and clone the repository.
2. Create a feature branch.
3. Add tests for new functionality.
4. Submit a pull request with clear descriptions.

## License
MIT © 2024 Your Name
