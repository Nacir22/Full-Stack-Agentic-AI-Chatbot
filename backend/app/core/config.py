"""Configuration centralisée de l'application.

Toutes les valeurs proviennent de variables d'environnement (fichier `.env` à la
racine du dépôt en local, variables injectées par Docker/CI en production).
**Aucun secret n'est écrit en dur** : ce module se contente de les *lire* et de
les *valider* via Pydantic.

Usage :
    from app.core.config import get_settings
    settings = get_settings()
    settings.LLM_PROVIDER  # -> "openai"
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# config.py -> core -> app -> backend -> racine du dépôt
ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    """Schéma typé de toute la configuration applicative."""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # ignore les variables non déclarées (ex. POSTGRES_*)
    )

    # --- Application -------------------------------------------------------
    APP_ENV: Literal["development", "production"] = "development"
    APP_NAME: str = "agentic-chatbot"
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000"

    # --- LLM ---------------------------------------------------------------
    LLM_PROVIDER: Literal["openai", "mistral", "ollama"] = "openai"
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.2
    OPENAI_API_KEY: str | None = None
    MISTRAL_API_KEY: str | None = None
    OLLAMA_BASE_URL: str = "http://localhost:11434/v1"

    # --- Embeddings --------------------------------------------------------
    EMBEDDING_PROVIDER: Literal["openai", "huggingface"] = "openai"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # --- LangSmith ---------------------------------------------------------
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: str | None = None
    LANGCHAIN_PROJECT: str = "agentic-chatbot"

    # --- Base de données ---------------------------------------------------
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"

    # --- Vector store (ChromaDB) ------------------------------------------
    CHROMA_PATH: str = "./data/chroma"
    CHROMA_COLLECTION: str = "documents"

    # --- RAG ---------------------------------------------------------------
    RAG_CHUNK_SIZE: int = 1000
    RAG_CHUNK_OVERLAP: int = 150
    RAG_TOP_K: int = 4

    @field_validator("BACKEND_CORS_ORIGINS")
    @classmethod
    def _strip_origins(cls, v: str) -> str:
        return v.strip()

    @property
    def cors_origins(self) -> list[str]:
        """Liste des origines autorisées (séparées par des virgules dans .env)."""
        return [o.strip() for o in self.BACKEND_CORS_ORIGINS.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


@lru_cache
def get_settings() -> Settings:
    """Retourne une instance unique (mise en cache) de la configuration."""
    return Settings()
