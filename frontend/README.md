# Frontend — Agentic AI Chatbot

Interface de chat **Next.js (App Router) + TypeScript + Tailwind**. Voir le
[README principal](../README.md) pour la vue d'ensemble.

## Démarrage

```bash
cd frontend
cp .env.local.example .env.local     # ajuster l'URL de l'API si besoin
npm install
npm run dev
```

Ouvrir http://localhost:3000 (le backend doit tourner sur http://localhost:8000).

## Configuration

`NEXT_PUBLIC_API_BASE_URL` (dans `.env.local`) pointe vers l'API FastAPI. Par
défaut `http://localhost:8000/api/v1`.

## Structure

```
src/
├── app/
│   ├── layout.tsx      # layout racine + Tailwind
│   ├── page.tsx        # monte <ChatApp/>
│   └── globals.css
├── components/
│   ├── ChatApp.tsx     # état + orchestration (messages, docs, erreurs, loading)
│   ├── MessageBubble.tsx
│   ├── Composer.tsx    # saisie + envoi
│   └── Sidebar.tsx     # historique des conversations + upload de documents
├── services/
│   └── api.ts          # client API isolé (seul point qui parle au backend)
└── lib/
    └── types.ts        # types alignés sur les schémas Pydantic
```

## Fonctionnalités

- Zone de chat avec messages utilisateur / assistant.
- État de chargement (« L'agent réfléchit… »).
- Historique des conversations (barre latérale), reprise d'un fil existant.
- Upload de documents (.txt, .md, .pdf) pour le RAG, liste et suppression.
- Affichage des erreurs API.
- Communication via un **service API séparé** (`services/api.ts`).

## Scripts

```bash
npm run dev     # développement (http://localhost:3000)
npm run build   # build de production
npm run start   # serveur de production
npm run lint    # lint
```
