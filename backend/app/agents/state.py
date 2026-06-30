"""État partagé du graphe agentique.

LangGraph fait circuler un objet d'état entre les nœuds. Le réducteur
`add_messages` gère l'accumulation de l'historique : chaque nœud renvoie les
nouveaux messages, qui sont *ajoutés* à la liste plutôt que de l'écraser.
"""

from __future__ import annotations

from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """État circulant dans le graphe : l'historique des messages."""

    messages: Annotated[list[BaseMessage], add_messages]
