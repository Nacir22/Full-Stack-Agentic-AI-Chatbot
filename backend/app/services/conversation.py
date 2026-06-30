"""Service de gestion des conversations et messages.

Toute la logique d'accès aux données vit ici : les routeurs FastAPI restent
fins (validation + délégation). Cela rend la logique testable sans HTTP.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Conversation, Message


class ConversationService:
    """Opérations CRUD de haut niveau sur les conversations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self, title: str | None = None, user_id: str | None = None
    ) -> Conversation:
        conversation = Conversation(title=title, user_id=user_id)
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation

    async def get(self, conversation_id: str) -> Conversation | None:
        return await self.db.get(Conversation, conversation_id)

    async def list(self) -> list[Conversation]:
        result = await self.db.execute(
            select(Conversation).order_by(Conversation.created_at.desc())
        )
        return list(result.scalars().all())

    async def add_message(
        self, conversation_id: str, role: str, content: str
    ) -> Message:
        message = Message(conversation_id=conversation_id, role=role, content=content)
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def get_history(self, conversation_id: str) -> list[Message]:
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at, Message.id)
        )
        return list(result.scalars().all())
