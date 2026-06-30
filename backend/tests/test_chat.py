"""Tests de l'endpoint /chat et de la persistance des conversations.

Le LLM est simulé (FakeListChatModel) : aucun appel réseau ni clé API requis.
"""

from __future__ import annotations

from httpx import AsyncClient


async def test_chat_creates_conversation(async_client: AsyncClient) -> None:
    resp = await async_client.post("/api/v1/chat", json={"message": "Bonjour"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["response"] == "Réponse simulée de l'agent."
    assert body["conversation_id"]
    assert body["message_id"]


async def test_chat_persists_and_continues_conversation(
    async_client: AsyncClient,
) -> None:
    first = await async_client.post("/api/v1/chat", json={"message": "Premier"})
    conv_id = first.json()["conversation_id"]

    second = await async_client.post(
        "/api/v1/chat",
        json={"message": "Deuxième", "conversation_id": conv_id},
    )
    assert second.status_code == 200
    assert second.json()["conversation_id"] == conv_id

    # 2 messages user + 2 messages assistant = 4 messages persistés
    detail = await async_client.get(f"/api/v1/conversations/{conv_id}")
    assert detail.status_code == 200
    messages = detail.json()["messages"]
    assert len(messages) == 4
    roles = [m["role"] for m in messages]
    assert roles == ["user", "assistant", "user", "assistant"]


async def test_chat_unknown_conversation_returns_404(
    async_client: AsyncClient,
) -> None:
    resp = await async_client.post(
        "/api/v1/chat",
        json={"message": "Salut", "conversation_id": "does-not-exist"},
    )
    assert resp.status_code == 404


async def test_list_conversations(async_client: AsyncClient) -> None:
    await async_client.post("/api/v1/chat", json={"message": "A"})
    resp = await async_client.get("/api/v1/conversations")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


async def test_empty_message_rejected(async_client: AsyncClient) -> None:
    resp = await async_client.post("/api/v1/chat", json={"message": ""})
    assert resp.status_code == 422
