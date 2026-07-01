"""Tests du pipeline RAG et des endpoints documentaires.

On utilise un `InMemoryVectorStore` + `DeterministicFakeEmbedding` : pas de
ChromaDB, pas de réseau, résultats déterministes.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.vectorstores import InMemoryVectorStore

from app.rag.chunking import split_text
from app.rag.loaders import clean_text, extract_text
from app.rag.pipeline import delete_document, ingest_text, search


# --- Unitaires : loaders / chunking ---------------------------------------


def test_clean_text_collapses_whitespace() -> None:
    assert clean_text("a   b\r\n\n\n\nc  ") == "a b\n\nc"


def test_extract_text_from_plain_bytes() -> None:
    text = extract_text("notes.txt", b"Bonjour   le monde", "text/plain")
    assert text == "Bonjour le monde"


def test_split_text_produces_overlapping_chunks() -> None:
    text = ". ".join(f"phrase numero {i}" for i in range(200))
    chunks = split_text(text, chunk_size=100, chunk_overlap=20)
    assert len(chunks) > 1
    assert all(chunks)


def test_split_empty_text_returns_empty() -> None:
    assert split_text("   ", 100, 10) == []


# --- Pipeline : ingest / search / delete ----------------------------------


@pytest.mark.asyncio
async def test_ingest_search_delete_cycle() -> None:
    store = InMemoryVectorStore(DeterministicFakeEmbedding(size=32))
    text = "Le RAG combine recherche vectorielle et génération. " * 20

    n = await ingest_text(store, "doc-1", text, chunk_size=120, chunk_overlap=20)
    assert n > 0

    results = await search(store, "recherche vectorielle", k=3)
    assert len(results) >= 1
    assert results[0].metadata["document_id"] == "doc-1"

    await delete_document(store, "doc-1", n)
    after = await search(store, "recherche vectorielle", k=3)
    assert after == []


# --- Endpoints ------------------------------------------------------------


async def test_upload_then_list_then_delete(async_client: AsyncClient) -> None:
    content = b"Section 1. " + b"Contenu de test pour le RAG. " * 30
    resp = await async_client.post(
        "/api/v1/upload",
        files={"file": ("guide.txt", content, "text/plain")},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "ready"
    assert body["num_chunks"] >= 1
    doc_id = body["id"]

    listing = await async_client.get("/api/v1/documents")
    assert listing.status_code == 200
    assert any(d["id"] == doc_id for d in listing.json())

    deleted = await async_client.delete(f"/api/v1/documents/{doc_id}")
    assert deleted.status_code == 204

    listing2 = await async_client.get("/api/v1/documents")
    assert all(d["id"] != doc_id for d in listing2.json())


async def test_upload_empty_file_rejected(async_client: AsyncClient) -> None:
    resp = await async_client.post(
        "/api/v1/upload",
        files={"file": ("empty.txt", b"", "text/plain")},
    )
    assert resp.status_code == 400


async def test_delete_unknown_document_returns_404(async_client: AsyncClient) -> None:
    resp = await async_client.delete("/api/v1/documents/nope")
    assert resp.status_code == 404
