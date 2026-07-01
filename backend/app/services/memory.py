"""Mémoire conversationnelle.

Problème résolu : envoyer **tout** l'historique au LLM à chaque tour coûte cher
et finit par dépasser la fenêtre de contexte. Le `MemoryManager` construit le
contexte transmis au modèle selon une stratégie configurable :

* ``window``  — ne conserve que les `window_size` derniers messages ;
* ``summary`` — résume les messages les plus anciens (via le LLM) et garde les
  `window_size` messages récents tels quels.

Dans les deux cas un prompt système ouvre toujours le contexte. La conversation
est identifiée par son `conversation_id`, qui joue le rôle de **session**.
"""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)

from app.core.config import get_settings
from app.models import Message, MessageRole

SYSTEM_PROMPT = (
    "Tu es un assistant IA utile, précis et concis. "
    "Réponds dans la langue de l'utilisateur."
)

_SUMMARY_INSTRUCTION = (
    "Résume de façon concise les points clés de cet échange "
    "(faits, décisions, préférences) pour servir de mémoire à la suite de la "
    "conversation. Réponds uniquement par le résumé."
)


def message_to_langchain(message: Message) -> BaseMessage | None:
    """Convertit un message stocké en message LangChain (None si rôle ignoré)."""
    if message.role == MessageRole.USER.value:
        return HumanMessage(content=message.content)
    if message.role == MessageRole.ASSISTANT.value:
        return AIMessage(content=message.content)
    if message.role == MessageRole.SYSTEM.value:
        return SystemMessage(content=message.content)
    return None


class MemoryManager:
    """Construit le contexte LLM à partir de l'historique persistné."""

    def __init__(
        self,
        *,
        strategy: str | None = None,
        window_size: int | None = None,
        model: BaseChatModel | None = None,
    ) -> None:
        settings = get_settings()
        self.strategy = strategy or settings.MEMORY_STRATEGY
        self.window_size = window_size or settings.MEMORY_WINDOW_SIZE
        self.model = model

    async def build_context(self, history: list[Message]) -> list[BaseMessage]:
        """Retourne la liste de messages LangChain à passer à l'agent."""
        conversation = [
            lc for m in history if (lc := message_to_langchain(m)) is not None
        ]
        context: list[BaseMessage] = [SystemMessage(content=SYSTEM_PROMPT)]

        # Historique assez court, ou stratégie fenêtre : pas de résumé.
        if self.strategy != "summary" or len(conversation) <= self.window_size:
            context.extend(conversation[-self.window_size :])
            return context

        # Stratégie résumé : on condense ce qui dépasse la fenêtre.
        overflow = conversation[: -self.window_size]
        recent = conversation[-self.window_size :]
        summary = await self._summarize(overflow)
        context.append(
            SystemMessage(content=f"Résumé de la conversation précédente : {summary}")
        )
        context.extend(recent)
        return context

    async def _summarize(self, messages: list[BaseMessage]) -> str:
        if self.model is None:
            # Sans modèle on dégrade proprement vers une simple troncature.
            return "(résumé indisponible)"
        transcript = "\n".join(
            f"{'Utilisateur' if isinstance(m, HumanMessage) else 'Assistant'}: {m.content}"
            for m in messages
        )
        prompt = [
            SystemMessage(content=_SUMMARY_INSTRUCTION),
            HumanMessage(content=transcript),
        ]
        result = await self.model.ainvoke(prompt)
        return str(result.content)
