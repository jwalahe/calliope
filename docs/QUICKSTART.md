# Quickstart

Get up and writing with Calliope in minutes.

## 1. Install
```bash
pip install -e .
# or from PyPI (once published)
pip install calliope
```

## 2. Initialize a Project
```bash
calliope init summer-fling
cd summer-fling
```

Project structure:
```
summer-fling/
├── .calliope/
├── chapters/
├── scenes/
├── notes/
└── exports/
```

## 3. Add Characters
```bash
calliope character add "Elena Martinez"
calliope character add "Marcus Hale"
calliope character list
```

## 4. Configure AI (Optional)
```bash
calliope config ai
```
Choose a provider and supply API keys (stored safely in `.env`).

## 5. Generate a Scene
```bash
calliope generate scene "first-date"
```
Respond to prompts for premise, tone, POV, and instructions. The scene is saved to `scenes/first-date.md`.

## 6. Check Continuity
```bash
calliope check --all
```
Reports are saved in `.calliope/consistency_reports/`.

## 7. Export Draft
```bash
calliope export docx
```
Find the compiled manuscript in `exports/`.

## 8. Iterate
Use `calliope status`, `calliope commit`, and `calliope log` to keep your creative Git history tidy.
