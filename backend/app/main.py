"""Point d'entrée de l'application FastAPI.

Responsabilités de ce module :
  * créer l'instance FastAPI (titre, version, docs) ;
  * configurer le logging et le CORS ;
  * monter les routeurs de l'API (préfixe /api/v1) ;
  * exposer /health à la racine pour les probes d'infrastructure.

La logique métier vit dans les services/agents, pas ici : `main.py` se contente
de câbler l'application.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.v1.health import router as health_router
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.llm import configure_langsmith
from app.core.logging import get_logger, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Hook de cycle de vie : exécuté au démarrage et à l'arrêt."""
    setup_logging()
    configure_langsmith()
    logger = get_logger("app.startup")
    settings = get_settings()
    logger.info(
        "Démarrage de %s v%s (env=%s, llm=%s)",
        settings.APP_NAME,
        __version__,
        settings.APP_ENV,
        settings.LLM_PROVIDER,
    )
    yield
    logger.info("Arrêt de l'application")


def create_app() -> FastAPI:
    """Factory d'application : facilite les tests et la configuration multiple."""
    settings = get_settings()

    app = FastAPI(
        title="Full-Stack Agentic AI Chatbot",
        version=__version__,
        description="API du chatbot agentique (LangGraph + RAG + FastAPI).",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # /health à la racine (probe infra) + sous /api/v1 (cohérence API)
    app.include_router(health_router)
    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()
