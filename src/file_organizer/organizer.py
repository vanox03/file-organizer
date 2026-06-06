"""Plan and execute safe file organization actions."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import shutil

from .config import OrganizerConfig


@dataclass(frozen=True)
class MoveAction:
    source: Path
    destination: Path
    category: str


def _is_hidden(relative_path: Path) -> bool:
    return any(part.startswith(".") for part in relative_path.parts)


def _unique_destination(destination: Path, reserved: set[Path]) -> Path:
    candidate = destination
    counter = 1
    while candidate.exists() or candidate in reserved:
        candidate = destination.with_name(f"{destination.stem} ({counter}){destination.suffix}")
        counter += 1
    return candidate


def plan_actions(
    directory: Path,
    config: OrganizerConfig,
    *,
    recursive: bool = False,
    excluded_paths: set[Path] | None = None,
) -> list[MoveAction]:
    """Return the moves needed to organize a directory without changing it."""
    root = directory.expanduser().resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"Directory not found: {directory}")

    excluded = {path.expanduser().resolve() for path in (excluded_paths or set())}
    candidates = root.rglob("*") if recursive else root.iterdir()
    reserved: set[Path] = set()
    actions: list[MoveAction] = []

    for source in sorted(candidates):
        if source.is_symlink() or not source.is_file():
            continue

        relative = source.relative_to(root)
        resolved_source = source.resolve()
        if not resolved_source.is_relative_to(root):
            continue
        if resolved_source in excluded or _is_hidden(relative):
            continue
        if relative.parts[0] in config.category_names:
            continue

        category = config.category_for(resolved_source)
        destination = _unique_destination(root / category / source.name, reserved)
        if resolved_source == destination:
            continue

        reserved.add(destination)
        actions.append(MoveAction(resolved_source, destination, category))

    return actions


def execute_actions(actions: list[MoveAction]) -> None:
    """Execute planned moves, refusing to overwrite destinations created meanwhile."""
    for action in actions:
        action.destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.link(action.source, action.destination, follow_symlinks=False)
        except FileExistsError:
            raise FileExistsError(f"Destination already exists: {action.destination}") from None
        except OSError:
            _copy_exclusive(action.source, action.destination)
        else:
            try:
                action.source.unlink()
            except OSError:
                action.destination.unlink(missing_ok=True)
                raise


def _copy_exclusive(source: Path, destination: Path) -> None:
    """Move by copying into an exclusively created destination."""
    destination_created = False
    try:
        with destination.open("xb") as destination_file:
            destination_created = True
            with source.open("rb") as source_file:
                shutil.copyfileobj(source_file, destination_file)
        shutil.copystat(source, destination, follow_symlinks=False)
    except OSError:
        if destination_created:
            destination.unlink(missing_ok=True)
        raise

    source.unlink()
