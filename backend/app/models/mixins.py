"""Mixins et utilitaires partagés par les modèles ORM."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


def generate_uuid() -> str:
    """Identifiant public opaque (UUID4 en str, compatible SQLite & Postgres)."""
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    """Horodatage UTC avec résolution microseconde (côté application).

    On fixe la valeur côté Python plutôt que via `CURRENT_TIMESTAMP` : SQLite ne
    stocke la date qu'à la seconde, ce qui rend l'ordre de messages créés dans la
    même seconde indéterministe. La résolution microseconde garantit un tri
    stable par `created_at`. `server_default` reste défini comme filet de
    sécurité au niveau base.
    """
    return datetime.now(timezone.utc)


class TimestampMixin:
    """Ajoute `created_at` / `updated_at` gérés à l'insertion/màj."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,
        server_default=func.now(),
        onupdate=_utcnow,
        nullable=False,
    )
