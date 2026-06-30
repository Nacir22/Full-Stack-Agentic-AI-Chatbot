#!/usr/bin/env bash
# Lance le backend FastAPI en local (hors Docker), avec rechargement à chaud.
# Usage : ./scripts/run_backend_local.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/backend"

# Environnement virtuel
if [ ! -d ".venv" ]; then
  echo "==> Création de l'environnement virtuel"
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

echo "==> Installation des dépendances"
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

echo "==> Démarrage de l'API sur http://localhost:8000 (Swagger: /docs)"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
