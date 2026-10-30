"""
SQLite Database manager for saving translation history, error reports, and execution results.
"""
import sqlite3
import os
import json
import time
from typing import List, Dict, Any, Optional

DB_FILE = os.path.join(os.path.dirname(__file__), "transpiler_history.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        source_lang TEXT,
        target_lang TEXT,
        original_code TEXT,
        corrected_code TEXT,
        target_code TEXT,
        errors_json TEXT,
        execution_match INTEGER,
        notes TEXT
    )
    """)
    conn.commit()
    conn.close()

def save_history_record(
    source_lang: str,
    target_lang: str,
    original_code: str,
    corrected_code: str,
    target_code: str,
    errors: List[Dict[str, Any]],
    execution_match: Optional[bool] = None,
    notes: str = ""
) -> int:
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO history (
        source_lang, target_lang, original_code, corrected_code, target_code,
        errors_json, execution_match, notes
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        source_lang, target_lang, original_code, corrected_code, target_code,
        json.dumps(errors), 1 if execution_match else (0 if execution_match is False else -1),
        notes
    ))
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record_id

def get_history_records(limit: int = 50) -> List[Dict[str, Any]]:
    init_db()
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM history ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    results = []
    for r in rows:
        results.append({
            "id": r["id"],
            "timestamp": r["timestamp"],
            "source_lang": r["source_lang"],
            "target_lang": r["target_lang"],
            "original_code": r["original_code"],
            "corrected_code": r["corrected_code"],
            "target_code": r["target_code"],
            "errors": json.loads(r["errors_json"] or "[]"),
            "execution_match": r["execution_match"],
            "notes": r["notes"]
        })
    conn.close()
    return results

def clear_history():
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM history")
    conn.commit()
    conn.close()
