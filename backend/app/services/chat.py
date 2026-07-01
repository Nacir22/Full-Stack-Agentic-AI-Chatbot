"""Service de chat : orchestre l'agent (avec outils) et la persistance.

Pipeline d'un tour :
  1. retrouver / créer la conversation ;
  2. enregistrer le message utilisateur ;
  3. construire le contexte via le `MemoryManager` ;
  4. construire les outils (RAG, mémoire, API externe) liés à cette requête ;
  5. exécuter le graphe agentique (avec routage conditionnel vers les outils) ;
  6. enregistrer et renvoyer la réponse.
"""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langchain_core.vectorstores import VectorStore
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.graph import build_agent_graph
from app.models import Conversation, Message, MessageRole
from app.services.conversation import ConversationService
from app.services.memory import MemoryManager
from app.tools.registry import build_tools


class ConversationNotFoundError(Exception):
    """Levée quand un conversation_id fourni n'existe pas."""


class ChatService:
    def __init__(
        self,
        db: AsyncSession,
        model: BaseChatModel,
        store: VectorStore | None = None,
        memory: MemoryManager | None = None,
    ) -> None:
        self.conversations = ConversationService(db)
        self.model = model
        self.store = store
        self.memory = memory or MemoryManager(model=model)

    async def handle(
        self, message: str, conversation_id: str | None = None
    ) -> tuple[Conversation, Message, str]:
        if conversation_id:
            conversation = await self.conversations.get(conversation_id)
            if conversation is None:
                raise ConversationNotFoundError(conversation_id)
        else:
            conversation = await self.conversations.create()

        await self.conversations.add_message(
            conversation.id, MessageRole.USER.value, message
        )

        context = await self.memory.build_context(
            await self.conversations.get_history(conversation.id)
        )

        tools = (
            build_tools(
                store=self.store,
                conversation_service=self.conversations,
                conversation_id=conversation.id,
            )
            if self.store is not None
            else []
        )

        graph = build_agent_graph(self.model, tools)
        result = await graph.ainvoke({"messages": context})
        answer = result["messages"][-1].content

        assistant_message = await self.conversations.add_message(
            conversation.id, MessageRole.ASSISTANT.value, answer
        )
        return conversation, assistant_message, answer
