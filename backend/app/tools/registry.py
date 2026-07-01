"""Assemblage de la liste d'outils disponibles pour l'agent.

Certains outils dépendent du contexte de la requête (store vectoriel,
conversation courante) : ils sont donc construits par requête, pas au démarrage.
Ajouter un nouvel outil = l'implémenter dans `app/tools/` puis l'ajouter ici.
"""

from __future__ import annotations

from langchain_core.tools import BaseTool
from langchain_core.vectorstores import VectorStore

from app.core.config import get_settings
from app.services.conversation import ConversationService
from app.tools.external_api import weather_tool
from app.tools.memory_tool import make_conversation_memory_tool
from app.tools.rag_search import make_rag_search_tool


def build_tools(
    *,
    store: VectorStore,
    conversation_service: ConversationService,
    conversation_id: str,
) -> list[BaseTool]:
    settings = get_settings()
    return [
        make_rag_search_tool(store, settings.RAG_TOP_K),
        make_conversation_memory_tool(conversation_service, conversation_id),
        weather_tool,
    ]
