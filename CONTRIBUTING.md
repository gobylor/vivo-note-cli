# Contributing

Thanks for helping improve `vivo-note-cli`.

## Development setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

## Checks

Run these before opening a pull request:

```bash
ruff check .
ruff format --check .
pytest
python -m build
```

## Privacy rules

- Do not upload real `NoteSync.db` files, exported JSON/Markdown, screenshots of private notes, or raw note content.
- Use synthetic SQLite fixtures in tests.
- If a bug requires a real schema detail, share only table/column names and redact values.

## Pull requests

Please describe:

- what changed;
- how it was tested;
- whether the change affects privacy, filesystem writes, or output schema compatibility.
