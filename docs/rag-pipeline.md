# Pipeline RAG (à détailler en Phase 5)

Stub de documentation. Le pipeline complet (upload → extraction → nettoyage →
chunking → embeddings → ChromaDB → retriever → réponse augmentée) sera implémenté
et documenté en Phase 5.

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
