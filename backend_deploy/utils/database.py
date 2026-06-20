"""
utils/database.py
SQLite persistence layer. Saves case searches, audits, notices.
Adds a real Case History tab — no more losing data on refresh.
"""
import sqlite3
import json
from datetime import datetime

DB_PATH = "aittorney.db"


def init_db():
    """Create tables if they don't exist. Call once at app startup."""
    conn = sqlite3.connect(DB_PATH)
    c    = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS case_searches (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT NOT NULL,
            query      TEXT NOT NULL,
            result     TEXT,
            win_prob   INTEGER,
            grade      TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS contract_audits (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT NOT NULL,
            filename   TEXT,
            role       TEXT,
            risk_score INTEGER,
            grade      TEXT,
            flags      TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS notices (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT NOT NULL,
            context    TEXT,
            tone       TEXT,
            output     TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS roadmaps (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT NOT NULL,
            situation  TEXT,
            jurisdiction TEXT,
            steps      TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


# ── Writers ──────────────────────────────────────────────────

def save_case(username: str, query: str, result: str, win_prob: int, grade: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO case_searches (username,query,result,win_prob,grade) VALUES (?,?,?,?,?)",
        (username, query[:500], result[:4000], win_prob, grade)
    )
    conn.commit()
    conn.close()


def save_audit(username: str, filename: str, role: str, score: int, grade: str, flags: list):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO contract_audits (username,filename,role,risk_score,grade,flags) VALUES (?,?,?,?,?,?)",
        (username, filename, role, score, grade, json.dumps(flags[:10]))
    )
    conn.commit()
    conn.close()


def save_notice(username: str, context: str, tone: str, output: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO notices (username,context,tone,output) VALUES (?,?,?,?)",
        (username, context[:500], tone, output[:5000])
    )
    conn.commit()
    conn.close()


def save_roadmap(username: str, situation: str, jurisdiction: str, steps: list):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO roadmaps (username,situation,jurisdiction,steps) VALUES (?,?,?,?)",
        (username, situation[:500], jurisdiction, json.dumps(steps))
    )
    conn.commit()
    conn.close()


# ── Readers ──────────────────────────────────────────────────

def get_case_history(username: str, limit: int = 15) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT query, win_prob, grade, created_at FROM case_searches "
        "WHERE username=? ORDER BY created_at DESC LIMIT ?",
        (username, limit)
    ).fetchall()
    conn.close()
    return [{"query": r[0], "win_prob": r[1], "grade": r[2], "date": r[3][:10]} for r in rows]


def get_audit_history(username: str, limit: int = 10) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT filename, role, risk_score, grade, created_at FROM contract_audits "
        "WHERE username=? ORDER BY created_at DESC LIMIT ?",
        (username, limit)
    ).fetchall()
    conn.close()
    return [{"filename": r[0], "role": r[1], "score": r[2], "grade": r[3], "date": r[4][:10]} for r in rows]


def get_notice_history(username: str, limit: int = 10) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT context, tone, output, created_at FROM notices "
        "WHERE username=? ORDER BY created_at DESC LIMIT ?",
        (username, limit)
    ).fetchall()
    conn.close()
    return [{"context": r[0], "tone": r[1], "output": r[2], "date": r[3][:10]} for r in rows]


def get_user_stats(username: str) -> dict:
    """Dashboard stats for the history page."""
    conn   = sqlite3.connect(DB_PATH)
    cases  = conn.execute("SELECT COUNT(*), AVG(win_prob) FROM case_searches WHERE username=?", (username,)).fetchone()
    audits = conn.execute("SELECT COUNT(*) FROM contract_audits WHERE username=?", (username,)).fetchone()
    notices= conn.execute("SELECT COUNT(*) FROM notices WHERE username=?", (username,)).fetchone()
    conn.close()
    return {
        "total_cases":   cases[0]  or 0,
        "avg_win_prob":  round(cases[1] or 0),
        "total_audits":  audits[0] or 0,
        "total_notices": notices[0] or 0,
    }