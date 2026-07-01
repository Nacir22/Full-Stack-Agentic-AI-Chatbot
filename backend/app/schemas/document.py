"""Schémas de lecture des documents."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    content_type: str | None
    size_bytes: int
    num_chunks: int
    status: str
    created_at: datetime
