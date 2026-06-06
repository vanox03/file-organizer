# File Organizer

A small, safe, open-source CLI that sorts files into category folders.

File Organizer is deliberately conservative: it organizes one directory, ignores
subdirectories unless asked to recurse, skips hidden files, and never silently
overwrites an existing file.

## Requirements

- Python 3.11 or newer

## Install

Clone the repository and install it locally:

```bash
git clone https://github.com/vanox03/file-organizer.git
cd file-organizer
python -m pip install .
```

For development:

```bash
python -m pip install -e ".[dev]"
```

## Usage

Preview the default organization of the current directory:

```bash
file-organizer organize --dry-run
```

Organize a selected directory:

```bash
file-organizer organize ~/Downloads
```

Include files inside subdirectories:

```bash
file-organizer organize ~/Downloads --recursive
```

Use custom rules:

```bash
file-organizer organize ~/Downloads --config examples/organizer.toml --dry-run
```

The built-in categories are `Images`, `Documents`, `Audio`, `Video`, `Archives`,
and `Other`.

## Custom Rules

Rules use TOML. Extensions may be written with or without a leading dot.

```toml
[rules]
Pictures = ["jpg", "jpeg", "png"]
Writing = ["md", "pdf", "txt"]

[settings]
uncategorized = "Misc"
```

See [`examples/organizer.toml`](examples/organizer.toml) for a complete example.

## Safety Guarantees

- `--dry-run` previews actions without changing files.
- Existing destination files are never overwritten.
- Name collisions become `filename (1).ext`, `filename (2).ext`, and so on.
- Hidden files and files already inside category folders are skipped.
- Invalid configurations stop the command before any file is moved.

Always review a dry run before organizing important directories.

## Contributing

Contributions are welcome. Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before
opening a pull request.

Contributors:

- [vanox03](https://github.com/vanox03)
- [divano-oss](https://github.com/divano-oss)
- [adrem-oxx](https://github.com/adrem-oxx)

## License

Licensed under the [MIT License](LICENSE).
