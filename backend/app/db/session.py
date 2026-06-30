"""Moteur et sessions asynchrones SQLAlchemy.

On utilise l'API **async** de SQLAlchemy 2.0 pour coller au modèle async de
FastAPI. L'URL provient de la configuration (`DATABASE_URL`), ce qui permet de
basculer SQLite (dev) ↔ PostgreSQL (prod) sans changer le code.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings

settings = get_settings()

# `future=True` est implicite en 2.0 ; pool_pre_ping évite les connexions mortes.
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.LOG_LEVEL == "DEBUG",
    pool_pre_ping=True,
)

# expire_on_commit=False : les objets restent utilisables après commit
# (pratique pour renvoyer l'objet dans la réponse API).
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dépendance FastAPI : fournit une session DB et la ferme proprement."""
    async with SessionLocal() as session:
        yield session
