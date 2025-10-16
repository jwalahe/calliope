"""Git integration utilities built on top of GitPython."""

from __future__ import annotations

import io
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from git import GitCommandError, InvalidGitRepositoryError, NoSuchPathError, Repo

from .config import ProjectPaths
from .utils import get_console


class GitError(RuntimeError):
    """Raised when git operations fail."""


def get_repo(path: Path) -> Repo:
    """Return Repo instance for provided path, raising friendly error on failure."""
    try:
        return Repo(path)
    except (InvalidGitRepositoryError, NoSuchPathError) as exc:
        raise GitError(f"No Git repository found at {path}") from exc


def init_repository(path: Path, initial_message: str = "Initial commit") -> Repo:
    """Initialise a new git repository and create first commit."""
    repo = Repo.init(path)
    repo.git.add(all=True)
    if repo.is_dirty(untracked_files=True):
        repo.index.commit(initial_message)
    return repo


def ensure_repo(path: Path) -> Repo:
    """Return repo at path, initialising if necessary."""
    try:
        return get_repo(path)
    except GitError:
        return init_repository(path)


def commit(repo: Repo, message: str, paths: Optional[Iterable[Path]] = None) -> None:
    """Create a commit if there are staged or unstaged changes."""
    if paths:
        for path in paths:
            repo.index.add([str(path)])
    else:
        repo.git.add(all=True)
    if repo.is_dirty(untracked_files=True):
        repo.index.commit(message)


def status(repo: Repo) -> Tuple[List[str], List[str]]:
    """
    Return tuple of (staged, unstaged/untracked) file paths for repo.

    GitPython does not expose porcelain formatting directly, so use git status.
    """
    staged: List[str] = []
    modified: List[str] = []
    diff_index = []
    if repo.head.is_valid():
        diff_index = repo.index.diff("HEAD")
        for diff in diff_index:
            staged.append(diff.b_path or diff.a_path)
    for diff in repo.index.diff(None):
        modified.append(diff.b_path or diff.a_path)
    for path in repo.untracked_files:
        modified.append(path)
    return sorted(set(staged)), sorted(set(modified))


def human_status(repo: Repo, paths: ProjectPaths) -> str:
    """Return formatted status message with basic word count info."""
    staged, modified = status(repo)
    console = get_console()
    buffer = io.StringIO()
    buffer.write(f"📖 Project Status: {paths.root.name}\n\n")
    word_count = _calculate_word_count(paths)
    buffer.write(f"Word Count: {word_count:,} words\n")
    if modified:
        buffer.write(f"Modified/Untracked: {len(modified)} file(s)\n")
    if staged:
        buffer.write(f"Staged: {len(staged)} file(s)\n")
    buffer.write("\nGit Status:\n")
    for label, items in (("Staged", staged), ("Modified/Untracked", modified)):
        if not items:
            continue
        buffer.write(f"  {label}:\n")
        for item in items:
            buffer.write(f"    - {item}\n")
    return buffer.getvalue() or "Clean working tree"


def _calculate_word_count(paths: ProjectPaths) -> int:
    """Calculate total word count across chapter and scene markdown files."""
    total = 0
    for directory in (paths.chapters_dir, paths.scenes_dir):
        if not directory.exists():
            continue
        for file in directory.glob("*.md"):
            text = file.read_text(encoding="utf-8")
            total += len(text.split())
    return total


def show_log(repo: Repo, max_entries: int = 10) -> str:
    """Return formatted git log output."""
    try:
        logs = repo.git.log(f"-{max_entries}", "--stat", "--decorate")
    except GitCommandError as exc:
        raise GitError("Failed to read git log") from exc
    return logs


def create_branch(repo: Repo, name: str) -> None:
    """Create a new git branch."""
    try:
        repo.git.branch(name)
    except GitCommandError as exc:
        raise GitError(f"Failed to create branch {name}") from exc


def diff(repo: Repo, path: Optional[str] = None) -> str:
    """Return diff output."""
    try:
        if path:
            return repo.git.diff("--", path)
        return repo.git.diff()
    except GitCommandError as exc:
        raise GitError("Failed to obtain diff") from exc
