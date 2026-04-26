from __future__ import annotations

import json
from collections.abc import Iterable
from datetime import datetime
from typing import Any

from .exporter import JSON_FIELDS


def _record_for_json(note: dict[str, Any], *, include_html: bool) -> dict[str, Any]:
    record = {field: note.get(field) for field in JSON_FIELDS}
    if include_html:
        record["content_html"] = note.get("content_html", "")
    return record


def format_json(notes: Iterable[dict[str, Any]], *, include_html: bool = False) -> str:
    records = [_record_for_json(note, include_html=include_html) for note in notes]
    return json.dumps(records, ensure_ascii=False, indent=2) + "\n"


def format_notebooks_json(notebooks: Iterable[dict[str, Any]]) -> str:
    return json.dumps(list(notebooks), ensure_ascii=False, indent=2) + "\n"


def format_notebooks_table(notebooks: Iterable[dict[str, Any]]) -> str:
    lines = ["notebook\tnotes"]
    lines.extend(f"{row['notebook']}\t{row['notes']}" for row in notebooks)
    return "\n".join(lines) + "\n"


def _clean_metadata(value: Any) -> str:
    return str(value if value is not None else "").replace("\n", " ").strip()


def format_markdown(notes: Iterable[dict[str, Any]], *, include_html: bool = False) -> str:
    note_list = list(notes)
    lines = [
        "# vivo notes export",
        "",
        f"- exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- count: {len(note_list)}",
        "",
    ]
    for note in note_list:
        title = _clean_metadata(note.get("title")) or "Untitled"
        notebook = _clean_metadata(note.get("notebook")) or "未分类"
        lines.extend(
            [
                f"## {notebook} / {title}",
                "",
                f"- vivo_guid: `{_clean_metadata(note.get('guid'))}`",
                f"- vivo_id: `{_clean_metadata(note.get('id'))}`",
                f"- created: {_clean_metadata(note.get('created'))}",
                f"- updated: {_clean_metadata(note.get('updated'))}",
            ]
        )
        if note.get("content_updated"):
            lines.append(f"- content_updated: {_clean_metadata(note.get('content_updated'))}")
        if note.get("contentDigest"):
            lines.append(f"- digest: {_clean_metadata(note.get('contentDigest'))}")
        lines.append("")

        body = note.get("content_markdown") or ""
        if body:
            lines.extend([body, ""])

        if include_html:
            lines.extend(
                [
                    "<details><summary>raw vivo HTML</summary>",
                    "",
                    "```html",
                    str(note.get("content_html") or ""),
                    "```",
                    "",
                    "</details>",
                    "",
                ]
            )
    return "\n".join(lines).rstrip() + "\n"
