"""Découpage du texte en chunks pour l'indexation vectorielle.

Le chunking est un compromis : des chunks trop grands diluent la pertinence de la
recherche, trop petits perdent le contexte. Le `RecursiveCharacterTextSplitter`
coupe en priorité sur les frontières naturelles (paragraphes, phrases) et applique
un chevauchement (`overlap`) pour ne pas casser une idée à cheval sur deux chunks.
"""

from __future__ import annotations

from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """Découpe `text` en chunks non vides."""
    if not text.strip():
        return []
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return [c for c in splitter.split_text(text) if c.strip()]
