from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from pathlib import Path

from . import __version__
from .db import DEFAULT_DB, check_database, connect_readonly, snapshot_database
from .exporter import DatabaseSchemaError, ExportFilters, list_notebooks, load_notes
from .formatters import (
    format_json,
    format_markdown,
    format_notebooks_json,
    format_notebooks_table,
)


@contextmanager
def _open_for_cli(args: argparse.Namespace) -> Iterator[sqlite3.Connection]:
    db_path = args.db.expanduser()
    if args.no_snapshot:
        with connect_readonly(db_path) as conn:
            yield conn
        return

    with snapshot_database(db_path, keep=args.keep_snapshot) as snapshot:
        if args.keep_snapshot:
            print(f"snapshot: {snapshot.directory}", file=sys.stderr)
        with connect_readonly(snapshot.path) as conn:
            yield conn


def _add_db_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB,
        help=f"NoteSync.db path (default: {DEFAULT_DB})",
    )
    parser.add_argument(
        "--no-snapshot",
        action="store_true",
        help="read the database path directly in read-only mode instead of copying a snapshot",
    )
    parser.add_argument(
        "--keep-snapshot",
        action="store_true",
        help="keep the temporary database snapshot and print its path to stderr",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vivo-note",
        description="Safely export vivo Office / Atomic Notes from NoteSync.db",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="list active notebooks and note counts")
    _add_db_args(list_parser)
    list_parser.add_argument("--json", action="store_true", help="emit JSON instead of a table")
    list_parser.set_defaults(handler=run_list)

    export_parser = subparsers.add_parser("export", help="export active notes")
    _add_db_args(export_parser)
    export_parser.add_argument(
        "--notebook",
        help="filter by notebook name, e.g. 日记 / 追剧 / 未分类",
    )
    export_parser.add_argument("--since", help="filter notes since YYYY-MM-DD")
    export_parser.add_argument(
        "--since-field",
        choices=("create", "update"),
        default="update",
        help="date field used by --since (default: update)",
    )
    export_parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="json",
        help="export format (default: json)",
    )
    export_parser.add_argument(
        "--include-html",
        action="store_true",
        help="include raw vivo HTML in output",
    )
    export_parser.add_argument(
        "--output",
        type=Path,
        help="write output to a file instead of stdout",
    )
    export_parser.set_defaults(handler=run_export)

    doctor_parser = subparsers.add_parser(
        "doctor",
        help="check database readability and required tables without exporting notes",
    )
    _add_db_args(doctor_parser)
    doctor_parser.add_argument("--json", action="store_true", help="emit JSON health report")
    doctor_parser.set_defaults(handler=run_doctor)
    return parser


def run_list(args: argparse.Namespace) -> int:
    with _open_for_cli(args) as conn:
        notebooks = list_notebooks(conn)
    output = format_notebooks_json(notebooks) if args.json else format_notebooks_table(notebooks)
    sys.stdout.write(output)
    return 0


def _write_output(text: str, output: Path | None) -> None:
    if output is None:
        sys.stdout.write(text)
        return
    output = output.expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")


def run_export(args: argparse.Namespace) -> int:
    filters = ExportFilters(
        notebook=args.notebook,
        since=args.since,
        since_field=args.since_field,
    )
    with _open_for_cli(args) as conn:
        notes = load_notes(conn, filters)
    if args.format == "json":
        text = format_json(notes, include_html=args.include_html)
    else:
        text = format_markdown(notes, include_html=args.include_html)
    _write_output(text, args.output)
    return 0


def _format_doctor_table(report: dict[str, object]) -> str:
    required = report.get("required_tables", {})
    lines = [
        f"database: {report.get('database')}",
        f"exists: {'ok' if report.get('exists') else 'missing'}",
        f"snapshot: {report.get('snapshot')}",
        f"readonly_open: {'ok' if report.get('readonly_open') else 'failed'}",
        "required_tables:",
    ]
    if isinstance(required, dict):
        for table, ok in required.items():
            lines.append(f"  {table}: {'ok' if ok else 'missing'}")
    if report.get("error"):
        lines.append(f"error: {report['error']}")
    lines.append(f"result: {'ok' if report.get('ok') else 'failed'}")
    return "\n".join(lines) + "\n"


def run_doctor(args: argparse.Namespace) -> int:
    report = check_database(
        args.db,
        use_snapshot=not args.no_snapshot,
        keep_snapshot=args.keep_snapshot,
    )
    if args.json:
        sys.stdout.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    else:
        sys.stdout.write(_format_doctor_table(report))
    return 0 if report.get("ok") else 1


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except (DatabaseSchemaError, FileNotFoundError, OSError, sqlite3.Error, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
