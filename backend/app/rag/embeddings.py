"""Factory d'embeddings multi-fournisseur.

Même principe que la factory LLM : le pipeline ne connaît qu'une interface
`Embeddings` LangChain. On choisit OpenAI ou HuggingFace via `EMBEDDING_PROVIDER`.
Imports **lazy** pour ne pas exiger les librairies lourdes (sentence-transformers)
quand on ne les utilise pas.
"""

from __future__ import annotations

from langchain_core.embeddings import Embeddings

from app.core.config import get_settings


def build_embeddings() -> Embeddings:
    settings = get_settings()
    provider = settings.EMBEDDING_PROVIDER

    if provider == "openai":
        from langchain_openai import OpenAIEmbeddings

        return OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL, api_key=settings.OPENAI_API_KEY
        )

    if provider == "huggingface":
        from langchain_huggingface import HuggingFaceEmbeddings

        return HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)

    raise ValueError(f"EMBEDDING_PROVIDER non supporté : {provider!r}")


def get_embeddings() -> Embeddings:
    """Dépendance FastAPI (surchargée par un faux embedder dans les tests)."""
    return build_embeddings()
