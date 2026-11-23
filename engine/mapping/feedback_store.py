"""
SQLite-backed feedback store for persisting user-confirmed mappings.
Stage 9 — User Feedback Learning.
"""

from datetime import datetime, timezone
import sqlite3
from typing import Dict, List, Optional


class FeedbackStore:
    def __init__(self, db_path: str = "conversion_history.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS confirmed_mappings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_name TEXT NOT NULL,
                    target_name TEXT NOT NULL,
                    frequency INTEGER DEFAULT 1,
                    last_used TEXT,
                    UNIQUE(source_name, target_name)
                )
                """
            )
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS conversion_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE,
                    excel_path TEXT,
                    word_path TEXT,
                    output_path TEXT,
                    record_count INTEGER,
                    status TEXT,
                    created_at TEXT
                )
                """
            )

    def record_confirmed_mapping(self, source_name: str, target_name: str) -> None:
        """Increment frequency count of user-confirmed mapping pair."""
        s = source_name.strip().lower()
        t = target_name.strip().lower()
        if not s or not t:
            return

        now_str = datetime.now(timezone.utc).isoformat()
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO confirmed_mappings (source_name, target_name, frequency, last_used)
                VALUES (?, ?, 1, ?)
                ON CONFLICT(source_name, target_name) DO UPDATE SET
                    frequency = frequency + 1,
                    last_used = ?
                """,
                (s, t, now_str, now_str),
            )

    def get_historical_affinity(self, source_name: str, target_name: str) -> float:
        """
        Returns a boost factor (0.0 to 0.65) based on how frequently this pair was previously confirmed.
        """
        s = source_name.strip().lower()
        t = target_name.strip().lower()
        cursor = self.conn.execute(
            "SELECT frequency FROM confirmed_mappings WHERE source_name = ? AND target_name = ?",
            (s, t),
        )
        row = cursor.fetchone()
        if row:
            freq = row[0]
            return min(0.35 + (freq * 0.10), 0.65)
        return 0.0

    def record_conversion_run(
        self, session_id: str, excel_path: str, word_path: str, output_path: str, record_count: int, status: str
    ):
        now_str = datetime.now(timezone.utc).isoformat()
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO conversion_runs
                (session_id, excel_path, word_path, output_path, record_count, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (session_id, excel_path, word_path, output_path, record_count, status, now_str),
            )

    def get_recent_runs(self, limit: int = 20) -> List[Dict]:
        cursor = self.conn.execute(
            "SELECT id, session_id, excel_path, word_path, output_path, record_count, status, created_at FROM conversion_runs ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def close(self):
        try:
            self.conn.close()
        except Exception:
            pass

    def __del__(self):
        self.close()
