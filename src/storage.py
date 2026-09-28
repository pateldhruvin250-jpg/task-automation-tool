"""
Lightweight local storage using SQLite (no external DB server needed —
keeps the tool self-contained and easy to run anywhere, including CI).
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime

from src.config import Config


SCHEMA = """
CREATE TABLE IF NOT EXISTS rate_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    base_currency TEXT NOT NULL,
    target_currency TEXT NOT NULL,
    rate REAL NOT NULL,
    fetched_at TEXT NOT NULL
);
"""


@contextmanager
def get_connection():
    conn = sqlite3.connect(Config.DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with get_connection() as conn:
        conn.execute(SCHEMA)
        conn.commit()


def save_rates(base_currency: str, rates: dict, fetched_at: str = None):
    fetched_at = fetched_at or datetime.utcnow().isoformat()
    with get_connection() as conn:
        conn.executemany(
            "INSERT INTO rate_history (base_currency, target_currency, rate, fetched_at) "
            "VALUES (?, ?, ?, ?)",
            [(base_currency, currency, rate, fetched_at) for currency, rate in rates.items()],
        )
        conn.commit()


def get_previous_rate(base_currency: str, target_currency: str) -> float | None:
    """Return the most recent stored rate for a currency pair, before this run."""
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT rate FROM rate_history "
            "WHERE base_currency = ? AND target_currency = ? "
            "ORDER BY fetched_at DESC LIMIT 1",
            (base_currency, target_currency),
        )
        row = cur.fetchone()
        return row[0] if row else None
