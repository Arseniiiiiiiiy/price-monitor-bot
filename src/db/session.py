from __future__ import annotations

from contextlib import contextmanager
from sqlalchemy.orm import Session

from src.db.engine import get_session


@contextmanager
def session_scope() -> Session:
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
