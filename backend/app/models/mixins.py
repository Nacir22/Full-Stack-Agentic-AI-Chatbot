"""Mixins et utilitaires partagés par les modèles ORM."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


def generate_uuid() -> str:
    """Identifiant public opaque (UUID4 en str, compatible SQLite & Postgres)."""
    return str(uuid.uuid4())


class TimestampMixin:
    """Ajoute `created_at` / `updated_at` gérés par la base."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
