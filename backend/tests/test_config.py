"""Tests de la configuration (Settings)."""

from __future__ import annotations

from app.core.config import Settings, get_settings


def test_defaults_are_sane() -> None:
    s = get_settings()
    assert s.APP_NAME
    assert s.LLM_PROVIDER in {"openai", "mistral", "ollama"}
    assert s.RAG_TOP_K >= 1


def test_cors_origins_parsing() -> None:
    s = Settings(BACKEND_CORS_ORIGINS="http://a.com, http://b.com ")
    assert s.cors_origins == ["http://a.com", "http://b.com"]


def test_is_production_flag() -> None:
    assert Settings(APP_ENV="production").is_production is True
    assert Settings(APP_ENV="development").is_production is False
