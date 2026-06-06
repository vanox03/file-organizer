"""Command-line interface for file-organizer."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .config import ConfigError, load_config
from .organizer import execute_actions, plan_actions


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="file-organizer",
        description="Safely organize files into category folders.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    organize = subparsers.add_parser("organize", help="organize files in a directory")
    organize.add_argument("directory", nargs="?", type=Path, default=Path.cwd())
    organize.add_argument(
        "--dry-run",
        action="store_true",
        help="preview moves without changing the filesystem",
    )
    organize.add_argument("--config", type=Path, help="load rules from a TOML file")
    organize.add_argument(
        "--recursive",
        action="store_true",
        help="include files in subdirectories",
    )
    return parser


def _format_move(source: Path, destination: Path, root: Path) -> str:
    try:
        shown_source = source.relative_to(root)
        shown_destination = destination.relative_to(root)
    except ValueError:
        shown_source = source
        shown_destination = destination
    return f"{shown_source} -> {shown_destination}"


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    excluded_paths = {args.config} if args.config else set()

    try:
        root = args.directory.expanduser().resolve()
        config = load_config(args.config)
        actions = plan_actions(
            root,
            config,
            recursive=args.recursive,
            excluded_paths=excluded_paths,
        )
    except (ConfigError, NotADirectoryError, OSError, RuntimeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if not actions:
        print("Nothing to organize.")
        return 0

    heading = "Planned moves:" if args.dry_run else "Moves:"
    print(heading)
    for action in actions:
        print(f"  {_format_move(action.source, action.destination, root)}")

    if args.dry_run:
        print(f"Dry run complete: {len(actions)} file(s) would be moved.")
        return 0

    try:
        execute_actions(actions)
    except OSError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    print(f"Organized {len(actions)} file(s).")
    return 0
