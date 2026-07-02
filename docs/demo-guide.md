# Guide de démonstration

Scénario de 5–10 minutes pour présenter le projet (entretien, portfolio). Il met
en valeur les points techniques : API, agent, RAG, mémoire, outils, observabilité.

## Préparation (avant la démo)

```bash
# 1) Backend + DB + frontend en une commande
cp .env.example .env            # renseigner OPENAI_API_KEY (ou MISTRAL_API_KEY)
docker compose up --build

# (Optionnel) activer LangSmith dans .env pour montrer les traces :
#   LANGCHAIN_TRACING_V2=true
#   LANGCHAIN_API_KEY=ls__...
```

Onglets à ouvrir : le frontend (`http://localhost:3000`), Swagger
(`http://localhost:8000/docs`), et LangSmith si activé.

## Déroulé

### 1. Vue d'ensemble (1 min)
Montrer le `README` et le diagramme d'architecture : frontend → API FastAPI →
agent LangGraph → outils / RAG / LLM, avec PostgreSQL et ChromaDB. Insister sur la
séparation des responsabilités et le caractère multi-fournisseur du LLM.

### 2. Conversation simple (1 min)
Dans le frontend, poser une question générale. Montrer la réponse, l'état de
chargement, et la persistance : recharger la page → la conversation est dans
l'historique (barre latérale).

### 3. Mémoire conversationnelle (1 min)
Dire « Je m'appelle Hakim », puis dans un message suivant « Comment je
m'appelle ? ». L'agent se souvient : démontre le `MemoryManager` et le
rechargement de l'historique par session (`conversation_id`).

### 4. RAG — répondre sur un document (2 min)
Uploader un document (`.txt`/`.md`/`.pdf`) via la barre latérale. Poser une
question dont la réponse est dans le document. Montrer que l'agent appelle
l'outil `rag_search` et cite le passage. C'est le cœur « augmenté par documents ».

### 5. Outils & routage agentique (1 min)
Sur Swagger ou LangSmith, montrer qu'une question documentaire déclenche
`rag_search`, alors qu'une question générale non — c'est le **routage
conditionnel** LangGraph (`agent → tools → agent`).

### 6. Observabilité (1 min, si LangSmith actif)
Ouvrir une trace `chat_turn` dans LangSmith : arbre des étapes, appel d'outil,
latences, tokens. Filtrer par `conversation_id`.

### 7. Qualité & déploiement (1 min)
Montrer `pytest` (37 tests, ~87 %), `ruff check` vert, et les workflows GitHub
Actions (CI + déploiement AWS ECR/EC2 avec healthcheck).

## Messages clés à faire passer

- Architecture **modulaire et testée**, pensée production (Docker, migrations,
  CI/CD, monitoring).
- Agent **réellement agentique** : il décide d'utiliser des outils, il n'exécute
  pas une chaîne figée.
- **Multi-fournisseur** LLM et **aucun secret dans le code**.
- Tests **sans clé API ni réseau** (LLM/embeddings simulés) → CI rapide et fiable.
