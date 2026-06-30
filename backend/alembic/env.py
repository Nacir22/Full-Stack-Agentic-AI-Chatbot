"""Environnement Alembic.

Choix d'implémentation : les migrations s'exécutent en mode **synchrone**, même
si l'application utilise un moteur async. On dérive une URL sync depuis
`DATABASE_URL` (ex. `sqlite+aiosqlite` -> `sqlite`). C'est plus simple et plus
robuste que de gérer un contexte async dans Alembic, et `render_as_batch=True`
assure la compatibilité des ALTER sous SQLite.
"""

from __future__ import annotations

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Importer les modèles peuple Base.metadata (cible de l'autogénération).
from app.core.config import get_settings
from app.db.base import Base
import app.models  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_sync_url() -> str:
    """Convertit l'URL applicative (async) en URL synchrone pour Alembic."""
    url = get_settings().DATABASE_URL
    return (
        url.replace("+aiosqlite", "")
        .replace("+asyncpg", "+psycopg")
    )


def run_migrations_offline() -> None:
    context.configure(
        url=get_sync_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_sync_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
