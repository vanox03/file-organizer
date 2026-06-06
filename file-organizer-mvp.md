# File Organizer MVP

## Goal
Build a safe, cross-platform Python CLI that organizes files in a selected directory using configurable rules, previews every action, and never overwrites files silently.

## Technical Direction
- Python 3.11+ with `pathlib`, packaged through `pyproject.toml`.
- CLI powered by `argparse` to keep runtime dependencies at zero.
- Rules stored in a human-readable TOML configuration file.
- Planning and filesystem execution kept separate so dry runs and tests use the same decisions.

## Tasks
- [ ] Define the MVP behavior in `README.md`: organize one directory, ignore subdirectories by default, categorize by extension, preview with `--dry-run`, and resolve name collisions safely. -> Verify: README includes examples and explicit safety guarantees.
- [ ] Create the Python package and CLI entry point in `src/file_organizer/`, with `organize`, `--dry-run`, `--config`, and `--recursive` options. -> Verify: `file-organizer --help` exits successfully and lists every option.
- [ ] Implement TOML rule loading with useful defaults for images, documents, audio, video, archives, and uncategorized files. -> Verify: valid rules load correctly and malformed rules produce a clear error without moving files.
- [ ] Implement a planner that scans the target directory and returns source/destination actions without changing the filesystem. -> Verify: planner tests cover known extensions, unknown extensions, hidden files, and optional recursion.
- [ ] Implement safe action execution that creates category folders, skips already-organized files, and adds a numeric suffix on collisions. -> Verify: integration tests confirm files are moved correctly and existing files are never overwritten.
- [ ] Add project essentials: `.gitignore`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, issue templates, and concise contributor credits. -> Verify: contributor instructions explain setup, testing, and pull-request expectations.
- [ ] Add GitHub Actions for Python 3.11, 3.12, and 3.13 running formatting checks and `pytest`. -> Verify: the workflow passes on all supported Python versions.
- [ ] Run final verification on temporary sample directories for dry-run, normal organization, recursion, malformed config, and collision handling. -> Verify: automated tests pass and manual dry-run output matches the resulting moves.

## Done When
- [ ] A new user can install the project, preview an organization, and organize a directory using only the README.
- [ ] No default operation deletes data, overwrites a file, or moves anything before an explicit organize command.
- [ ] The full test suite and GitHub Actions workflow pass.

## Notes
- Keep the MVP focused on a local CLI; a GUI, background watcher, undo history, duplicate detection, and date-based rules belong in later milestones.
- Future commits can credit collaborators with valid `Co-authored-by:` trailers when they have contributed to the corresponding changes; the pull-request description can also acknowledge `vanox03`, `divano-oss`, and `adrem-oxx`.
