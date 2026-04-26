from __future__ import annotations

import shutil
import sqlite3
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

DEFAULT_DB = Path.home() / "Library/Application Support/pcsuite/database/NoteSync.db"
REQUIRED_TABLES = ("NoteBook", "Note")
SNAPSHOT_SUFFIXES = ("", "-wal", "-shm")


@dataclass(frozen=True)
class DatabaseSnapshot:
    """A copied database snapshot and its containing temporary directory."""

    source: Path
    path: Path
    directory: Path
    copied_files: tuple[Path, ...]


def _expanded(path: Path) -> Path:
    return path.expanduser()


def _copy_snapshot_files(db_path: Path, target_dir: Path) -> tuple[Path, ...]:
    copied: list[Path] = []
    for suffix in SNAPSHOT_SUFFIXES:
        source = Path(f"{db_path}{suffix}")
        if source.exists():
            destination = target_dir / source.name
            shutil.copy2(source, destination)
            copied.append(destination)
    return tuple(copied)


@contextmanager
def snapshot_database(db_path: Path, *, keep: bool = False) -> Iterator[DatabaseSnapshot]:
    """Copy a vivo database and sidecars to a temp dir, then clean it up by default."""

    source = _expanded(db_path)
    if not source.exists():
        raise FileNotFoundError(f"database not found: {source}")

    temp_dir = Path(tempfile.mkdtemp(prefix="vivo-note-cli-"))
    snapshot_path = temp_dir / source.name
    try:
        copied = _copy_snapshot_files(source, temp_dir)
        if not snapshot_path.exists():
            raise FileNotFoundError(f"database snapshot was not created for: {source}")
        yield DatabaseSnapshot(
            source=source,
            path=snapshot_path,
            directory=temp_dir,
            copied_files=copied,
        )
    finally:
        if not keep:
            shutil.rmtree(temp_dir, ignore_errors=True)


def connect_readonly(db_path: Path) -> sqlite3.Connection:
    """Open a SQLite database with a read-only URI and query-only pragma."""

    path = _expanded(db_path)
    if not path.exists():
        raise FileNotFoundError(f"database not found: {path}")
    uri = f"{path.resolve().as_uri()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only = ON")
    return conn


@contextmanager
def readonly_connection(
    db_path: Path,
    *,
    use_snapshot: bool = True,
    keep_snapshot: bool = False,
) -> Iterator[sqlite3.Connection]:
    """Open the source DB safely, snapshotting by default."""

    if use_snapshot:
        with (
            snapshot_database(db_path, keep=keep_snapshot) as snapshot,
            connect_readonly(snapshot.path) as conn,
        ):
            yield conn
    else:
        with connect_readonly(db_path) as conn:
            yield conn


def table_names(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
    return {str(row["name"]) for row in rows}


def check_database(
    db_path: Path,
    *,
    use_snapshot: bool = True,
    keep_snapshot: bool = False,
) -> dict[str, object]:
    """Return a content-free health report for a vivo notes database."""

    source = _expanded(db_path)
    report: dict[str, object] = {
        "database": str(source),
        "exists": source.exists(),
        "snapshot": False,
        "readonly_open": False,
        "required_tables": {table: False for table in REQUIRED_TABLES},
        "ok": False,
    }
    if not source.exists():
        report["error"] = "database not found"
        return report

    try:
        if use_snapshot:
            with snapshot_database(source, keep=keep_snapshot) as snapshot:
                report["snapshot"] = True
                if keep_snapshot:
                    report["snapshot_path"] = str(snapshot.directory)
                with connect_readonly(snapshot.path) as conn:
                    report["readonly_open"] = True
                    names = table_names(conn)
        else:
            report["snapshot"] = "skipped"
            with connect_readonly(source) as conn:
                report["readonly_open"] = True
                names = table_names(conn)
    except (OSError, sqlite3.Error) as exc:
        report["error"] = str(exc)
        return report

    table_report = {table: table in names for table in REQUIRED_TABLES}
    report["required_tables"] = table_report
    report["ok"] = all(table_report.values()) and bool(report["readonly_open"])
    return report
