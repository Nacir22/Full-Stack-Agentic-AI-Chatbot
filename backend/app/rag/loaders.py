"""Extraction et nettoyage du texte des documents uploadés.

Supporte le texte brut / Markdown (décodage direct) et le PDF (via pypdf).
D'autres formats pourront être ajoutés ici sans toucher au reste du pipeline.
"""

from __future__ import annotations

import io
import re

_WHITESPACE_RE = re.compile(r"[ \t]+")
_BLANKLINES_RE = re.compile(r"\n{3,}")


def clean_text(text: str) -> str:
    """Normalise les espaces et supprime les lignes vides superflues."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _WHITESPACE_RE.sub(" ", text)
    text = _BLANKLINES_RE.sub("\n\n", text)
    return text.strip()


def _extract_pdf(data: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(data))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def extract_text(filename: str, data: bytes, content_type: str | None = None) -> str:
    """Retourne le texte nettoyé d'un fichier uploadé."""
    name = (filename or "").lower()
    is_pdf = name.endswith(".pdf") or content_type == "application/pdf"
    raw = _extract_pdf(data) if is_pdf else data.decode("utf-8", errors="ignore")
    return clean_text(raw)
