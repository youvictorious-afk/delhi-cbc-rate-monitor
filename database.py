import sqlite3
from config import DATABASE_PATH


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():

    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS rate_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            checked_at TEXT NOT NULL,

            state TEXT NOT NULL,

            publication TEXT,

            edition TEXT,

            language TEXT,

            media_type TEXT,

            rate REAL,

            rate_unit TEXT,

            effective_from TEXT,

            raw_text TEXT,

            source_url TEXT,

            confidence TEXT
        )
    """)

    conn.commit()
    conn.close()


def insert_rate(row):

    conn = get_connection()

    conn.execute("""
        INSERT INTO rate_history (
            checked_at,
            state,
            publication,
            edition,
            language,
            media_type,
            rate,
            rate_unit,
            effective_from,
            raw_text,
            source_url,
            confidence
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        row["checked_at"],
        "DELHI",
        row.get("publication"),
        row.get("edition"),
        row.get("language"),
        row.get("media_type"),
        row.get("rate"),
        row.get("rate_unit"),
        row.get("effective_from"),
        row.get("raw_text"),
        row["source_url"],
        row.get("confidence", "LOW")
    ))

    conn.commit()
    conn.close()


def get_history():

    conn = get_connection()

    rows = conn.execute("""
        SELECT *
        FROM rate_history
        ORDER BY checked_at DESC
    """).fetchall()

    conn.close()

    return [dict(row) for row in rows]


def get_latest():

    conn = get_connection()

    rows = conn.execute("""
        SELECT *
        FROM rate_history
        WHERE state = 'DELHI'
        ORDER BY checked_at DESC
    """).fetchall()

    conn.close()

    return [dict(row) for row in rows]
