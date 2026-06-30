"""Route de santé (liveness probe).

Endpoint léger utilisé par Docker, le load balancer et le pipeline CI/CD pour
vérifier que le service répond. Volontairement sans dépendance externe (pas de
DB) afin de toujours répondre vite ; un check de readiness (DB/Chroma) viendra
plus tard.
"""

from __future__ import annotations

from fastapi import APIRouter

from app import __version__
from app.core.config import get_settings
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Liveness probe")
def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        app=settings.APP_NAME,
        version=__version__,
        environment=settings.APP_ENV,
    )
