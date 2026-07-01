"""Modèle Document.

Métadonnées d'un document ingéré. Le **texte des chunks** et leurs **embeddings**
vivent dans ChromaDB (base vectorielle), pas en SQL : on garde ici seulement de
quoi lister, suivre l'état et retrouver/supprimer les vecteurs associés
(via `document_id` + `num_chunks`).
"""

from __future__ import annotations

import enum

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin, generate_uuid


class DocumentStatus(str, enum.Enum):
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class Document(TimestampMixin, Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    content_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    size_bytes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    num_chunks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(
        String(16), default=DocumentStatus.PROCESSING.value, nullable=False
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Document id={self.id} filename={self.filename!r} status={self.status}>"
