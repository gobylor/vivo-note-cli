from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "vivo_note_cli.cli", *args],
        check=False,
        capture_output=True,
        text=True,
    )


def test_cli_list_json(sample_db: Path) -> None:
    result = run_cli("list", "--db", str(sample_db), "--json")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)[0] == {"notebook": "日记", "notes": 2}


def test_cli_export_json_default_excludes_html(sample_db: Path) -> None:
    result = run_cli("export", "--db", str(sample_db), "--notebook", "日记", "--format", "json")
    assert result.returncode == 0, result.stderr
    records = json.loads(result.stdout)
    assert len(records) == 2
    assert "content_html" not in records[0]
    assert records[0]["content_markdown"] == "第一段\n\n第二段"


def test_cli_export_markdown_to_file(sample_db: Path, tmp_path: Path) -> None:
    output = tmp_path / "export.md"
    result = run_cli(
        "export",
        "--db",
        str(sample_db),
        "--notebook",
        "工作",
        "--format",
        "markdown",
        "--output",
        str(output),
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == ""
    text = output.read_text(encoding="utf-8")
    assert "## 工作 / 工作记录" in text
    assert "- 任务 A" in text


def test_cli_doctor(sample_db: Path) -> None:
    result = run_cli("doctor", "--db", str(sample_db))
    assert result.returncode == 0, result.stderr
    assert "result: ok" in result.stdout
    assert "第一篇" not in result.stdout


def test_cli_doctor_json(sample_db: Path) -> None:
    result = run_cli("doctor", "--db", str(sample_db), "--json")
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["ok"] is True
    assert report["required_tables"] == {"NoteBook": True, "Note": True}
