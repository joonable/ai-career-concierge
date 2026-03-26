from __future__ import annotations

from typing import Iterable


def summarize_recent_dislikes(dislike_reasons: Iterable[str]) -> str:
    cleaned = [reason.strip() for reason in dislike_reasons if reason and reason.strip()]
    if not cleaned:
        return ""

    deduped = list(dict.fromkeys(cleaned))
    joined = "; ".join(deduped[:10])
    return f"Avoid jobs similar to these recent dislikes: {joined}."
