"""Service de gestion des documents (métadonnées SQL + vecteurs Chroma).

Coordonne les deux mondes : la ligne `Document` en base relationnelle et les
chunks vectorisés dans le store. Garde les routeurs fins.
"""

from __future__ import annotations

from langchain_core.vectorstores import VectorStore
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import Document, DocumentStatus
from app.rag.loaders import extract_text
from app.rag.pipeline import delete_document as delete_vectors
from app.rag.pipeline import ingest_text


class DocumentService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def ingest_upload(
        self,
        *,
        filename: str,
        data: bytes,
        content_type: str | None,
        store: VectorStore,
    ) -> Document:
        settings = get_settings()

        # 1. Ligne SQL (statut "processing") pour disposer d'un id stable.
        document = Document(
            filename=filename,
            content_type=content_type,
            size_bytes=len(data),
            status=DocumentStatus.PROCESSING.value,
        )
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)

        # 2. Extraction -> chunking -> embeddings -> store.
        try:
            text = extract_text(filename, data, content_type)
            num_chunks = await ingest_text(
                store,
                document.id,
                text,
                chunk_size=settings.RAG_CHUNK_SIZE,
                chunk_overlap=settings.RAG_CHUNK_OVERLAP,
            )
            document.num_chunks = num_chunks
            document.status = DocumentStatus.READY.value
        except Exception:
            document.status = DocumentStatus.FAILED.value
            await self.db.commit()
            raise

        await self.db.commit()
        await self.db.refresh(document)
        return document

    async def list(self) -> list[Document]:
        result = await self.db.execute(
            select(Document).order_by(Document.created_at.desc())
        )
        return list(result.scalars().all())

    async def get(self, document_id: str) -> Document | None:
        return await self.db.get(Document, document_id)

    async def delete(self, document_id: str, store: VectorStore) -> bool:
        document = await self.get(document_id)
        if document is None:
            return False
        await delete_vectors(store, document_id, document.num_chunks or 0)
        await self.db.delete(document)
        await self.db.commit()
        return True
