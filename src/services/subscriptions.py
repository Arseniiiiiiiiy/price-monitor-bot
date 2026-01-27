from datetime import datetime, timezone

from src.db.session import session_scope
from src.db.models import ChatSetting, Subscription


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def set_chat_default_threshold(chat_id: int, threshold: float) -> None:
    with session_scope() as s:
        row = s.get(ChatSetting, chat_id)
        if row is None:
            s.add(ChatSetting(chat_id=chat_id, default_threshold_percent=threshold, updated_at=_now_iso()))
        else:
            row.default_threshold_percent = threshold
            row.updated_at = _now_iso()


def get_chat_default_threshold(chat_id: int) -> float:
    with session_scope() as s:
        row = s.get(ChatSetting, chat_id)
        return float(row.default_threshold_percent) if row else 5.0


def upsert_subscription(chat_id: int, product_id: int, threshold: float) -> None:
    with session_scope() as s:
        row = s.get(Subscription, {"chat_id": chat_id, "product_id": product_id})
        if row is None:
            s.add(
                Subscription(
                    chat_id=chat_id,
                    product_id=product_id,
                    threshold_percent=threshold,
                    is_active=1,
                    created_at=_now_iso(),
                )
            )
        else:
            row.threshold_percent = threshold
            row.is_active = 1


def disable_subscription(chat_id: int, product_id: int) -> None:
    with session_scope() as s:
        row = s.get(Subscription, {"chat_id": chat_id, "product_id": product_id})
        if row:
            row.is_active = 0


def list_active_subscriptions(chat_id: int) -> list[tuple[int, float]]:
    with session_scope() as s:
        rows = (
            s.query(Subscription)
            .filter(Subscription.chat_id == chat_id, Subscription.is_active == 1)
            .order_by(Subscription.product_id.asc())
            .all()
        )
        return [(int(r.product_id), float(r.threshold_percent)) for r in rows]


def list_all_active_subscriptions() -> list[tuple[int, int, float]]:
    with session_scope() as s:
        rows = s.query(Subscription).filter(Subscription.is_active == 1).all()
        return [(int(r.chat_id), int(r.product_id), float(r.threshold_percent)) for r in rows]
