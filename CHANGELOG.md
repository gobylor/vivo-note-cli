# Changelog

All notable changes to this project will be documented in this file.

## [0.1.1] - 2026-04-26

### Added

- Added `vivo-note install-skills` to install the project AI-agent Skill via the `skills` CLI.
- Added the `vivo-note` Skill with safe doctor/list/export guidance for LLM agents.

### Changed

- Updated installation and release documentation for the explicit Skill installation flow.

## [0.1.0] - 2026-04-26

### Added

- Initial `vivo-note` CLI with `list`, `export`, and `doctor` subcommands.
- Safe snapshot-based read path for `NoteSync.db`, `-wal`, and `-shm` files.
- Read-only SQLite connection with query-only mode.
- JSON and Markdown exporters for active notes.
- Dependency-free vivo HTML to Markdown conversion.
- Tests, GitHub Actions CI, release artifact workflow, and open-source community files.
