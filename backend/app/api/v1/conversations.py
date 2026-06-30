"""Routes de lecture des conversations."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.conversation import ConversationDetail, ConversationOut, MessageOut
from app.services.conversation import ConversationService

router = APIRouter()


@router.get("", response_model=list[ConversationOut], summary="Lister les conversations")
async def list_conversations(
    db: AsyncSession = Depends(get_db),
) -> list[ConversationOut]:
    conversations = await ConversationService(db).list()
    return [ConversationOut.model_validate(c) for c in conversations]


@router.get(
    "/{conversation_id}",
    response_model=ConversationDetail,
    summary="Détail d'une conversation (avec messages)",
)
async def get_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
) -> ConversationDetail:
    service = ConversationService(db)
    conversation = await service.get(conversation_id)
    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation introuvable"
        )
    messages = await service.get_history(conversation_id)
    return ConversationDetail(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        messages=[MessageOut.model_validate(m) for m in messages],
    )
