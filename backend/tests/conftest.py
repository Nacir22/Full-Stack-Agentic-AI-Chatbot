"""Fixtures partagées des tests backend."""

from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.vectorstores import InMemoryVectorStore
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.core.llm import get_chat_model
from app.db.base import Base
from app.db.session import get_db
from app.main import create_app
from app.rag.embeddings import get_embeddings
from app.rag.store import get_vector_store


@pytest.fixture()
def client() -> TestClient:
    """Client synchrone pour les routes simples (sans DB)."""
    return TestClient(create_app())


@pytest_asyncio.fixture()
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Client async : DB en mémoire, LLM simulé, store vectoriel en mémoire."""
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
    fake_embeddings = DeterministicFakeEmbedding(size=32)
    memory_store = InMemoryVectorStore(fake_embeddings)

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_chat_model] = lambda: fake_model
    app.dependency_overrides[get_embeddings] = lambda: fake_embeddings
    app.dependency_overrides[get_vector_store] = lambda: memory_store

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    await engine.dispose()
