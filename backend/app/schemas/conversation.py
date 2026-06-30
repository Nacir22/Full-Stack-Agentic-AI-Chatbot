"""Schémas de lecture des conversations et messages."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    role: str
    content: str
    created_at: datetime


class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str | None
    created_at: datetime


class ConversationDetail(ConversationOut):
    messages: list[MessageOut] = []
