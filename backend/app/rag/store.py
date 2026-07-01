"""Accès au vector store ChromaDB.

Le store est exposé via l'interface `VectorStore` de LangChain : le pipeline et
les tools ne dépendent donc pas de Chroma directement (on peut injecter un store
en mémoire dans les tests). L'import de Chroma est **lazy** pour ne pas exiger
`chromadb` tant qu'on ne s'en sert pas.
"""

from __future__ import annotations

from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore

from app.core.config import get_settings
from app.rag.embeddings import get_embeddings


def build_vector_store(embeddings: Embeddings) -> VectorStore:
    """Instancie un store Chroma persistant (dossier `CHROMA_PATH`)."""
    from langchain_chroma import Chroma

    settings = get_settings()
    return Chroma(
        collection_name=settings.CHROMA_COLLECTION,
        embedding_function=embeddings,
        persist_directory=settings.CHROMA_PATH,
    )


def get_vector_store() -> VectorStore:
    """Dépendance FastAPI (surchargée par un store en mémoire dans les tests).

    Sans paramètre : FastAPI ne doit pas tenter d'en faire un champ de requête.
    Les embeddings sont résolus en interne via la factory dédiée.
    """
    return build_vector_store(get_embeddings())
