from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

from common.config import get_settings


def _ensure_sqlite_directory(database_url: str) -> None:
    if not database_url.startswith("sqlite:///./"):
        return

    relative_path = database_url.replace("sqlite:///./", "", 1)
    Path(relative_path).parent.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_engine():
    settings = get_settings()
    if not settings.database_url:
        raise ValueError("DATABASE_URL is not configured.")
    _ensure_sqlite_directory(settings.database_url)
    connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
    return create_engine(settings.database_url, connect_args=connect_args)


def prepare_database() -> None:
    settings = get_settings()
    if not settings.database_url:
        return
    if settings.database_url.startswith("sqlite"):
        SQLModel.metadata.create_all(get_engine())


def get_session() -> Generator[Session, None, None]:
    with Session(get_engine()) as session:
        yield session
