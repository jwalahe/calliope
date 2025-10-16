# Contributing

Thank you for helping Calliope grow. This project thrives on community storytelling wisdom.

## Code of Conduct
Be respectful, inclusive, and collaborative. Romance and adult fiction communities are diverse—honour that diversity when collaborating.

## Getting Started
1. Fork the repository and clone your fork.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # optional extras, if added later
   ```
3. Run the test suite:
   ```bash
   pytest
   ```

## Development Workflow
- Create feature branches named `feature/<topic>` or `fix/<issue-number>`.
- Keep pull requests focused and well-described.
- Include tests for new features or bug fixes.
- Update documentation when behaviour changes.

## Style Guidelines
- Python 3.10+ with type hints.
- Follow PEP 8 and favour readability over cleverness.
- Use `rich` for CLI output styling.
- Keep CLI prompts friendly and informative.

## Submitting Templates
- Place character templates under `templates/characters/`.
- Place scene templates under `templates/scenes/`.
- Provide descriptive names and clear YAML fields.
- Document the template purpose in the PR description.

## Reporting Issues
- Include Calliope version (`calliope --version`).
- Describe steps to reproduce and expected vs. actual behaviour.
- Attach logs or tracebacks when available.

## Community
Join discussions via GitHub Issues and pull requests. Share scene templates, prompt ideas, and writing workflows—the muse favours collaboration.
