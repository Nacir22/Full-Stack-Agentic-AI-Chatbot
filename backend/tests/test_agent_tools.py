"""Test du routage agentique : agent -> tools -> agent -> END.

On utilise un modèle scripté qui émet d'abord un appel d'outil (`rag_search`),
puis une réponse finale. Cela exerce le graphe complet sans vrai LLM.
"""

from __future__ import annotations

from typing import Any

import pytest
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.vectorstores import InMemoryVectorStore

from app.agents.graph import build_agent_graph
from app.rag.pipeline import ingest_text
from app.tools.rag_search import make_rag_search_tool


class ScriptedToolModel(BaseChatModel):
    """Faux modèle qui rejoue une liste d'AIMessage et supporte bind_tools."""

    responses: list[AIMessage]
    idx: int = 0

    @property
    def _llm_type(self) -> str:
        return "scripted-tool-model"

    def bind_tools(self, tools: Any, **kwargs: Any) -> "ScriptedToolModel":
        return self

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        message = self.responses[min(self.idx, len(self.responses) - 1)]
        self.idx += 1
        return ChatResult(generations=[ChatGeneration(message=message)])


@pytest.mark.asyncio
async def test_agent_calls_tool_then_answers() -> None:
    store = InMemoryVectorStore(DeterministicFakeEmbedding(size=32))
    await ingest_text(
        store, "doc-1", "Le projet utilise LangGraph pour l'orchestration. " * 5,
        chunk_size=120, chunk_overlap=20,
    )
    tool = make_rag_search_tool(store, top_k=2)

    model = ScriptedToolModel(
        responses=[
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "rag_search",
                        "args": {"query": "orchestration"},
                        "id": "call-1",
                        "type": "tool_call",
                    }
                ],
            ),
            AIMessage(content="D'après les documents : LangGraph orchestre l'agent."),
        ]
    )

    graph = build_agent_graph(model, [tool])
    result = await graph.ainvoke({"messages": [HumanMessage(content="Quelle orchestration ?")]})

    messages = result["messages"]
    assert any(isinstance(m, ToolMessage) for m in messages)  # l'outil a été exécuté
    assert messages[-1].content == "D'après les documents : LangGraph orchestre l'agent."


@pytest.mark.asyncio
async def test_agent_without_tools_answers_directly() -> None:
    model = ScriptedToolModel(responses=[AIMessage(content="Réponse directe.")])
    graph = build_agent_graph(model, [])
    result = await graph.ainvoke({"messages": [HumanMessage(content="Salut")]})
    assert result["messages"][-1].content == "Réponse directe."
