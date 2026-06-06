from pathlib import Path

import pytest

from file_organizer.config import ConfigError, load_config


def test_default_config_categorizes_known_and_unknown_files() -> None:
    config = load_config()

    assert config.category_for(Path("photo.JPG")) == "Images"
    assert config.category_for(Path("unknown.xyz")) == "Other"


def test_custom_config_normalizes_extensions(tmp_path: Path) -> None:
    config_path = tmp_path / "rules.toml"
    config_path.write_text(
        """
[rules]
Pictures = ["JPG", ".png"]

[settings]
uncategorized = "Misc"
""".strip(),
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.category_for(Path("photo.jpg")) == "Pictures"
    assert config.category_for(Path("notes.txt")) == "Misc"


@pytest.mark.parametrize(
    "content",
    [
        "[rules\nbroken = true",
        "[rules]\nImages = []",
        '[rules]\n"../unsafe" = ["txt"]',
        '[rules]\nImages = ["txt"]\nDocuments = ["txt"]',
    ],
)
def test_invalid_config_raises_clear_error(tmp_path: Path, content: str) -> None:
    config_path = tmp_path / "invalid.toml"
    config_path.write_text(content, encoding="utf-8")

    with pytest.raises(ConfigError):
        load_config(config_path)
