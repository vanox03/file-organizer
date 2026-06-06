import errno
import os
from pathlib import Path

import pytest

from file_organizer.config import load_config
from file_organizer.organizer import MoveAction, execute_actions, plan_actions


def test_plan_ignores_hidden_files_subdirectories_and_category_folders(tmp_path: Path) -> None:
    (tmp_path / "photo.jpg").write_text("photo", encoding="utf-8")
    (tmp_path / ".secret.txt").write_text("secret", encoding="utf-8")
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "notes.txt").write_text("notes", encoding="utf-8")
    (tmp_path / "Images").mkdir()
    (tmp_path / "Images" / "done.jpg").write_text("done", encoding="utf-8")

    actions = plan_actions(tmp_path, load_config())

    assert [(action.source.name, action.category) for action in actions] == [
        ("photo.jpg", "Images")
    ]


def test_recursive_plan_includes_nested_files_but_skips_organized_files(tmp_path: Path) -> None:
    (tmp_path / "nested").mkdir()
    nested_file = tmp_path / "nested" / "notes.txt"
    nested_file.write_text("notes", encoding="utf-8")
    (tmp_path / "Documents").mkdir()
    (tmp_path / "Documents" / "done.txt").write_text("done", encoding="utf-8")

    actions = plan_actions(tmp_path, load_config(), recursive=True)

    assert actions == [
        MoveAction(nested_file.resolve(), tmp_path / "Documents" / "notes.txt", "Documents")
    ]


def test_plan_resolves_existing_and_planned_collisions(tmp_path: Path) -> None:
    (tmp_path / "one").mkdir()
    (tmp_path / "two").mkdir()
    (tmp_path / "one" / "photo.jpg").write_text("one", encoding="utf-8")
    (tmp_path / "two" / "photo.jpg").write_text("two", encoding="utf-8")
    (tmp_path / "Images").mkdir()
    (tmp_path / "Images" / "photo.jpg").write_text("existing", encoding="utf-8")

    actions = plan_actions(tmp_path, load_config(), recursive=True)

    assert [action.destination.name for action in actions] == ["photo (1).jpg", "photo (2).jpg"]


def test_execute_moves_files_without_overwriting(tmp_path: Path) -> None:
    source = tmp_path / "notes.txt"
    source.write_text("notes", encoding="utf-8")
    actions = plan_actions(tmp_path, load_config())

    execute_actions(actions)

    assert not source.exists()
    assert (tmp_path / "Documents" / "notes.txt").read_text(encoding="utf-8") == "notes"


def test_execute_refuses_destination_created_after_plan(tmp_path: Path) -> None:
    source = tmp_path / "notes.txt"
    source.write_text("source", encoding="utf-8")
    actions = plan_actions(tmp_path, load_config())
    destination = actions[0].destination
    destination.parent.mkdir()
    destination.write_text("existing", encoding="utf-8")

    with pytest.raises(FileExistsError):
        execute_actions(actions)

    assert source.exists()
    assert destination.read_text(encoding="utf-8") == "existing"


def test_execute_falls_back_to_exclusive_copy_across_filesystems(
    tmp_path: Path, monkeypatch
) -> None:
    source = tmp_path / "notes.txt"
    source.write_text("notes", encoding="utf-8")
    actions = plan_actions(tmp_path, load_config())

    def raise_cross_device(*args, **kwargs) -> None:
        raise OSError(errno.EXDEV, "Cross-device link")

    monkeypatch.setattr(os, "link", raise_cross_device)

    execute_actions(actions)

    assert not source.exists()
    assert actions[0].destination.read_text(encoding="utf-8") == "notes"


def test_exclusive_copy_fallback_never_removes_existing_destination(
    tmp_path: Path, monkeypatch
) -> None:
    source = tmp_path / "notes.txt"
    source.write_text("source", encoding="utf-8")
    actions = plan_actions(tmp_path, load_config())
    destination = actions[0].destination
    destination.parent.mkdir()
    destination.write_text("existing", encoding="utf-8")

    def raise_cross_device(*args, **kwargs) -> None:
        raise OSError(errno.EXDEV, "Cross-device link")

    monkeypatch.setattr(os, "link", raise_cross_device)

    with pytest.raises(FileExistsError):
        execute_actions(actions)

    assert source.read_text(encoding="utf-8") == "source"
    assert destination.read_text(encoding="utf-8") == "existing"


def test_plan_skips_symlinks(tmp_path: Path) -> None:
    target = tmp_path / "target.txt"
    target.write_text("target", encoding="utf-8")
    link = tmp_path / "link.txt"
    link.symlink_to(target)

    actions = plan_actions(tmp_path, load_config())

    assert [action.source.name for action in actions] == ["target.txt"]
