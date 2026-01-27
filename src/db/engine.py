from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

from src.config import settings


def make_engine() -> Engine:
    db_url = f"sqlite:///{settings.db_path}"
    return create_engine(
        db_url,
        future=True,
        connect_args={"check_same_thread": False},
    )


_engine = make_engine()

SessionLocal = sessionmaker(
    bind=_engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
)


def get_session() -> Session:
    return SessionLocal()
