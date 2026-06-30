"""Base déclarative SQLAlchemy.

Toutes les tables héritent de `Base`. `Base.metadata` est la source de vérité
utilisée par Alembic pour générer les migrations : il suffit donc d'importer les
modèles (cf. `app/models/__init__.py`) pour qu'ils soient pris en compte.
"""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Classe de base déclarative commune à tous les modèles ORM."""
