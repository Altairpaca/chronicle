from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal

BsMode = Literal["B", "S"]


@dataclass(frozen=True, slots=True)
class NewEntry:
    title: str
    started_at: str
    ended_at: str
    category: str
    bs_mode: BsMode
    energy: int
    note: str


class LedgerStore:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connection(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    ended_at TEXT NOT NULL,
                    category TEXT NOT NULL,
                    bs_mode TEXT NOT NULL CHECK (bs_mode IN ('B', 'S')),
                    energy INTEGER NOT NULL CHECK (energy BETWEEN 1 AND 5),
                    note TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    planned_date TEXT NOT NULL,
                    target_minutes INTEGER NOT NULL CHECK (target_minutes > 0),
                    category TEXT NOT NULL,
                    completed INTEGER NOT NULL DEFAULT 0 CHECK (completed IN (0, 1))
                );
                """
            )

    def create_entry(
        self,
        title: str,
        started_at: str,
        ended_at: str,
        category: str,
        bs_mode: BsMode,
        energy: int,
        note: str,
    ) -> dict[str, object]:
        entry = NewEntry(title.strip(), started_at, ended_at, category.strip(), bs_mode, energy, note.strip())
        start, end = self._parse_interval(entry)
        with self._connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO entries (title, started_at, ended_at, category, bs_mode, energy, note)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (entry.title, entry.started_at, entry.ended_at, entry.category, entry.bs_mode, entry.energy, entry.note),
            )
            entry_id = cursor.lastrowid
        return self._entry_dict(entry_id, entry, int((end - start).total_seconds() // 60))

    def daily_summary(self, date_value: str) -> dict[str, object]:
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT * FROM entries WHERE substr(started_at, 1, 10) = ? ORDER BY started_at",
                (date_value,),
            ).fetchall()
            plans = connection.execute(
                "SELECT * FROM plans WHERE planned_date = ? ORDER BY completed, id",
                (date_value,),
            ).fetchall()
        entries = [self._row_to_entry(row) for row in rows]
        total = sum(int(item["minutes"]) for item in entries)
        focus = sum(int(item["minutes"]) for item in entries if item["bs_mode"] == "B")
        category_minutes: dict[str, int] = {}
        for item in entries:
            category = str(item["category"])
            category_minutes[category] = category_minutes.get(category, 0) + int(item["minutes"])
        return {
            "date": date_value,
            "entries": entries,
            "plans": [dict(row) for row in plans],
            "total_minutes": total,
            "focus_minutes": focus,
            "category_minutes": category_minutes,
        }

    def create_plan(self, title: str, planned_date: str, target_minutes: int, category: str) -> dict[str, object]:
        cleaned_title = title.strip()
        cleaned_category = category.strip()
        if not cleaned_title or not cleaned_category or target_minutes <= 0:
            raise ValueError("计划需要标题、分类和正数分钟数")
        with self._connection() as connection:
            cursor = connection.execute(
                "INSERT INTO plans (title, planned_date, target_minutes, category) VALUES (?, ?, ?, ?)",
                (cleaned_title, planned_date, target_minutes, cleaned_category),
            )
        return {"id": cursor.lastrowid, "title": cleaned_title, "planned_date": planned_date, "target_minutes": target_minutes, "category": cleaned_category, "completed": 0}

    def _parse_interval(self, entry: NewEntry) -> tuple[datetime, datetime]:
        if not entry.title or not entry.category:
            raise ValueError("记录需要事项和分类")
        if entry.bs_mode not in ("B", "S") or entry.energy not in range(1, 6):
            raise ValueError("B/S 类型或能量等级无效")
        start = datetime.fromisoformat(entry.started_at)
        end = datetime.fromisoformat(entry.ended_at)
        if end <= start:
            raise ValueError("结束时间必须晚于开始时间")
        return start, end

    def _row_to_entry(self, row: sqlite3.Row) -> dict[str, object]:
        entry = NewEntry(row["title"], row["started_at"], row["ended_at"], row["category"], row["bs_mode"], row["energy"], row["note"])
        start, end = self._parse_interval(entry)
        return self._entry_dict(row["id"], entry, int((end - start).total_seconds() // 60))

    def _entry_dict(self, entry_id: int | None, entry: NewEntry, minutes: int) -> dict[str, object]:
        return {"id": entry_id, "title": entry.title, "started_at": entry.started_at, "ended_at": entry.ended_at, "category": entry.category, "bs_mode": entry.bs_mode, "energy": entry.energy, "note": entry.note, "minutes": minutes}
