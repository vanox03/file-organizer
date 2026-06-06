from pathlib import Path

from file_organizer.cli import main


def test_dry_run_prints_plan_without_moving_files(tmp_path: Path, capsys) -> None:
    source = tmp_path / "notes.txt"
    source.write_text("notes", encoding="utf-8")

    exit_code = main(["organize", str(tmp_path), "--dry-run"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "notes.txt -> Documents/notes.txt" in output
    assert source.exists()


def test_organize_moves_files(tmp_path: Path, capsys) -> None:
    (tmp_path / "notes.txt").write_text("notes", encoding="utf-8")

    exit_code = main(["organize", str(tmp_path)])

    assert exit_code == 0
    assert "Organized 1 file(s)." in capsys.readouterr().out
    assert (tmp_path / "Documents" / "notes.txt").exists()


def test_invalid_config_stops_before_moving_files(tmp_path: Path, capsys) -> None:
    source = tmp_path / "notes.txt"
    source.write_text("notes", encoding="utf-8")
    config = tmp_path / "invalid.toml"
    config.write_text("[rules\n", encoding="utf-8")

    exit_code = main(["organize", str(tmp_path), "--config", str(config)])

    assert exit_code == 2
    assert "error:" in capsys.readouterr().err
    assert source.exists()


def test_config_inside_target_directory_is_not_moved(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    config = tmp_path / "organizer.toml"
    config.write_text('[rules]\nDocuments = ["txt"]\n', encoding="utf-8")
    (tmp_path / "notes.txt").write_text("notes", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    exit_code = main(["organize", str(tmp_path), "--config", "organizer.toml"])

    assert exit_code == 0
    assert "Organized 1 file(s)." in capsys.readouterr().out
    assert config.exists()


def test_path_resolution_error_is_reported(monkeypatch, capsys) -> None:
    def raise_resolution_error(self, strict=False):
        raise RuntimeError("Symlink loop")

    monkeypatch.setattr(Path, "resolve", raise_resolution_error)

    exit_code = main(["organize", "."])

    assert exit_code == 2
    assert "error: Symlink loop" in capsys.readouterr().err
