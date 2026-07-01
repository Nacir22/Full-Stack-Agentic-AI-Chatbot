"""Tests unitaires des outils de l'agent."""

from __future__ import annotations

import httpx
import pytest
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.vectorstores import InMemoryVectorStore

from app.models import Message, MessageRole
from app.rag.pipeline import ingest_text
from app.tools.external_api import get_weather
from app.tools.memory_tool import make_conversation_memory_tool
from app.tools.rag_search import make_rag_search_tool


class _StubConversationService:
    def __init__(self, messages: list[Message]) -> None:
        self._messages = messages

    async def get_history(self, conversation_id: str) -> list[Message]:
        return self._messages


@pytest.mark.asyncio
async def test_rag_search_tool_returns_chunks() -> None:
    store = InMemoryVectorStore(DeterministicFakeEmbedding(size=32))
    await ingest_text(
        store, "doc-1", "Le RAG relie recherche et génération. " * 10,
        chunk_size=120, chunk_overlap=20,
    )
    tool = make_rag_search_tool(store, top_k=3)
    result = await tool.ainvoke({"query": "recherche"})
    assert isinstance(result, str)
    assert result and "Aucun" not in result


@pytest.mark.asyncio
async def test_rag_search_tool_no_results() -> None:
    store = InMemoryVectorStore(DeterministicFakeEmbedding(size=32))
    tool = make_rag_search_tool(store, top_k=3)
    result = await tool.ainvoke({"query": "quoi que ce soit"})
    assert "Aucun passage" in result


@pytest.mark.asyncio
async def test_memory_tool_finds_past_message() -> None:
    messages = [
        Message(conversation_id="c", role=MessageRole.USER.value, content="Je m'appelle Hakim"),
        Message(conversation_id="c", role=MessageRole.ASSISTANT.value, content="Enchanté"),
    ]
    tool = make_conversation_memory_tool(_StubConversationService(messages), "c")
    result = await tool.ainvoke({"query": "hakim"})
    assert "Hakim" in result


@pytest.mark.asyncio
async def test_memory_tool_no_match() -> None:
    tool = make_conversation_memory_tool(_StubConversationService([]), "c")
    result = await tool.ainvoke({"query": "inexistant"})
    assert "Aucun message" in result


@pytest.mark.asyncio
async def test_weather_tool_handles_network_error(monkeypatch: pytest.MonkeyPatch) -> None:
    class _BoomClient:
        def __init__(self, *a, **k): ...
        async def __aenter__(self): return self
        async def __aexit__(self, *a): return False
        async def get(self, *a, **k): raise httpx.ConnectError("réseau indisponible")

    monkeypatch.setattr(httpx, "AsyncClient", _BoomClient)
    result = await get_weather(48.85, 2.35)
    assert "Erreur" in result
