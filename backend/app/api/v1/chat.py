"""Route POST /chat : un tour de conversation avec l'agent."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from langchain_core.language_models import BaseChatModel
from langchain_core.vectorstores import VectorStore
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.llm import get_chat_model
from app.db.session import get_db
from app.rag.store import get_vector_store
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat import ChatService, ConversationNotFoundError

router = APIRouter()


@router.post("", response_model=ChatResponse, summary="Envoyer un message à l'agent")
async def chat(
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db),
    model: BaseChatModel = Depends(get_chat_model),
    store: VectorStore = Depends(get_vector_store),
) -> ChatResponse:
    service = ChatService(db, model, store=store)
    try:
        conversation, message, answer = await service.handle(
            payload.message, payload.conversation_id
        )
    except ConversationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation introuvable : {exc}",
        ) from exc

    return ChatResponse(
        conversation_id=conversation.id,
        message_id=message.id,
        response=answer,
    )
