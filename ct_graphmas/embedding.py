"""Small deterministic text embedding utilities.

The project is intentionally dependency-light so it can run inside a thesis
defense demo machine without model downloads. The embedder is a signed hashing
vectorizer; it is not a neural embedding model, but it gives stable semantic-ish
retrieval over the uploaded corpus and can later be replaced by a local or API
embedding model behind the same interface.
"""

from __future__ import annotations

import hashlib
import math
import re
from collections import Counter

from .seed_data import CONCEPT_ALIASES


STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "this",
    "that",
    "from",
    "into",
    "your",
    "when",
    "where",
    "while",
    "我",
    "你",
    "他",
    "她",
    "它",
    "我们",
    "你们",
    "他们",
    "这个",
    "那个",
    "怎么",
    "如何",
    "一下",
    "一个",
    "进行",
    "需要",
    "可以",
    "是不是",
}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def tokenize(text: str) -> list[str]:
    text = normalize_text(text)
    tokens: list[str] = []
    tokens.extend(re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", text))
    tokens.extend(re.findall(r"\d+(?:\.\d+)?", text))
    chinese_runs = re.findall(r"[\u4e00-\u9fff]{2,}", text)
    for run in chinese_runs:
        if len(run) <= 4:
            tokens.append(run)
        else:
            tokens.extend(run[i : i + 2] for i in range(len(run) - 1))
            tokens.extend(run[i : i + 3] for i in range(len(run) - 2))
    for node_id, aliases in CONCEPT_ALIASES.items():
        for alias in aliases:
            if alias.lower() in text:
                tokens.append(node_id)
                tokens.append(alias.lower())
    return [token for token in tokens if token and token not in STOPWORDS]


class HashingEmbedder:
    def __init__(self, dimensions: int = 128) -> None:
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        counts = Counter(tokenize(text))
        vector = [0.0] * self.dimensions
        for token, count in counts.items():
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
            raw = int.from_bytes(digest, "big")
            index = raw % self.dimensions
            sign = -1.0 if raw & 1 else 1.0
            vector[index] += sign * (1.0 + math.log(count))
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [round(value / norm, 6) for value in vector]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0
    size = min(len(left), len(right))
    return sum(left[i] * right[i] for i in range(size))


def concept_hits(text: str) -> list[tuple[str, int]]:
    lowered = normalize_text(text)
    hits: list[tuple[str, int]] = []
    for node_id, aliases in CONCEPT_ALIASES.items():
        score = 0
        for alias in aliases:
            score += lowered.count(alias.lower())
        if score:
            hits.append((node_id, score))
    hits.sort(key=lambda item: item[1], reverse=True)
    return hits
