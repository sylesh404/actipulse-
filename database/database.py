"""SQLite persistence layer for ActiPulse AI.

Provides connection management, schema initialization, and CRUD operations
for recorded physical activities without embedding UI logic.
"""

from __future__ import annotations

import logging
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = Path("data") / "actipulse.db"

ACTIVITY_RECORD_COLUMNS = [
    "id",
    "activity_date",
    "start_time",
    "end_time",
    "activity_label",
    "duration_minutes",
    "created_at",
]


def get_database_path() -> Path:
    """Resolve the SQLite database path from environment configuration."""
    configured = os.getenv("DATABASE_PATH", "").strip()
    return Path(configured) if configured else DEFAULT_DB_PATH


class DatabaseManager:
    """Lightweight SQLite manager for activity logs, narratives, and exports."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path = Path(db_path) if db_path is not None else get_database_path()

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        """Yield a configured SQLite connection with foreign keys enabled."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path), detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA foreign_keys = ON;")
            yield conn
            conn.commit()
        except sqlite3.Error as exc:
            conn.rollback()
            logger.exception("SQLite operation failed: %s", exc)
            raise
        finally:
            conn.close()

    def initialize_schema(self) -> None:
        """Create foundational tables and indexes if they do not already exist."""
        schema_sql = """
        CREATE TABLE IF NOT EXISTS upload_batches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            file_format TEXT NOT NULL,
            row_count INTEGER NOT NULL DEFAULT 0,
            uploaded_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS activity_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id INTEGER,
            activity_date TEXT NOT NULL,
            start_time TEXT,
            end_time TEXT,
            activity_label TEXT NOT NULL,
            duration_minutes REAL NOT NULL CHECK (duration_minutes > 0),
            notes TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (batch_id) REFERENCES upload_batches(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_activity_records_date
            ON activity_records(activity_date);

        CREATE INDEX IF NOT EXISTS idx_activity_records_label
            ON activity_records(activity_label);

        CREATE UNIQUE INDEX IF NOT EXISTS idx_activity_unique_entry
            ON activity_records(activity_date, start_time, end_time, activity_label);

        CREATE TABLE IF NOT EXISTS daily_narratives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_date TEXT NOT NULL UNIQUE,
            narrative_text TEXT NOT NULL,
            model_name TEXT,
            generated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS report_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_name TEXT NOT NULL,
            report_format TEXT NOT NULL,
            date_range_start TEXT,
            date_range_end TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        """
        with self.connect() as conn:
            conn.executescript(schema_sql)

    def get_table_counts(self) -> dict[str, int]:
        """Return row counts for core tables to support diagnostics and status views."""
        tables = ("upload_batches", "activity_records", "daily_narratives", "report_history")
        counts: dict[str, int] = {}
        with self.connect() as conn:
            for table in tables:
                row = conn.execute(f"SELECT COUNT(*) AS cnt FROM {table};").fetchone()
                counts[table] = int(row["cnt"]) if row else 0
        return counts

    def get_existing_record_keys(self) -> set[tuple[str, str, str, str]]:
        """Return canonical deduplication keys (date, start, end, lower_label) currently stored."""
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT activity_date, COALESCE(start_time, ''), COALESCE(end_time, ''), activity_label
                FROM activity_records;
                """
            ).fetchall()
        return {
            (
                str(row[0]),
                str(row[1]),
                str(row[2]),
                str(row[3]).strip().lower(),
            )
            for row in rows
        }

    def insert_upload_batch(self, filename: str, file_format: str, row_count: int) -> int:
        """Record an imported file batch and return its database ID."""
        with self.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO upload_batches (filename, file_format, row_count)
                VALUES (?, ?, ?);
                """,
                (filename, file_format, int(row_count)),
            )
            return int(cursor.lastrowid)

    def insert_activity_record(
        self,
        activity_date: str,
        start_time: str,
        end_time: str,
        activity_label: str,
        duration_minutes: float,
        notes: str | None = None,
        batch_id: int | None = None,
    ) -> bool:
        """Insert a single activity record, returning False if it duplicates an existing entry."""
        inserted, _ = self.insert_activity_records(
            [
                {
                    "activity_date": activity_date,
                    "start_time": start_time,
                    "end_time": end_time,
                    "activity_label": activity_label,
                    "duration_minutes": duration_minutes,
                    "notes": notes,
                }
            ],
            batch_id=batch_id,
        )
        return inserted == 1

    def insert_activity_records(
        self,
        records: list[dict[str, Any]],
        batch_id: int | None = None,
    ) -> tuple[int, int]:
        """Bulk insert validated activity records while preventing duplicate entries.

        Returns:
            A tuple of (inserted_count, duplicate_count).
        """
        if not records:
            return 0, 0

        existing_keys = self.get_existing_record_keys()
        to_insert: list[tuple[Any, ...]] = []
        duplicate_count = 0

        for rec in records:
            key = (
                str(rec["activity_date"]),
                str(rec["start_time"]),
                str(rec["end_time"]),
                str(rec["activity_label"]).strip().lower(),
            )
            if key in existing_keys:
                duplicate_count += 1
                continue
            existing_keys.add(key)
            to_insert.append(
                (
                    batch_id,
                    str(rec["activity_date"]),
                    str(rec["start_time"]),
                    str(rec["end_time"]),
                    str(rec["activity_label"]).strip(),
                    float(rec["duration_minutes"]),
                    rec.get("notes"),
                )
            )

        if not to_insert:
            return 0, duplicate_count

        with self.connect() as conn:
            conn.executemany(
                """
                INSERT INTO activity_records (
                    batch_id,
                    activity_date,
                    start_time,
                    end_time,
                    activity_label,
                    duration_minutes,
                    notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                to_insert,
            )

        return len(to_insert), duplicate_count

    def get_all_activity_records(self) -> pd.DataFrame:
        """Retrieve all stored activity records ordered with most recent entries first."""
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    id,
                    activity_date,
                    start_time,
                    end_time,
                    activity_label,
                    duration_minutes,
                    created_at
                FROM activity_records
                ORDER BY activity_date DESC, start_time DESC, id DESC;
                """
            ).fetchall()

        if not rows:
            return pd.DataFrame(columns=ACTIVITY_RECORD_COLUMNS)

        return pd.DataFrame([dict(row) for row in rows], columns=ACTIVITY_RECORD_COLUMNS)

    def get_records_by_date(self, activity_date: str) -> pd.DataFrame:
        """Retrieve all stored activity records for a specific YYYY-MM-DD date."""
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    id,
                    activity_date,
                    start_time,
                    end_time,
                    activity_label,
                    duration_minutes,
                    created_at
                FROM activity_records
                WHERE activity_date = ?
                ORDER BY start_time ASC, id ASC;
                """,
                (activity_date,),
            ).fetchall()

        if not rows:
            return pd.DataFrame(columns=ACTIVITY_RECORD_COLUMNS)

        return pd.DataFrame([dict(row) for row in rows], columns=ACTIVITY_RECORD_COLUMNS)

    def delete_activity_record(self, record_id: int) -> bool:
        """Delete a single activity record by ID. Returns True if a row was deleted."""
        with self.connect() as conn:
            cursor = conn.execute(
                "DELETE FROM activity_records WHERE id = ?;",
                (int(record_id),),
            )
            return cursor.rowcount > 0

    def clear_all_activity_records(self) -> int:
        """Delete all activity records and upload batches. Returns deleted record count."""
        with self.connect() as conn:
            cursor = conn.execute("DELETE FROM activity_records;")
            conn.execute("DELETE FROM upload_batches;")
            return int(cursor.rowcount)

    def get_last_updated_timestamp(self) -> str | None:
        """Return the most recent created_at timestamp across activity records, or None."""
        with self.connect() as conn:
            row = conn.execute(
                "SELECT MAX(created_at) AS last_updated FROM activity_records;"
            ).fetchone()
        if row and row["last_updated"]:
            return str(row["last_updated"])
        return None

    def get_ai_narratives_for_period(self, start_date: str, end_date: str) -> list[dict[str, str]]:
        """Retrieve AI-generated narratives for a date range."""
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT activity_date, narrative_text, model_name, generated_at
                FROM daily_narratives
                WHERE activity_date BETWEEN ? AND ?
                ORDER BY activity_date DESC;
                """,
                (start_date, end_date),
            ).fetchall()
        
        return [
            {
                "date": row["activity_date"],
                "narrative": row["narrative_text"],
                "model": row["model_name"] or "Unknown",
                "generated_at": row["generated_at"],
            }
            for row in rows
        ]
