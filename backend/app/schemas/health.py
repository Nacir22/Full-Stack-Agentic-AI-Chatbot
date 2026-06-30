"""Schémas Pydantic de la route de santé."""

from __future__ import annotations

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Réponse renvoyée par GET /health."""

    status: str = Field(default="ok", examples=["ok"])
    app: str = Field(examples=["agentic-chatbot"])
    version: str = Field(examples=["0.1.0"])
    environment: str = Field(examples=["development"])
