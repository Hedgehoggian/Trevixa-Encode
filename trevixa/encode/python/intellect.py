from __future__ import annotations

import math
from collections import Counter


def tokenize(text: str) -> list[str]:
    return [t for t in ''.join(c.lower() if c.isalnum() else ' ' for c in text).split() if t]


def cosine_similarity(a: Counter[str], b: Counter[str]) -> float:
    dot = sum(a[k] * b[k] for k in a.keys() & b.keys())
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


class IntellectEngine:
    """Lightweight reasoning helper for retrieval + concise planning."""

    def retrieve(self, prompt: str, memory_lines: list[str], top_k: int = 3) -> list[str]:
        q = Counter(tokenize(prompt))
        scored: list[tuple[float, str]] = []
        for line in memory_lines:
            s = cosine_similarity(q, Counter(tokenize(line)))
            if s > 0:
                scored.append((s, line))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [line for _, line in scored[:top_k]]

    def plan(self, prompt: str) -> list[str]:
        words = tokenize(prompt)
        if not words:
            return ["Clarify goal", "Gather context", "Implement safely"]
        return [
            f"Understand objective: {' '.join(words[:8])}",
            "Design minimal safe solution",
            "Implement + validate",
            "Report assumptions and next steps",
        ]
