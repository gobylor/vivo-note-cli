from vivo_note_cli.db import connect_readonly
from vivo_note_cli.exporter import ExportFilters, list_notebooks, load_notes
from vivo_note_cli.formatters import JSON_FIELDS, format_json


def test_lists_active_notebooks(sample_db) -> None:
    with connect_readonly(sample_db) as conn:
        notebooks = list_notebooks(conn)
    assert notebooks == [
        {"notebook": "日记", "notes": 2},
        {"notebook": "工作", "notes": 1},
        {"notebook": "空文件夹", "notes": 0},
    ]


def test_exports_notes_with_since_filter_and_origin_fallback(sample_db) -> None:
    with connect_readonly(sample_db) as conn:
        notes = load_notes(
            conn,
            ExportFilters(notebook="日记", since="2026-04-03", since_field="create"),
        )
    assert [note["guid"] for note in notes] == ["guid-diary-2"]
    assert notes[0]["content_markdown"] == "来自 originContent"
    assert notes[0]["stickTop"] == 1


def test_update_since_filter(sample_db) -> None:
    with connect_readonly(sample_db) as conn:
        notes = load_notes(conn, ExportFilters(since="2026-04-06", since_field="update"))
    assert [note["guid"] for note in notes] == ["guid-diary-2"]


def test_default_json_schema_excludes_raw_html(sample_db) -> None:
    with connect_readonly(sample_db) as conn:
        notes = load_notes(conn, ExportFilters(notebook="日记"))
    output = format_json(notes, include_html=False)
    assert "content_html" not in output
    import json

    records = json.loads(output)
    assert tuple(records[0].keys()) == JSON_FIELDS


def test_json_can_include_raw_html_when_requested(sample_db) -> None:
    with connect_readonly(sample_db) as conn:
        notes = load_notes(conn, ExportFilters(notebook="日记"))
    output = format_json(notes, include_html=True)
    assert "content_html" in output
    assert "<p>第一段</p>" in output
