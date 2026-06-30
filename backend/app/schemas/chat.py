"""Schémas d'entrée/sortie de la route /chat."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, examples=["Bonjour, que peux-tu faire ?"])
    conversation_id: str | None = Field(
        default=None,
        description="Identifiant d'une conversation existante. Si absent, une "
        "nouvelle conversation est créée.",
    )


class ChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    response: str
