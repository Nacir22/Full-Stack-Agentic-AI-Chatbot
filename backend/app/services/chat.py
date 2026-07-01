"""Service de chat : orchestre l'agent et la persistance.

Pipeline d'un tour de conversation :
  1. retrouver (ou créer) la conversation ;
  2. enregistrer le message utilisateur ;
  3. recharger l'historique et construire le contexte via le `MemoryManager`
     (fenêtrage / résumé — cf. Phase 4) ;
  4. exécuter le graphe agentique ;
  5. enregistrer la réponse de l'assistant et la renvoyer.
"""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.graph import build_agent_graph
from app.models import Conversation, Message, MessageRole
from app.services.conversation import ConversationService
from app.services.memory import MemoryManager


class ConversationNotFoundError(Exception):
    """Levée quand un conversation_id fourni n'existe pas."""


class ChatService:
    def __init__(
        self,
        db: AsyncSession,
        model: BaseChatModel,
        memory: MemoryManager | None = None,
    ) -> None:
        self.conversations = ConversationService(db)
        self.model = model
        # La mémoire utilise le même modèle (pour les résumés éventuels).
        self.memory = memory or MemoryManager(model=model)

    async def handle(
        self, message: str, conversation_id: str | None = None
    ) -> tuple[Conversation, Message, str]:
        # 1-2. conversation + message utilisateur
        if conversation_id:
            conversation = await self.conversations.get(conversation_id)
            if conversation is None:
                raise ConversationNotFoundError(conversation_id)
        else:
            conversation = await self.conversations.create()

        await self.conversations.add_message(
            conversation.id, MessageRole.USER.value, message
        )

        # 3. historique -> contexte (mémoire)
        history = await self.conversations.get_history(conversation.id)
        context = await self.memory.build_context(history)

        # 4. exécution du graphe agentique
        graph = build_agent_graph(self.model)
        result = await graph.ainvoke({"messages": context})
        answer = result["messages"][-1].content

        # 5. persistance de la réponse
        assistant_message = await self.conversations.add_message(
            conversation.id, MessageRole.ASSISTANT.value, answer
        )
        return conversation, assistant_message, answer
