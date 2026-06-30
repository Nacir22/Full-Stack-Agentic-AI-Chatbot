"""Construction du graphe LangGraph.

Version **Phase 3 (minimale)** : un seul nœud `agent` qui appelle le LLM et
renvoie sa réponse.

    START --> agent --> END

Le routage conditionnel et les nœuds d'outils (RAG, mémoire, API) seront
ajoutés en Phase 6 ; la structure en graphe est déjà là pour les accueillir
sans refonte.
"""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.agents.state import AgentState


def build_agent_graph(model: BaseChatModel) -> CompiledStateGraph:
    """Compile le graphe agentique autour d'un modèle de chat donné."""

    async def call_model(state: AgentState) -> dict:
        """Nœud principal : interroge le LLM avec l'historique courant."""
        response = await model.ainvoke(state["messages"])
        return {"messages": [response]}

    builder = StateGraph(AgentState)
    builder.add_node("agent", call_model)
    builder.add_edge(START, "agent")
    builder.add_edge("agent", END)
    return builder.compile()
