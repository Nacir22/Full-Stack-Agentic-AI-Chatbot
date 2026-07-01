"""Routes de gestion documentaire : upload, liste, suppression.

L'upload déclenche tout le pipeline RAG (extraction -> chunking -> embeddings ->
ChromaDB). Le store vectoriel et les embeddings sont injectés par dépendance,
donc surchargeables en test.
"""

from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from langchain_core.vectorstores import VectorStore
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.rag.store import get_vector_store
from app.schemas.document import DocumentOut
from app.services.document import DocumentService

router = APIRouter()


@router.post(
    "/upload",
    response_model=DocumentOut,
    status_code=status.HTTP_201_CREATED,
    tags=["documents"],
    summary="Uploader et indexer un document",
)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    store: VectorStore = Depends(get_vector_store),
) -> DocumentOut:
    data = await file.read()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Fichier vide"
        )
    document = await DocumentService(db).ingest_upload(
        filename=file.filename or "document",
        data=data,
        content_type=file.content_type,
        store=store,
    )
    return DocumentOut.model_validate(document)


@router.get(
    "/documents",
    response_model=list[DocumentOut],
    tags=["documents"],
    summary="Lister les documents indexés",
)
async def list_documents(db: AsyncSession = Depends(get_db)) -> list[DocumentOut]:
    documents = await DocumentService(db).list()
    return [DocumentOut.model_validate(d) for d in documents]


@router.delete(
    "/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["documents"],
    summary="Supprimer un document et ses vecteurs",
)
async def delete_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    store: VectorStore = Depends(get_vector_store),
) -> Response:
    deleted = await DocumentService(db).delete(document_id, store)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document introuvable"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
