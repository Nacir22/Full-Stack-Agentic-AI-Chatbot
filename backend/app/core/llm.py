"""Factory de modèle de chat multi-fournisseur.

Le code métier (l'agent) ne connaît jamais le fournisseur concret : il reçoit un
`BaseChatModel` LangChain. On bascule OpenAI / Mistral / Llama-via-Ollama
uniquement via `LLM_PROVIDER` dans `.env`. Les imports des clients sont **lazy**
pour ne pas exiger toutes les librairies à la fois.
"""

from __future__ import annotations

import os

from langchain_core.language_models import BaseChatModel

from app.core.config import get_settings


def build_chat_model() -> BaseChatModel:
    """Construit le modèle de chat correspondant au provider configuré."""
    settings = get_settings()
    provider = settings.LLM_PROVIDER

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            api_key=settings.OPENAI_API_KEY,
        )

    if provider == "mistral":
        from langchain_mistralai import ChatMistralAI

        return ChatMistralAI(
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            api_key=settings.MISTRAL_API_KEY,
        )

    if provider == "ollama":
        # Ollama expose une API compatible OpenAI -> on réutilise ChatOpenAI.
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            base_url=settings.OLLAMA_BASE_URL,
            api_key="ollama",  # placeholder requis par le client
        )

    raise ValueError(f"LLM_PROVIDER non supporté : {provider!r}")


def get_chat_model() -> BaseChatModel:
    """Dépendance FastAPI (surchargée par un faux modèle dans les tests)."""
    return build_chat_model()


def configure_langsmith() -> None:
    """Active le tracing LangSmith en propageant la config vers l'environnement.

    LangChain lit ses variables depuis `os.environ`. On les y injecte si le
    tracing est activé et qu'une clé est fournie (sinon on ne touche à rien).
    """
    settings = get_settings()
    if settings.LANGCHAIN_TRACING_V2 and settings.LANGCHAIN_API_KEY:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
        os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT
