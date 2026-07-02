"""Tests des factories LLM et embeddings (branches d'erreur, sans réseau)."""

from __future__ import annotations

import os
import types

import pytest

from app.core import llm
from app.rag import embeddings


def test_build_chat_model_unknown_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = types.SimpleNamespace(
        LLM_PROVIDER="bogus",
        LLM_MODEL="x",
        LLM_TEMPERATURE=0.0,
        OPENAI_API_KEY=None,
        MISTRAL_API_KEY=None,
        OLLAMA_BASE_URL="",
    )
    monkeypatch.setattr(llm, "get_settings", lambda: fake)
    with pytest.raises(ValueError):
        llm.build_chat_model()


def test_configure_langsmith_sets_env(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = types.SimpleNamespace(
        LANGCHAIN_TRACING_V2=True,
        LANGCHAIN_API_KEY="secret-key",
        LANGCHAIN_PROJECT="proj",
    )
    monkeypatch.setattr(llm, "get_settings", lambda: fake)
    monkeypatch.delenv("LANGCHAIN_API_KEY", raising=False)
    llm.configure_langsmith()
    assert os.environ["LANGCHAIN_API_KEY"] == "secret-key"
    assert os.environ["LANGCHAIN_PROJECT"] == "proj"


def test_configure_langsmith_noop_without_key(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = types.SimpleNamespace(
        LANGCHAIN_TRACING_V2=False, LANGCHAIN_API_KEY=None, LANGCHAIN_PROJECT="p"
    )
    monkeypatch.setattr(llm, "get_settings", lambda: fake)
    monkeypatch.delenv("LANGCHAIN_API_KEY", raising=False)
    llm.configure_langsmith()
    assert "LANGCHAIN_API_KEY" not in os.environ


def test_build_embeddings_unknown_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = types.SimpleNamespace(
        EMBEDDING_PROVIDER="bogus", EMBEDDING_MODEL="x", OPENAI_API_KEY=None
    )
    monkeypatch.setattr(embeddings, "get_settings", lambda: fake)
    with pytest.raises(ValueError):
        embeddings.build_embeddings()
