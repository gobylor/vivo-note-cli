from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

import pytest


def ms(value: str) -> int:
    return int(datetime.strptime(value, "%Y-%m-%d %H:%M:%S").timestamp() * 1000)


@pytest.fixture
def sample_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "NoteSync.db"
    with sqlite3.connect(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE NoteBook (
                id INTEGER PRIMARY KEY,
                guid TEXT,
                name TEXT,
                sort INTEGER,
                deleted INTEGER
            );
            CREATE TABLE Note (
                id INTEGER PRIMARY KEY,
                guid TEXT,
                noteBookGuid TEXT,
                title TEXT,
                contentNote TEXT,
                originContent TEXT,
                contentDigest TEXT,
                createTime INTEGER,
                updateTime INTEGER,
                contentUpdateTime INTEGER,
                type INTEGER,
                stickTop INTEGER,
                deleted INTEGER
            );
            """
        )
        conn.executemany(
            "INSERT INTO NoteBook (id, guid, name, sort, deleted) VALUES (?, ?, ?, ?, ?)",
            [
                (1, "nb-diary", "日记", 1, 1),
                (2, "nb-work", "工作", 2, 1),
                (3, "nb-empty", "空文件夹", 3, 1),
                (4, "nb-deleted", "已删除", 4, 0),
            ],
        )
        conn.executemany(
            """
            INSERT INTO Note (
                id, guid, noteBookGuid, title, contentNote, originContent, contentDigest,
                createTime, updateTime, contentUpdateTime, type, stickTop, deleted
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    1,
                    "guid-diary-1",
                    "nb-diary",
                    "第一篇",
                    "<p>第一段</p><p>第二段</p>",
                    "<p>origin ignored</p>",
                    "摘要一",
                    ms("2026-04-01 08:00:00"),
                    ms("2026-04-02 09:00:00"),
                    ms("2026-04-02 09:30:00"),
                    0,
                    0,
                    1,
                ),
                (
                    2,
                    "guid-diary-2",
                    "nb-diary",
                    "fallback",
                    "",
                    "<p>来自 originContent</p>",
                    "摘要二",
                    ms("2026-04-05 08:00:00"),
                    ms("2026-04-06 09:00:00"),
                    ms("2026-04-06 09:30:00"),
                    0,
                    1,
                    1,
                ),
                (
                    3,
                    "guid-work-1",
                    "nb-work",
                    "工作记录",
                    "<ul><li>任务 A</li><li>任务 B</li></ul>",
                    "",
                    "工作摘要",
                    ms("2026-03-01 10:00:00"),
                    ms("2026-03-02 10:00:00"),
                    None,
                    1,
                    0,
                    1,
                ),
                (
                    4,
                    "guid-hidden",
                    "nb-diary",
                    "hidden",
                    "<p>should not export</p>",
                    "",
                    "",
                    ms("2026-04-07 10:00:00"),
                    ms("2026-04-07 10:00:00"),
                    None,
                    0,
                    0,
                    0,
                ),
            ],
        )
    return db_path
