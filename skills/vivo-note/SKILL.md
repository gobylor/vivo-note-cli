---
name: vivo-note
description: Safely inspect and export vivo Office / Atomic Notes from the local NoteSync.db using the vivo-note CLI.
requires:
  bins: ["vivo-note"]
cliHelp: "vivo-note --help"
---

# vivo-note

Use `vivo-note` to safely inspect and export vivo Office / Atomic Notes (`vivo 办公笔记` / `原子笔记`) from the desktop `NoteSync.db` SQLite database.

## Safety first

- Start with `vivo-note doctor` to verify the database is readable and has the expected tables without exporting note content.
- Prefer the default snapshot behavior. Do **not** add `--no-snapshot` unless the user explicitly asks to read the live database path directly.
- Treat exported notes, JSON, Markdown, snapshots, and raw HTML as private user data.
- Do not commit, upload, paste, or display private note content unless the user explicitly asks for that specific content to be shown or shared.
- Do not write to the original vivo database. `vivo-note` is a read-only exporter.

## Common workflow

1. Check database health:

   ```bash
   vivo-note doctor
   ```

2. List notebooks without exposing note bodies:

   ```bash
   vivo-note list --json
   ```

3. Export notes to a user-approved local path:

   ```bash
   vivo-note export --format json --output /path/to/vivo-notes.json
   vivo-note export --format markdown --output /path/to/vivo-notes.md
   ```

4. Narrow exports when possible:

   ```bash
   vivo-note export --notebook 日记 --format markdown --output /path/to/diary.md
   vivo-note export --since 2026-04-01 --since-field update --format json --output /path/to/recent.json
   ```

## Raw HTML

`content_html` is omitted by default. Add `--include-html` only when the user clearly needs vivo's raw HTML representation, for example for debugging conversion fidelity or preserving original markup.

```bash
vivo-note export --format json --include-html --output /path/to/vivo-notes-with-html.json
```

## Privacy guardrails for agents

- Prefer summaries, counts, filenames, and notebook names over full note bodies.
- Before showing note text in chat, confirm that the user requested that content.
- Never include exported note files, `NoteSync.db` snapshots, or private note content in commits or public artifacts.
