from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from vivo_note_cli import cli


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


def test_cli_install_skills_dry_run() -> None:
    result = run_cli("install-skills", "--dry-run")
    assert result.returncode == 0, result.stderr
    assert result.stdout == "npx -y skills add gobylor/vivo-note-cli -g -y\n"


def test_cli_install_skills_project_dry_run_omits_global_flag() -> None:
    result = run_cli("install-skills", "--project", "--dry-run")
    assert result.returncode == 0, result.stderr
    assert result.stdout == "npx -y skills add gobylor/vivo-note-cli -y\n"


def test_cli_install_skills_repeats_agent_flags() -> None:
    result = run_cli(
        "install-skills",
        "--agent",
        "codex",
        "--agent",
        "claude-code",
        "--dry-run",
    )
    assert result.returncode == 0, result.stderr
    assert (
        result.stdout
        == "npx -y skills add gobylor/vivo-note-cli --agent codex --agent claude-code -g -y\n"
    )


def test_cli_install_skills_runs_without_shell(monkeypatch) -> None:
    calls: list[dict[str, object]] = []

    def fake_run(cmd: list[str], *, check: bool, shell: bool) -> subprocess.CompletedProcess[str]:
        calls.append({"cmd": cmd, "check": check, "shell": shell})
        return subprocess.CompletedProcess(cmd, 7)

    monkeypatch.setattr(cli.subprocess, "run", fake_run)

    assert cli.main(["install-skills", "--source", ".", "--project"]) == 7
    assert calls == [
        {
            "cmd": ["npx", "-y", "skills", "add", ".", "-y"],
            "check": False,
            "shell": False,
        }
    ]


def test_cli_install_skills_missing_npx_prints_manual_fallback(monkeypatch, capsys) -> None:
    def fake_run(cmd: list[str], *, check: bool, shell: bool) -> subprocess.CompletedProcess[str]:
        raise FileNotFoundError("npx")

    monkeypatch.setattr(cli.subprocess, "run", fake_run)

    assert cli.main(["install-skills"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "npx was not found" in captured.err
    assert "npx -y skills add gobylor/vivo-note-cli -g -y" in captured.err
