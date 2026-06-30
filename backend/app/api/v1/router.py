"""Agrégateur des routeurs de l'API v1.

Chaque domaine déclare son propre routeur ; on les monte ici afin que `main.py`
n'ait qu'un seul `include_router` à appeler.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import chat, conversations, health

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(
    conversations.router, prefix="/conversations", tags=["conversations"]
)

# Phase 5 : documents / upload
# api_router.include_router(documents.router)
