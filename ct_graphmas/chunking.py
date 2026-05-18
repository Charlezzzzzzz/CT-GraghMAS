"""Corpus chunking for teaching documents."""

from __future__ import annotations

import re


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _split_sentences(paragraph: str) -> list[str]:
    parts = re.split(r"(?<=[。！？!?；;.!?])\s*", paragraph.strip())
    return [part.strip() for part in parts if part.strip()]


def chunk_text(text: str, max_chars: int = 520, overlap_chars: int = 80) -> list[str]:
    text = clean_text(text)
    if not text:
        return []

    units: list[str] = []
    for paragraph in re.split(r"\n\s*\n", text):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        if len(paragraph) <= max_chars:
            units.append(paragraph)
            continue
        units.extend(_split_sentences(paragraph))

    chunks: list[str] = []
    current = ""
    for unit in units:
        if not current:
            current = unit
            continue
        if len(current) + 1 + len(unit) <= max_chars:
            current = f"{current}\n{unit}"
            continue
        chunks.append(current)
        overlap = current[-overlap_chars:] if overlap_chars > 0 else ""
        current = f"{overlap}\n{unit}".strip()

    if current:
        chunks.append(current)

    normalized: list[str] = []
    for chunk in chunks:
        chunk = chunk.strip()
        if len(chunk) > max_chars * 1.4:
            normalized.extend(chunk[i : i + max_chars] for i in range(0, len(chunk), max_chars - overlap_chars))
        else:
            normalized.append(chunk)
    return [chunk for chunk in normalized if chunk.strip()]
