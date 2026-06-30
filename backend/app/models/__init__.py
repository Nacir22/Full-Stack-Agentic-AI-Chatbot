"""Modèles ORM.

Importer ce module suffit à enregistrer toutes les tables dans
`Base.metadata` — c'est ce que fait Alembic pour l'autogénération des migrations.
"""

from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.models.user import User

__all__ = ["User", "Conversation", "Message", "MessageRole"]
