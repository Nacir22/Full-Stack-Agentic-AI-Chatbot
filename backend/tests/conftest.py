"""Fixtures partagées des tests backend.

Deux niveaux de fixtures :
  * `client` (sync) pour les routes sans DB ni LLM (ex. /health) ;
  * `async_client` (async) avec base SQLite en mémoire et **LLM simulé**, pour
    tester /chat sans clé API ni appel réseau.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401  (peuple Base.metadata)
from app.core.llm import get_chat_model
from app.db.base import Base
from app.db.session import get_db
from app.main import create_app


@pytest.fixture()
def client() -> TestClient:
    """Client synchrone pour les routes simples (sans DB)."""
    return TestClient(create_app())


@pytest_asyncio.fixture()
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Client async avec DB en mémoire et LLM simulé (réponses déterministes)."""
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_db() -> AsyncGenerator:
        async with maker() as session:
            yield session

    fake_model = FakeListChatModel(
        responses=["Réponse simulée de l'agent.", "Deuxième réponse simulée."]
    )

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_chat_model] = lambda: fake_model

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    await engine.dispose()
