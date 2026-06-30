"""Tests de la route de santé."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_health_root(client: TestClient) -> None:
    """GET /health renvoie 200 et un statut ok."""
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["app"]
    assert body["version"]
    assert body["environment"] in {"development", "production"}


def test_health_v1(client: TestClient) -> None:
    """La même route est aussi exposée sous /api/v1."""
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_openapi_available(client: TestClient) -> None:
    """Le schéma OpenAPI (Swagger) est généré."""
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    assert "/health" in resp.json()["paths"]
