"""Configuration du logging applicatif.

Un logging structuré et cohérent est indispensable en production pour relier les
traces (LangSmith) aux logs serveur. On configure un format simple et lisible,
piloté par `LOG_LEVEL`.
"""

from __future__ import annotations

import logging
import sys

from app.core.config import get_settings

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def setup_logging() -> None:
    """Initialise le logging racine selon LOG_LEVEL."""
    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format=_LOG_FORMAT,
        stream=sys.stdout,
        force=True,
    )
    # Réduit le bruit des librairies tierces verbeuses.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Raccourci pour obtenir un logger nommé."""
    return logging.getLogger(name)
