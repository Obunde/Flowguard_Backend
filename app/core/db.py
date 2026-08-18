"""The one DB engine + session factory for the whole app.

Built from the single `settings.database_url` (app/core/config.py). Every
module gets its DB access through `get_db` (a FastAPI dependency) — nothing
outside this file calls `create_engine` or opens a connection string.
migrations/env.py imports `settings` directly rather than duplicating this.
"""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True, future=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a request-scoped session.

    Usage: `db: Session = Depends(get_db)` in a route, then pass `db` down
    into the service layer. Routes never talk to the engine/session factory
    directly.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
