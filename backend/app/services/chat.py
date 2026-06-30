"""Service de chat : orchestre l'agent et la persistance.

Pipeline d'un tour de conversation :
  1. retrouver (ou créer) la conversation ;
  2. enregistrer le message utilisateur ;
  3. recharger l'historique et le convertir au format LangChain ;
  4. exécuter le graphe agentique ;
  5. enregistrer la réponse de l'assistant et la renvoyer.

L'étape 3 (rechargement de l'historique) donne déjà une mémoire conversationnelle
de base ; elle sera enrichie en Phase 4.
"""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.graph import build_agent_graph
from app.models import Conversation, Message, MessageRole
from app.services.conversation import ConversationService

SYSTEM_PROMPT = (
    "Tu es un assistant IA utile, précis et concis. "
    "Réponds dans la langue de l'utilisateur."
)


class ConversationNotFoundError(Exception):
    """Levée quand un conversation_id fourni n'existe pas."""


def _to_langchain_messages(history: list[Message]) -> list[BaseMessage]:
    """Convertit les messages stockés en messages LangChain."""
    messages: list[BaseMessage] = [SystemMessage(content=SYSTEM_PROMPT)]
    for msg in history:
        if msg.role == MessageRole.USER.value:
            messages.append(HumanMessage(content=msg.content))
        elif msg.role == MessageRole.ASSISTANT.value:
            messages.append(AIMessage(content=msg.content))
        elif msg.role == MessageRole.SYSTEM.value:
            messages.append(SystemMessage(content=msg.content))
    return messages


class ChatService:
    def __init__(self, db: AsyncSession, model: BaseChatModel) -> None:
        self.conversations = ConversationService(db)
        self.model = model

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

        # 3. historique -> format LangChain
        history = await self.conversations.get_history(conversation.id)
        lc_messages = _to_langchain_messages(history)

        # 4. exécution du graphe agentique
        graph = build_agent_graph(self.model)
        result = await graph.ainvoke({"messages": lc_messages})
        answer = result["messages"][-1].content

        # 5. persistance de la réponse
        assistant_message = await self.conversations.add_message(
            conversation.id, MessageRole.ASSISTANT.value, answer
        )
        return conversation, assistant_message, answer
