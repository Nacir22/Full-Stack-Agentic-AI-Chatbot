"""Tests des modèles ORM et des relations.

On utilise une base SQLite **en mémoire** (StaticPool pour partager l'unique
connexion entre la création des tables et la session), ce qui rend les tests
rapides et sans effet de bord.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401  (peuple Base.metadata)
from app.db.base import Base
from app.models import Conversation, Message, MessageRole, User


@pytest_asyncio.fixture()
async def session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as s:
        yield s
    await engine.dispose()


async def test_conversation_with_messages(session: AsyncSession) -> None:
    conv = Conversation(title="Première conversation")
    conv.messages.append(Message(role=MessageRole.USER.value, content="Bonjour"))
    conv.messages.append(Message(role=MessageRole.ASSISTANT.value, content="Salut !"))
    session.add(conv)
    await session.commit()

    rows = (
        await session.execute(
            select(Message).where(Message.conversation_id == conv.id)
        )
    ).scalars().all()

    assert len(rows) == 2
    assert conv.id  # UUID auto-généré
    assert conv.created_at is not None


async def test_cascade_delete(session: AsyncSession) -> None:
    conv = Conversation(title="À supprimer")
    conv.messages.append(Message(role="user", content="x"))
    session.add(conv)
    await session.commit()

    await session.delete(conv)
    await session.commit()

    remaining = (await session.execute(select(Message))).scalars().all()
    assert remaining == []


async def test_user_relationship(session: AsyncSession) -> None:
    user = User(username="hakim")
    user.conversations.append(Conversation(title="Conv de Hakim"))
    session.add(user)
    await session.commit()

    loaded = (
        await session.execute(select(User).where(User.username == "hakim"))
    ).scalar_one()
    assert loaded.username == "hakim"
