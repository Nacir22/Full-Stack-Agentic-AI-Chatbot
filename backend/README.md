# Backend — Full-Stack Agentic AI Chatbot

API FastAPI du chatbot agentique. Voir le [README principal](../README.md) pour
la vue d'ensemble et la roadmap.

## Démarrage rapide (local)

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

- API : http://localhost:8000
- Swagger UI : http://localhost:8000/docs
- Health : http://localhost:8000/health

## Configuration

La configuration est lue depuis le fichier `.env` à la **racine du dépôt**
(voir `../.env.example`). Aucun secret n'est codé en dur — tout passe par
`app/core/config.py` (`Settings` Pydantic).

## Structure (Phase 1)

```
app/
├── core/
│   ├── config.py     # Settings Pydantic (lecture .env)
│   └── logging.py    # configuration du logging
├── api/v1/
│   ├── health.py     # GET /health
│   └── router.py     # agrégateur des routeurs v1
├── schemas/
│   └── health.py     # DTO de la route health
└── main.py           # factory FastAPI + montage des routeurs
tests/
├── conftest.py       # fixture client de test
└── test_health.py    # tests de /health
```

## Tests

```bash
cd backend
pytest          # ou: pytest -q
```
