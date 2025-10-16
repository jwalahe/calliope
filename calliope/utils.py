"""Utility helpers for Calliope."""

from __future__ import annotations

import contextlib
import datetime as dt
import json
import os
from pathlib import Path
from typing import Iterable, Iterator, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm


_CONSOLE: Optional[Console] = None


def get_console() -> Console:
    """Return shared Rich console."""
    global _CONSOLE  # noqa: PLW0603 - module-level singleton is fine here
    if _CONSOLE is None:
        _CONSOLE = Console()
    return _CONSOLE


def now_iso() -> str:
    """Return current UTC timestamp in ISO format."""
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def human_join(items: Iterable[str]) -> str:
    """Return a human friendly conjunction string."""
    items = list(items)
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def render_panel(title: str, body: str, style: str = "cyan") -> None:
    """Render a titled panel message."""
    console = get_console()
    console.print(Panel(body, title=title, border_style=style))


@contextlib.contextmanager
def working_directory(path: Path) -> Iterator[None]:
    """Temporarily change directories."""
    original = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(original)


def confirm_action(message: str) -> bool:
    """Ask for confirmation using Rich Confirm."""
    return Confirm.ask(message)


def pretty_json(data: object) -> str:
    """Return pretty formatted JSON string."""
    return json.dumps(data, indent=2, sort_keys=False)
