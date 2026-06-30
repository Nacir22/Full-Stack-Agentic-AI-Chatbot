"""Modèle Message : un tour de parole dans une conversation."""

from __future__ import annotations

import enum
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from app.models.conversation import Conversation


class MessageRole(str, enum.Enum):
    """Rôles possibles d'un message (compatibles avec l'API des LLM)."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class Message(TimestampMixin, Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    conversation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Stocké en str pour rester portable (SQLite/Postgres) ; validé côté app.
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Message id={self.id} role={self.role} conv={self.conversation_id}>"
