r"""Construction du graphe LangGraph.

Version **Phase 6** : l'agent peut appeler des outils. Le routage est
conditionnel — après le nœud `agent`, on va vers `tools` si le LLM a demandé un
outil, sinon on termine.

    START --> agent --(tool calls ?)--> tools --> agent
                     \--(sinon)--------------------> END

Robustesse : si le modèle ne supporte pas `bind_tools` (ex. faux modèle de test),
on retombe proprement sur un agent sans outils.
"""

from __future__ import annotations

from collections.abc import Sequence

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from app.agents.state import AgentState


def build_agent_graph(
    model: BaseChatModel, tools: Sequence[BaseTool] | None = None
) -> CompiledStateGraph:
    """Compile le graphe agentique, avec outils si le modèle les supporte."""
    tool_list: list[BaseTool] = list(tools or [])
    bound_model: BaseChatModel = model

    if tool_list:
        try:
            bound_model = model.bind_tools(tool_list)
        except NotImplementedError:
            bound_model = model
            tool_list = []

    async def call_model(state: AgentState) -> dict:
        response = await bound_model.ainvoke(state["messages"])
        return {"messages": [response]}

    builder = StateGraph(AgentState)
    builder.add_node("agent", call_model)
    builder.add_edge(START, "agent")

    if tool_list:
        builder.add_node("tools", ToolNode(tool_list))
        # tools_condition renvoie "tools" s'il y a des tool_calls, sinon END.
        builder.add_conditional_edges("agent", tools_condition)
        builder.add_edge("tools", "agent")
    else:
        builder.add_edge("agent", END)

    return builder.compile()
