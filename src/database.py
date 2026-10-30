"""Small SQLite store for saving creator analyses."""
import sqlite3
import json
from datetime import datetime, timezone
from config import DB_PATH

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                platform TEXT NOT NULL,
                topic TEXT NOT NULL,
                audit_score INTEGER,
                result_json TEXT NOT NULL
            )
        """)
        conn.commit()

def save_analysis(platform: str, topic: str, audit_score: int, result: dict) -> int:
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "INSERT INTO analyses (created_at, platform, topic, audit_score, result_json) VALUES (?, ?, ?, ?, ?)",
            (datetime.now(timezone.utc).isoformat(), platform, topic, int(audit_score), json.dumps(result, ensure_ascii=False))
        )
        conn.commit()
        return int(cur.lastrowid)

def get_recent_analyses(limit: int = 20):
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT id, created_at, platform, topic, audit_score FROM analyses ORDER BY id DESC LIMIT ?",
            (int(limit),)
        ).fetchall()
    return rows
