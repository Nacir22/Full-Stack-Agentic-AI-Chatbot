"""Tests du MemoryManager (fenêtrage et résumé)."""

from __future__ import annotations

from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.messages import SystemMessage

from app.models import Message, MessageRole
from app.services.memory import SYSTEM_PROMPT, MemoryManager


def _history(n: int) -> list[Message]:
    """Construit n messages alternés user/assistant (objets ORM non persistés)."""
    history: list[Message] = []
    for i in range(n):
        role = MessageRole.USER.value if i % 2 == 0 else MessageRole.ASSISTANT.value
        history.append(Message(conversation_id="c", role=role, content=f"msg-{i}"))
    return history


async def test_window_keeps_only_recent_messages() -> None:
    manager = MemoryManager(strategy="window", window_size=4)
    context = await manager.build_context(_history(10))

    # 1 system prompt + 4 messages récents
    assert isinstance(context[0], SystemMessage)
    assert context[0].content == SYSTEM_PROMPT
    assert len(context) == 5
    assert context[-1].content == "msg-9"
    assert context[1].content == "msg-6"


async def test_window_shorter_than_size_keeps_all() -> None:
    manager = MemoryManager(strategy="window", window_size=10)
    context = await manager.build_context(_history(3))
    assert len(context) == 1 + 3


async def test_summary_strategy_inserts_summary() -> None:
    fake = FakeListChatModel(responses=["RÉSUMÉ_DES_ANCIENS"])
    manager = MemoryManager(strategy="summary", window_size=2, model=fake)
    context = await manager.build_context(_history(6))

    # system prompt + message de résumé + 2 récents
    assert context[0].content == SYSTEM_PROMPT
    assert isinstance(context[1], SystemMessage)
    assert "RÉSUMÉ_DES_ANCIENS" in context[1].content
    assert context[-1].content == "msg-5"
    assert len(context) == 1 + 1 + 2


async def test_summary_without_overflow_skips_summary() -> None:
    fake = FakeListChatModel(responses=["NE_DEVRAIT_PAS_SERVIR"])
    manager = MemoryManager(strategy="summary", window_size=10, model=fake)
    context = await manager.build_context(_history(4))
    # Pas de débordement -> pas de résumé, juste system + 4 messages
    assert len(context) == 1 + 4
    assert all(
        "NE_DEVRAIT_PAS_SERVIR" not in str(m.content) for m in context
    )
