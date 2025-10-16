# Calliope Documentation

Welcome to the Calliope documentation set. This section outlines the CLI workflow, AI integrations, and project structure that power the tool.

## Contents
- [Quickstart](QUICKSTART.md) – Install and create your first project.
- [CLI Reference](#cli-reference) – Command overview grouped by feature.
- [Configuration](#configuration) – Manage AI providers, Git automation, and metadata.
- [Extending Calliope](#extending-calliope) – Add new templates or AI providers.

## CLI Reference
### Project Setup
- `calliope init <project>` – Bootstrap a new writing workspace.
- `calliope status` – Summarize Git status and word counts.

### Character Management
- `calliope character add <name>`
- `calliope character list`
- `calliope character show <name>`
- `calliope character edit <name>`

Characters are stored in `.calliope/characters.yaml` with timestamps for auditing.

### AI Assistance
- `calliope generate scene <name>` – Build prompts with character context and tone guidance.
- `calliope check --all` or `calliope check <files...>` – Continuity review for Markdown chapters/scenes.
- `calliope config ai` – Choose provider, model, temperature, and API keys.

### Git Workflow
- `calliope commit [message]`
- `calliope log`
- `calliope branch <name>`
- `calliope diff [file]`

### Templates
- `calliope template list`
- `calliope template use character <template>`
- `calliope template use scene <template>`

## Configuration
Calliope configuration files live in `.calliope/`:
- `config.yaml` – project metadata, AI settings, Git preferences.
- `characters.yaml` – full character bible.
- `metadata.yaml` – word counts and timestamps.
- `consistency_reports/` – AI generated reports with timestamps.

Environment variables (API keys) are written to `.env` and should never be committed.

## Extending Calliope
### Adding Templates
Place YAML files under `templates/characters/` or `templates/scenes/`. Use `calliope template list` to verify discovery, then share with the community.

### New AI Providers
Implement `AIProvider.generate()` in `calliope/ai_providers.py` or create a plugin module, then register via configuration.

## Support
- File issues on GitHub.
- Join the community discussions for template swaps and story craft tips.
