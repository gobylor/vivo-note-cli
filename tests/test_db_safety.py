from __future__ import annotations

import hashlib

from vivo_note_cli.db import check_database, connect_readonly, snapshot_database


def digest(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_snapshot_cleans_up_by_default(sample_db) -> None:
    with snapshot_database(sample_db) as snapshot:
        snapshot_dir = snapshot.directory
        assert snapshot.path.exists()
        assert snapshot.path != sample_db
    assert not snapshot_dir.exists()


def test_readonly_snapshot_does_not_modify_source(sample_db) -> None:
    before = digest(sample_db)
    with snapshot_database(sample_db) as snapshot, connect_readonly(snapshot.path) as conn:
        conn.execute("SELECT COUNT(*) FROM Note").fetchone()
    after = digest(sample_db)
    assert before == after


def test_doctor_reports_required_tables_without_content(sample_db) -> None:
    report = check_database(sample_db)
    assert report["ok"] is True
    assert report["required_tables"] == {"NoteBook": True, "Note": True}
    assert "guid-diary" not in str(report)
    assert "第一篇" not in str(report)
