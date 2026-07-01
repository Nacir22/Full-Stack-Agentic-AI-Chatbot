"""Outil RAG : recherche dans les documents indexés.

Fabriqué en *closure* autour du vector store courant : le tool exposé au LLM ne
prend qu'une requête textuelle, le store est capturé à la construction. Toute
erreur est capturée et renvoyée sous forme de texte (l'agent ne doit pas crasher
si la recherche échoue).
"""

from __future__ import annotations

from langchain_core.tools import BaseTool, StructuredTool
from langchain_core.vectorstores import VectorStore

from app.rag.pipeline import search


def make_rag_search_tool(store: VectorStore, top_k: int) -> BaseTool:
    async def rag_search(query: str) -> str:
        """Recherche des passages pertinents dans les documents de l'utilisateur."""
        try:
            docs = await search(store, query, top_k)
        except Exception as exc:  # noqa: BLE001 - on renvoie l'erreur au LLM
            return f"Erreur lors de la recherche documentaire : {exc}"
        if not docs:
            return "Aucun passage pertinent trouvé dans les documents."
        return "\n\n".join(
            f"[{i + 1}] {d.page_content}" for i, d in enumerate(docs)
        )

    return StructuredTool.from_function(
        coroutine=rag_search,
        name="rag_search",
        description=(
            "Recherche des informations dans les documents fournis par "
            "l'utilisateur. À utiliser dès que la question porte sur le contenu "
            "de documents. Argument : query (str)."
        ),
    )
