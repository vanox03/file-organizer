"""Configuration loading and validation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib


DEFAULT_RULES: dict[str, tuple[str, ...]] = {
    "Images": (".bmp", ".gif", ".jpeg", ".jpg", ".png", ".svg", ".webp"),
    "Documents": (".csv", ".doc", ".docx", ".md", ".pdf", ".ppt", ".pptx", ".txt", ".xls", ".xlsx"),
    "Audio": (".aac", ".flac", ".m4a", ".mp3", ".ogg", ".wav"),
    "Video": (".avi", ".mkv", ".mov", ".mp4", ".webm"),
    "Archives": (".7z", ".gz", ".rar", ".tar", ".zip"),
}


class ConfigError(ValueError):
    """Raised when an organizer configuration is invalid."""


@dataclass(frozen=True)
class OrganizerConfig:
    rules: dict[str, tuple[str, ...]]
    uncategorized: str = "Other"

    @property
    def category_names(self) -> frozenset[str]:
        return frozenset((*self.rules.keys(), self.uncategorized))

    def category_for(self, path: Path) -> str:
        extension = path.suffix.lower()
        for category, extensions in self.rules.items():
            if extension in extensions:
                return category
        return self.uncategorized


def _validate_category(category: object) -> str:
    if not isinstance(category, str) or not category.strip():
        raise ConfigError("Category names must be non-empty strings.")

    normalized = category.strip()
    if normalized in {".", ".."} or Path(normalized).is_absolute():
        raise ConfigError(f"Invalid category name: {category!r}")
    if "/" in normalized or "\\" in normalized:
        raise ConfigError(f"Category names cannot contain path separators: {category!r}")
    return normalized


def _normalize_extension(extension: object, category: str) -> str:
    if not isinstance(extension, str) or not extension.strip():
        raise ConfigError(f"Extensions for {category!r} must be non-empty strings.")

    normalized = extension.strip().lower()
    if not normalized.startswith("."):
        normalized = f".{normalized}"
    if "/" in normalized or "\\" in normalized or normalized == ".":
        raise ConfigError(f"Invalid extension {extension!r} in category {category!r}.")
    return normalized


def _parse_config(data: object) -> OrganizerConfig:
    if not isinstance(data, dict):
        raise ConfigError("The configuration root must be a TOML table.")

    raw_rules = data.get("rules", DEFAULT_RULES)
    if not isinstance(raw_rules, dict) or not raw_rules:
        raise ConfigError("[rules] must contain at least one category.")

    rules: dict[str, tuple[str, ...]] = {}
    seen_extensions: set[str] = set()
    for raw_category, raw_extensions in raw_rules.items():
        category = _validate_category(raw_category)
        if not isinstance(raw_extensions, list) or not raw_extensions:
            raise ConfigError(f"Rule {category!r} must be a non-empty TOML array.")

        extensions = tuple(_normalize_extension(item, category) for item in raw_extensions)
        duplicates = seen_extensions.intersection(extensions)
        if duplicates:
            duplicate = sorted(duplicates)[0]
            raise ConfigError(f"Extension {duplicate!r} appears in more than one category.")
        seen_extensions.update(extensions)
        rules[category] = extensions

    raw_settings = data.get("settings", {})
    if not isinstance(raw_settings, dict):
        raise ConfigError("[settings] must be a TOML table.")
    uncategorized = _validate_category(raw_settings.get("uncategorized", "Other"))
    if uncategorized in rules:
        raise ConfigError("The uncategorized folder must differ from rule category names.")

    return OrganizerConfig(rules=rules, uncategorized=uncategorized)


def load_config(path: Path | None = None) -> OrganizerConfig:
    """Load an organizer configuration, or return the built-in defaults."""
    if path is None:
        return OrganizerConfig(rules=DEFAULT_RULES.copy())

    try:
        with path.open("rb") as config_file:
            return _parse_config(tomllib.load(config_file))
    except FileNotFoundError as error:
        raise ConfigError(f"Configuration file not found: {path}") from error
    except tomllib.TOMLDecodeError as error:
        raise ConfigError(f"Invalid TOML in {path}: {error}") from error
