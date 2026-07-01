"""Outil de mémoire conversationnelle.

Permet à l'agent de *retrouver* des messages antérieurs de la conversation
courante (recherche par sous-chaîne, simple et déterministe). Fabriqué en
closure autour du service de conversation et de l'`conversation_id` du tour.
"""

from __future__ import annotations

from langchain_core.tools import BaseTool, StructuredTool

from app.services.conversation import ConversationService


def make_conversation_memory_tool(
    conversation_service: ConversationService, conversation_id: str
) -> BaseTool:
    async def search_conversation(query: str) -> str:
        """Retrouve dans l'historique de la conversation les messages contenant `query`."""
        history = await conversation_service.get_history(conversation_id)
        needle = query.lower().strip()
        matches = [m for m in history if needle in m.content.lower()]
        if not matches:
            return "Aucun message antérieur ne correspond."
        return "\n".join(f"{m.role}: {m.content}" for m in matches[-5:])

    return StructuredTool.from_function(
        coroutine=search_conversation,
        name="search_conversation",
        description=(
            "Recherche dans l'historique de la conversation en cours pour se "
            "souvenir de ce qui a déjà été dit. Argument : query (str)."
        ),
    )
