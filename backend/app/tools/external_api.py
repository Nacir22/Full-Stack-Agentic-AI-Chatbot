"""Outil d'appel à une API externe : météo (Open-Meteo, sans clé).

Exemple d'intégration d'un service tiers dans l'agent. Open-Meteo est gratuit et
sans authentification. La gestion d'erreurs est volontairement défensive : toute
défaillance réseau renvoie un message exploitable par le LLM plutôt qu'une
exception qui casserait le workflow.
"""

from __future__ import annotations

import httpx
from langchain_core.tools import BaseTool, StructuredTool

_OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


async def get_weather(latitude: float, longitude: float) -> str:
    """Météo actuelle (température, vent) pour des coordonnées géographiques."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": True,
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(_OPEN_METEO_URL, params=params)
            response.raise_for_status()
            data = response.json()
        current = data["current_weather"]
        return (
            f"Température : {current['temperature']} °C, "
            f"vent : {current['windspeed']} km/h."
        )
    except Exception as exc:  # noqa: BLE001 - on renvoie l'erreur au LLM
        return f"Erreur lors de l'appel météo : {exc}"


weather_tool: BaseTool = StructuredTool.from_function(
    coroutine=get_weather,
    name="get_weather",
    description=(
        "Donne la météo actuelle pour des coordonnées (latitude, longitude). "
        "Arguments : latitude (float), longitude (float)."
    ),
)
