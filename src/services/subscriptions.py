from datetime import datetime, timezone
from src.db.sqlite import get_conn

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def set_chat_default_threshold(chat_id: int, threshold: float) -> None:
    conn = get_conn()
    try:
        conn.execute(
            """
            INSERT INTO chat_settings(chat_id, default_threshold_percent, updated_at)
            VALUES(?,?,?)
            ON CONFLICT(chat_id) DO UPDATE SET
              default_threshold_percent=excluded.default_threshold_percent,
              updated_at=excluded.updated_at
            """,
            (chat_id, threshold, _now_iso()),
        )
        conn.commit()
    finally:
        conn.close()

def get_chat_default_threshold(chat_id: int) -> float:
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT default_threshold_percent FROM chat_settings WHERE chat_id=?",
            (chat_id,),
        ).fetchone()
        return float(row["default_threshold_percent"]) if row else 5.0
    finally:
        conn.close()

def upsert_subscription(chat_id: int, product_id: int, threshold: float) -> None:
    conn = get_conn()
    try:
        conn.execute(
            """
            INSERT INTO subscriptions(chat_id, product_id, threshold_percent, is_active, created_at)
            VALUES(?,?,?,?,?)
            ON CONFLICT(chat_id, product_id) DO UPDATE SET
              threshold_percent=excluded.threshold_percent,
              is_active=1
            """,
            (chat_id, product_id, threshold, 1, _now_iso()),
        )
        conn.commit()
    finally:
        conn.close()

def disable_subscription(chat_id: int, product_id: int) -> None:
    conn = get_conn()
    try:
        conn.execute(
            "UPDATE subscriptions SET is_active=0 WHERE chat_id=? AND product_id=?",
            (chat_id, product_id),
        )
        conn.commit()
    finally:
        conn.close()

def list_active_subscriptions(chat_id: int) -> list[tuple[int, float]]:
    conn = get_conn()
    try:
        rows = conn.execute(
            """
            SELECT product_id, threshold_percent
            FROM subscriptions
            WHERE chat_id=? AND is_active=1
            ORDER BY product_id
            """,
            (chat_id,),
        ).fetchall()
        return [(int(r["product_id"]), float(r["threshold_percent"])) for r in rows]
    finally:
        conn.close()

def list_all_active_subscriptions() -> list[tuple[int, int, float]]:
    conn = get_conn()
    try:
        rows = conn.execute(
            """
            SELECT chat_id, product_id, threshold_percent
            FROM subscriptions
            WHERE is_active=1
            """,
        ).fetchall()
        return [(int(r["chat_id"]), int(r["product_id"]), float(r["threshold_percent"])) for r in rows]
    finally:
        conn.close()
