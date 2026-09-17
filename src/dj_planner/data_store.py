from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Iterable, List
from platformdirs import user_data_path


def default_db_path() -> Path:
    return user_data_path("DJPlanner", appauthor=False) / "planner.sqlite3"


class DataStore:
    def __init__(self, db_path: str | None = None):
        self.db_path = Path(db_path) if db_path else default_db_path()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        cur = self.conn.cursor()
        cur.executescript("""
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS djs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            active INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        );

        CREATE TABLE IF NOT EXISTS bands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start TEXT NOT NULL,
            end TEXT NOT NULL,
            value REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS history_sets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            party_external_id TEXT,
            party_name TEXT,
            date TEXT,
            dj TEXT NOT NULL,
            start TEXT NOT NULL,
            end TEXT NOT NULL,
            value REAL NOT NULL DEFAULT 0,
            position REAL
        );
        """)
        self.conn.commit()

    def close(self):
        self.conn.close()

    def get_djs(self) -> List[str]:
        rows = self.conn.execute("SELECT name FROM djs WHERE active=1 ORDER BY id").fetchall()
        return [r["name"] for r in rows]

    def replace_djs(self, names: Iterable[str]):
        cur = self.conn.cursor()
        cur.execute("UPDATE djs SET active=0")
        for name in names:
            cur.execute(
                "INSERT INTO djs(name, active) VALUES(?,1) "
                "ON CONFLICT(name) DO UPDATE SET active=1",
                (name,),
            )
        self.conn.commit()

    def add_dj(self, name: str):
        self.conn.execute(
            "INSERT INTO djs(name, active) VALUES(?,1) ON CONFLICT(name) DO UPDATE SET active=1",
            (name,),
        )
        self.conn.commit()

    def remove_dj(self, name: str):
        self.conn.execute("UPDATE djs SET active=0 WHERE name=?", (name,))
        self.conn.commit()

    def get_bands(self):
        rows = self.conn.execute("SELECT start,end,value FROM bands ORDER BY id").fetchall()
        return [(r["start"], r["end"], r["value"]) for r in rows]

    def replace_bands(self, bands):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM bands")
        cur.executemany(
            "INSERT INTO bands(start,end,value) VALUES(?,?,?)",
            [(s, e, float(v)) for s, e, v in bands],
        )
        self.conn.commit()

    def set_setting(self, key: str, value: str):
        self.conn.execute(
            "INSERT INTO settings(key,value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )
        self.conn.commit()

    def get_setting(self, key: str, default: str = "") -> str:
        row = self.conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return row["value"] if row else default

    def replace_history(self, history_rows):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM history_sets")
        cur.executemany(
            """INSERT INTO history_sets(
                party_external_id,party_name,date,dj,start,end,value,position
            ) VALUES(?,?,?,?,?,?,?,?)""",
            [
                (
                    h.party_id,
                    h.party_name,
                    h.date,
                    h.dj,
                    h.start,
                    h.end,
                    float(h.value or 0),
                    h.position,
                )
                for h in history_rows
            ],
        )
        self.conn.commit()

    def append_history(self, history_rows):
        self.conn.executemany(
            """INSERT INTO history_sets(
                party_external_id,party_name,date,dj,start,end,value,position
            ) VALUES(?,?,?,?,?,?,?,?)""",
            [
                (
                    h.party_id,
                    h.party_name,
                    h.date,
                    h.dj,
                    h.start,
                    h.end,
                    float(h.value or 0),
                    h.position,
                )
                for h in history_rows
            ],
        )
        self.conn.commit()

    def get_history(self, HistorySet):
        rows = self.conn.execute(
            """SELECT party_external_id,party_name,date,dj,start,end,value,position
               FROM history_sets ORDER BY id"""
        ).fetchall()
        return [
            HistorySet(
                party_id=r["party_external_id"] or "",
                party_name=r["party_name"] or "",
                date=r["date"] or "",
                dj=r["dj"],
                start=r["start"],
                end=r["end"],
                value=r["value"],
                position=r["position"],
            )
            for r in rows
        ]

    def clear_history(self):
        self.conn.execute("DELETE FROM history_sets")
        self.conn.commit()
