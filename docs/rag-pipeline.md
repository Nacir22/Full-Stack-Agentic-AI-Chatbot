# Pipeline RAG

Le **RAG** (Retrieval-Augmented Generation) permet à l'agent de répondre à
partir de **tes documents** plutôt que de sa seule mémoire paramétrique. Deux
temps : l'**ingestion** (indexer les documents) et la **recherche** (retrouver
les passages pertinents au moment de répondre).

## Vue d'ensemble

```mermaid
graph LR
    A[Upload Document] --> B[Text Extraction]
    B --> C[Cleaning]
    C --> D[Chunking]
    D --> E[Embeddings]
    E --> F[ChromaDB]
    F --> G[Retriever]
    G --> H[Agent Response]
```

## Étapes (code)

| Étape | Module | Rôle |
|---|---|---|
| Extraction | `rag/loaders.py` | Texte depuis `.txt`/`.md` (décodage) ou `.pdf` (pypdf) |
| Nettoyage | `rag/loaders.py` | Normalise espaces et lignes vides |
| Chunking | `rag/chunking.py` | `RecursiveCharacterTextSplitter` (taille + chevauchement) |
| Embeddings | `rag/embeddings.py` | Factory OpenAI / HuggingFace (`EMBEDDING_PROVIDER`) |
| Stockage | `rag/store.py` | ChromaDB persistant (`CHROMA_PATH`, collection) |
| Recherche | `rag/pipeline.py` | `similarity_search(query, k=RAG_TOP_K)` |

## Pourquoi ces choix

**Chunking avec chevauchement** : un document entier dépasse la fenêtre du
modèle et dilue la pertinence. On coupe en morceaux (`RAG_CHUNK_SIZE`) sur des
frontières naturelles, avec un `RAG_CHUNK_OVERLAP` pour ne pas casser une idée à
cheval sur deux chunks.

**Embeddings** : chaque chunk est transformé en vecteur qui capture son sens. Une
question proche sémantiquement d'un chunk aura un vecteur proche → on la retrouve
par distance vectorielle, même sans mots-clés communs.

**Métadonnées + IDs déterministes** : chaque chunk porte `document_id` et
`chunk_index`, et son id vectoriel est `"<document_id>:<index>"`. On peut ainsi
**supprimer** tous les vecteurs d'un document proprement (`num_chunks` est stocké
en base), indépendamment du backend.

**Séparation SQL / vectoriel** : les métadonnées du document (nom, taille, statut,
nombre de chunks) vivent en SQL (`documents`) ; le texte des chunks et leurs
embeddings vivent dans Chroma. Chacun sa responsabilité.

## Endpoints

```text
POST   /api/v1/upload              # multipart "file" -> ingestion
GET    /api/v1/documents           # liste des documents indexés
DELETE /api/v1/documents/{id}      # supprime doc + vecteurs
```

## Configuration (.env)

```env
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
CHROMA_PATH=./data/chroma
CHROMA_COLLECTION=documents
RAG_CHUNK_SIZE=1000
RAG_CHUNK_OVERLAP=150
RAG_TOP_K=4
```

## Tests

Les tests utilisent un `InMemoryVectorStore` + `DeterministicFakeEmbedding` :
pas de ChromaDB, pas de réseau, résultats déterministes. Le cycle
ingest → search → delete et les endpoints upload/list/delete sont couverts.
