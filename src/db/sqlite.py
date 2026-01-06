import sqlite3
from pathlib import Path
from src.config import settings

def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    Path(settings.db_path).touch(exist_ok=True)

    conn = get_conn()
    try:
        with open("src/db/schema.sql", "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()
    finally:
        conn.close()
