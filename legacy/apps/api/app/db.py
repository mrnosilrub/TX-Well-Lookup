import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def get_engine() -> Engine:
    url = os.getenv('DATABASE_URL', 'postgresql+psycopg2://postgres:postgres@localhost:5432/txwell')
    return create_engine(url, pool_pre_ping=True)


@contextmanager
def get_db_session():
    engine = get_engine()
    conn = engine.connect()
    try:
        yield conn
    finally:
        conn.close()

import os
from contextlib import contextmanager
from typing import Iterator, Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


_engine: Optional[Engine] = None
_SessionLocal: Optional[sessionmaker] = None


def get_engine() -> Optional[Engine]:
    global _engine, _SessionLocal
    if _engine is not None:
        return _engine
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return None
    _engine = create_engine(database_url, pool_pre_ping=True, future=True)
    _SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False, future=True)
    return _engine


@contextmanager
def get_db_session() -> Iterator[Session]:
    engine = get_engine()
    if engine is None:
        yield None  # type: ignore
        return
    assert _SessionLocal is not None
    session = _SessionLocal()
    try:
        yield session
    finally:
        session.close()


