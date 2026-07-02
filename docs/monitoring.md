# Monitoring & observabilité — LangSmith

LangSmith trace **automatiquement** chaque exécution LangChain/LangGraph :
appels LLM, étapes du graphe, appels d'outils, latences et erreurs. Aucun code
d'instrumentation n'est nécessaire — il suffit d'activer le tracing par variables
d'environnement.

## 1. Activation

Créer un compte sur [smith.langchain.com](https://smith.langchain.com) et générer
une clé API, puis renseigner dans `.env` :

```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__...
LANGCHAIN_PROJECT=agentic-chatbot
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

Au démarrage, `configure_langsmith()` (dans `app/core/llm.py`, appelée par le
lifespan FastAPI) propage ces valeurs vers `os.environ` **uniquement si** le
tracing est activé et qu'une clé est fournie. Sans clé, l'application fonctionne
normalement, sans tracing.

## 2. Ce qui est tracé

| Élément | Détail |
|---|---|
| Appels LLM | prompt, réponse, tokens, latence, coût estimé |
| Étapes LangGraph | nœuds `agent` / `tools`, transitions, état des messages |
| Appels d'outils | `rag_search`, `search_conversation`, `get_weather` (entrées/sorties) |
| Erreurs | exceptions, tool calls échoués |
| Métadonnées | `run_name=chat_turn`, tags `agent`/`chat`, `conversation_id` |

L'ajout du `conversation_id` en métadonnée (dans `ChatService`) permet de
**filtrer les traces par conversation** dans l'UI LangSmith.

## 3. Lire une trace

Dans LangSmith → projet `agentic-chatbot` → onglet **Traces**. Chaque requête
`/chat` apparaît comme un run `chat_turn`. En le dépliant, on voit l'arbre :

```
chat_turn
├── agent (appel LLM)          ← décide : répondre ou appeler un outil ?
├── tools (si tool_calls)      ← exécution de rag_search / get_weather / ...
└── agent (appel LLM)          ← réponse finale à partir du résultat des outils
```

Chaque nœud affiche entrée, sortie, durée et tokens. C'est la vue idéale pour
comprendre *pourquoi* l'agent a (ou n'a pas) appelé un outil.

## 4. Déboguer un workflow agentique

- **L'agent n'appelle jamais l'outil attendu** → vérifier la trace du premier
  nœud `agent` : le LLM a-t-il émis un `tool_call` ? Sinon, améliorer la
  description de l'outil (elle guide le choix du LLM) ou le prompt système.
- **Un outil renvoie une erreur** → le nœud `tools` montre l'exception. Nos
  outils capturent leurs erreurs et renvoient un message : on le voit dans la
  sortie du tool.
- **Réponse lente** → comparer les latences par nœud pour isoler l'étape
  coûteuse (souvent l'appel LLM ou une recherche vectorielle).
- **Boucle d'outils** → si `agent ↔ tools` se répète trop, ajouter une limite de
  récursion (`graph.ainvoke(..., config={"recursion_limit": N})`).

## 5. Filtrer et analyser

- Filtre par tag (`agent`, `chat`) ou par métadonnée (`conversation_id=...`).
- Métriques agrégées : latence P50/P95, tokens, taux d'erreur par période.
- Les runs peuvent être ajoutés à des **datasets** pour de l'évaluation
  automatisée (piste d'amélioration future).

## 6. Bonnes pratiques

- Un projet LangSmith par environnement (`agentic-chatbot`,
  `agentic-chatbot-prod`) via `LANGCHAIN_PROJECT`.
- Ne jamais committer `LANGCHAIN_API_KEY` (déjà couvert par `.gitignore`).
- Désactiver le tracing (`LANGCHAIN_TRACING_V2=false`) en test pour éviter tout
  appel réseau — c'est le comportement par défaut du projet.
