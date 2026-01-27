import sqlite3
from pathlib import Path
from src.config import settings

import logging

REQUIRED_TABLES = {
    "products",
    "raw_api_responses",
    "prices_history",
    "subscriptions",
    "chat_settings",
    "alembic_version",
}

def log_db_schema(conn, table_name: str = "prices_history") -> None:
    try:
        cur = conn.cursor()

        cur.execute(f"PRAGMA table_info({table_name});")
        cols = cur.fetchall()

        #Колонки
        if not cols:
            logger.warning("DB schema: table '%s' not found.", table_name)
            return

        cols_pretty = ", ".join(
            f"{c[1]} {c[2]}{' NOT NULL' if c[3] else ''}{' PK' if c[5] else ''}"
            + (f" DEFAULT {c[4]}" if c[4] is not None else "")
            for c in cols
        )
        logger.info("DB schema: %s columns: %s", table_name, cols_pretty)

        # Индексы таблицы
        cur.execute(f"PRAGMA index_list({table_name});")
        idxs = cur.fetchall()
        if idxs:
            idx_names = ", ".join(i[1] for i in idxs)  # i[1] = name
            logger.info("DB schema: %s indexes: %s", table_name, idx_names)
        else:
            logger.info("DB schema: %s indexes: none", table_name)

    except Exception:
        logger.exception("DB schema: failed to read schema info.")

logger = logging.getLogger("price_monitor")

def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.db_path, check_same_thread=False, timeout=5)
    conn.row_factory = sqlite3.Row
    return conn

def _list_tables(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    ).fetchall()
    return {r["name"] for r in rows}


def init_db() -> None:
    Path(settings.db_path).touch(exist_ok=True)

    conn = get_conn()
    try:
        tables = _list_tables(conn)
    finally:
        conn.close()

    missing = REQUIRED_TABLES - tables
    if missing:
        logger.error("В базе нет нужных таблиц: %s", ", ".join(sorted(missing)))
        raise RuntimeError(
            "База данных не инициализирована миграциями. "
            "Запусти: alembic upgrade head"
        )

    logger.info("DB в порядке. Все таблицы на месте.")


