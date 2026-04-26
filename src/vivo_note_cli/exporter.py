from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal

from .html_md import html_to_markdown

UNCATEGORIZED = "未分类"
JSON_FIELDS = (
    "id",
    "guid",
    "notebook",
    "title",
    "contentDigest",
    "created",
    "updated",
    "content_updated",
    "type",
    "stickTop",
    "content_markdown",
)
SinceField = Literal["create", "update"]


class DatabaseSchemaError(RuntimeError):
    """Raised when the database does not look like a supported vivo NoteSync.db."""


@dataclass(frozen=True)
class ExportFilters:
    notebook: str | None = None
    since: str | None = None
    since_field: SinceField = "update"


def ms_to_local(value: Any) -> str:
    if value in (None, ""):
        return ""
    try:
        timestamp = int(value)
    except (TypeError, ValueError):
        return ""
    if timestamp <= 0:
        return ""
    seconds = timestamp if timestamp < 10_000_000_000 else timestamp / 1000
    return datetime.fromtimestamp(seconds).strftime("%Y-%m-%d %H:%M:%S")


def date_to_ms(date_text: str) -> int:
    try:
        return int(datetime.strptime(date_text, "%Y-%m-%d").timestamp() * 1000)
    except ValueError as exc:
        raise ValueError(f"invalid date {date_text!r}; expected YYYY-MM-DD") from exc


def table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {str(row["name"] if isinstance(row, sqlite3.Row) else row[1]) for row in rows}


def _require_columns(columns: set[str], table: str, required: set[str]) -> None:
    missing = sorted(required - columns)
    if missing:
        joined = ", ".join(missing)
        raise DatabaseSchemaError(f"{table} table is missing required column(s): {joined}")


def _active_condition(alias: str, columns: set[str]) -> str:
    return f"{alias}.deleted = 1" if "deleted" in columns else "1 = 1"


def _note_expr(
    columns: set[str],
    column: str,
    *,
    alias: str | None = None,
    default: str = "NULL",
) -> str:
    output = alias or column
    if column in columns:
        return f"n.{column} AS {output}"
    return f"{default} AS {output}"


def _content_expr(note_columns: set[str]) -> str:
    parts: list[str] = []
    if "contentNote" in note_columns:
        parts.append("NULLIF(n.contentNote, '')")
    if "originContent" in note_columns:
        parts.append("n.originContent")
    if not parts:
        return "'' AS content_html"
    return f"COALESCE({', '.join(parts)}, '') AS content_html"


def _count_expr(note_columns: set[str]) -> str:
    return "COUNT(n.id)" if "id" in note_columns else "COUNT(n.rowid)"


def list_notebooks(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    note_columns = table_columns(conn, "Note")
    notebook_columns = table_columns(conn, "NoteBook")
    _require_columns(note_columns, "Note", {"guid", "noteBookGuid"})
    _require_columns(notebook_columns, "NoteBook", {"guid", "name"})

    note_active = _active_condition("n", note_columns)
    notebook_active = _active_condition("nb", notebook_columns)
    sort_expr = "nb.sort" if "sort" in notebook_columns else "NULL"
    note_count = _count_expr(note_columns)

    rows = conn.execute(
        f"""
        SELECT nb.name AS notebook,
               {note_count} AS notes,
               {sort_expr} AS sort_order
        FROM NoteBook nb
        LEFT JOIN Note n ON n.noteBookGuid = nb.guid AND {note_active}
        WHERE {notebook_active}
        GROUP BY nb.guid, nb.name, sort_order
        ORDER BY sort_order IS NULL, sort_order, nb.name
        """
    ).fetchall()

    notebooks = [
        {"notebook": row["notebook"] or UNCATEGORIZED, "notes": int(row["notes"])} for row in rows
    ]

    unclassified = conn.execute(
        f"""
        SELECT {note_count} AS notes
        FROM Note n
        LEFT JOIN NoteBook nb ON n.noteBookGuid = nb.guid AND {notebook_active}
        WHERE {note_active} AND nb.guid IS NULL
        """
    ).fetchone()
    unclassified_count = int(unclassified["notes"] if unclassified else 0)
    if unclassified_count:
        notebooks.append({"notebook": UNCATEGORIZED, "notes": unclassified_count})
    return notebooks


def load_notes(
    conn: sqlite3.Connection,
    filters: ExportFilters | None = None,
) -> list[dict[str, Any]]:
    filters = filters or ExportFilters()
    note_columns = table_columns(conn, "Note")
    notebook_columns = table_columns(conn, "NoteBook")
    _require_columns(note_columns, "Note", {"guid", "noteBookGuid"})
    _require_columns(notebook_columns, "NoteBook", {"guid", "name"})

    note_active = _active_condition("n", note_columns)
    notebook_active = _active_condition("nb", notebook_columns)
    where = [note_active]
    params: list[Any] = []

    if filters.notebook:
        if filters.notebook == UNCATEGORIZED:
            where.append("nb.name IS NULL")
        else:
            where.append("nb.name = ?")
            params.append(filters.notebook)

    if filters.since:
        column = "updateTime" if filters.since_field == "update" else "createTime"
        if column not in note_columns:
            raise DatabaseSchemaError(f"Note table is missing required date column: {column}")
        where.append(f"n.{column} >= ?")
        params.append(date_to_ms(filters.since))

    id_expr = "n.id AS id" if "id" in note_columns else "n.rowid AS id"
    create_expr = _note_expr(note_columns, "createTime", alias="created_ms")
    update_expr = _note_expr(note_columns, "updateTime", alias="updated_ms")
    content_update_expr = _note_expr(
        note_columns,
        "contentUpdateTime",
        alias="content_updated_ms",
    )
    order_expr = "n.createTime" if "createTime" in note_columns else "n.rowid"

    sql = f"""
        SELECT {id_expr},
               n.guid AS guid,
               COALESCE(nb.name, '{UNCATEGORIZED}') AS notebook,
               {_note_expr(note_columns, "title", default="''")},
               {_note_expr(note_columns, "contentDigest", default="''")},
               {create_expr},
               {update_expr},
               {content_update_expr},
               {_note_expr(note_columns, "type")},
               {_note_expr(note_columns, "stickTop")},
               {_content_expr(note_columns)}
        FROM Note n
        LEFT JOIN NoteBook nb ON nb.guid = n.noteBookGuid AND {notebook_active}
        WHERE {" AND ".join(where)}
        ORDER BY {order_expr} ASC, id ASC
    """

    records: list[dict[str, Any]] = []
    for row in conn.execute(sql, params):
        content_html = row["content_html"] or ""
        record = {
            "id": row["id"],
            "guid": row["guid"],
            "notebook": row["notebook"] or UNCATEGORIZED,
            "title": row["title"] or "",
            "contentDigest": row["contentDigest"] or "",
            "created": ms_to_local(row["created_ms"]),
            "updated": ms_to_local(row["updated_ms"]),
            "content_updated": ms_to_local(row["content_updated_ms"]),
            "type": row["type"],
            "stickTop": row["stickTop"],
            "content_markdown": html_to_markdown(content_html),
            "content_html": content_html,
        }
        records.append(record)
    return records
