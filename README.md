# vivo-note-cli

`vivo-note-cli` is a small, dependency-free command line exporter for vivo Office / Atomic Notes (`vivo 办公笔记` / `原子笔记`) desktop `NoteSync.db` files.

It is designed for safe local use:

- snapshots `NoteSync.db` plus `-wal` / `-shm` sidecar files before reading;
- opens the copied database with a read-only SQLite URI;
- exports active notes to JSON or Markdown;
- omits raw vivo HTML unless you explicitly pass `--include-html`;
- never writes to the original vivo database.

> [!WARNING]
> Your notes may contain private content. Do not commit exported JSON/Markdown, database snapshots, or raw private note text to a public repository.

## Install

Install from PyPI with `uv`:

```bash
uv tool install vivo-note-cli
vivo-note install-skills
```

`vivo-note install-skills` installs the project AI-agent Skill globally so tools
such as Codex, Claude Code, and Cursor can discover the safe `vivo-note`
workflow. Restart your AI agent after installing the Skill so it reloads the new
instructions.

Upgrade or remove the CLI:

```bash
uv tool upgrade vivo-note-cli
uv tool uninstall vivo-note-cli
```

Manual Skill installation fallback:

```bash
npx -y skills add gobylor/vivo-note-cli -g -y
```

## Quick start

The default database path is:

```text
~/Library/Application Support/pcsuite/database/NoteSync.db
```

List notebooks:

```bash
vivo-note list
vivo-note list --json
```

Export all active notes as JSON:

```bash
vivo-note export --format json --output /tmp/vivo-notes.json
```

Export one notebook as Markdown:

```bash
vivo-note export --notebook 日记 --format markdown --output /tmp/vivo-diary.md
```

Export notes updated since a date:

```bash
vivo-note export --since 2026-04-01 --since-field update --format json
```

Check whether a database can be read safely without exporting note content:

```bash
vivo-note doctor
```

## JSON output

Default JSON records keep these stable fields:

```text
id, guid, notebook, title, contentDigest, created, updated, content_updated,
type, stickTop, content_markdown
```

`content_html` is only emitted when `--include-html` is passed.

## 中文快速开始

`vivo-note-cli` 用于只读导出 vivo 办公笔记 / 原子笔记桌面端的 `NoteSync.db`。默认会先把数据库复制到临时目录，再用 SQLite 只读模式打开，不会写原始数据库。

```bash
# 查看笔记文件夹
vivo-note list --json

# 导出「日记」文件夹为 Markdown
vivo-note export --notebook 日记 --format markdown --output /tmp/vivo-diary.md

# 诊断数据库是否可读（不会导出正文）
vivo-note doctor
```

请不要把 `/tmp/vivo-*.json`、导出的 Markdown、`NoteSync.db` 快照或任何私人笔记内容提交到公开仓库。

## Scope

Version 0.1 focuses on read-only export. It intentionally does **not** copy attachments, write to Obsidian, or perform bidirectional sync. See [docs/obsidian-recipe.md](docs/obsidian-recipe.md) for an optional import recipe you can adapt outside this package.

## Documentation

- [Known database shape](docs/database.md)
- [Obsidian import recipe](docs/obsidian-recipe.md)
- [Release process](docs/releasing.md)

## License

MIT
