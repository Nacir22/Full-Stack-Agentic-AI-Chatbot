"""Orchestration du pipeline RAG : ingestion et recherche.

Ingestion :  texte -> chunks -> documents LangChain (avec métadonnées) -> store.
Recherche  :  requête -> chunks les plus proches (similarité vectorielle).

Les identifiants de chunk sont déterministes (`<document_id>:<index>`), ce qui
permet de **supprimer** proprement tous les vecteurs d'un document sans dépendre
d'un filtre par métadonnées spécifique au backend.
"""

from __future__ import annotations

from langchain_core.documents import Document as LCDocument
from langchain_core.vectorstores import VectorStore

from app.rag.chunking import split_text


def _chunk_id(document_id: str, index: int) -> str:
    return f"{document_id}:{index}"


def build_chunk_documents(
    document_id: str, chunks: list[str]
) -> tuple[list[LCDocument], list[str]]:
    docs: list[LCDocument] = []
    ids: list[str] = []
    for index, chunk in enumerate(chunks):
        docs.append(
            LCDocument(
                page_content=chunk,
                metadata={"document_id": document_id, "chunk_index": index},
            )
        )
        ids.append(_chunk_id(document_id, index))
    return docs, ids


async def ingest_text(
    store: VectorStore,
    document_id: str,
    text: str,
    *,
    chunk_size: int,
    chunk_overlap: int,
) -> int:
    """Découpe le texte, l'indexe dans le store et renvoie le nombre de chunks."""
    chunks = split_text(text, chunk_size, chunk_overlap)
    if not chunks:
        return 0
    docs, ids = build_chunk_documents(document_id, chunks)
    await store.aadd_documents(docs, ids=ids)
    return len(ids)


async def delete_document(store: VectorStore, document_id: str, num_chunks: int) -> None:
    """Supprime tous les vecteurs d'un document du store."""
    if num_chunks <= 0:
        return
    ids = [_chunk_id(document_id, i) for i in range(num_chunks)]
    await store.adelete(ids=ids)


async def search(store: VectorStore, query: str, k: int) -> list[LCDocument]:
    """Retourne les `k` chunks les plus proches de la requête."""
    return await store.asimilarity_search(query, k=k)
