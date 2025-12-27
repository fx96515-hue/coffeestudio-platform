from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

from rapidfuzz import fuzz
from sqlalchemy.orm import Session

from app.models.cooperative import Cooperative
from app.models.roaster import Roaster


def _domain(url: str | None) -> str | None:
    if not url:
        return None
    try:
        return (urlparse(url).netloc or "").lower() or None
    except Exception:
        return None


@dataclass
class DedupPair:
    a_id: int
    b_id: int
    a_name: str
    b_name: str
    score: float
    reason: str


def _score(a_name: str, b_name: str) -> float:
    # token-based fuzzy score (0..100)
    return float(max(
        fuzz.token_set_ratio(a_name or "", b_name or ""),
        fuzz.token_sort_ratio(a_name or "", b_name or ""),
    ))


def suggest_duplicates(
    db: Session,
    *,
    entity_type: str,
    threshold: float = 90.0,
    limit_pairs: int = 50,
) -> list[dict[str, Any]]:
    """Suggest possible duplicates.

    This is intentionally conservative and optimized for small/medium datasets.
    """
    if entity_type not in {"cooperative", "roaster"}:
        raise ValueError("entity_type must be cooperative|roaster")

    if entity_type == "cooperative":
        items: list[Any] = db.query(Cooperative).all()
    else:
        items = db.query(Roaster).all()  # type: ignore[assignment]

    # group by domain when possible (strong signal)
    by_domain: dict[str, list[Any]] = {}
    no_domain: list[Any] = []
    for it in items:
        dom = _domain(getattr(it, "website", None))
        if dom:
            by_domain.setdefault(dom, []).append(it)
        else:
            no_domain.append(it)

    pairs: list[DedupPair] = []

    # Domain-based duplicates (same domain)
    for dom, group in by_domain.items():
        if len(group) < 2:
            continue
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                a, b = group[i], group[j]
                s = _score(a.name, b.name)
                pairs.append(DedupPair(a.id, b.id, a.name, b.name, max(s, 98.0), f"same_domain:{dom}"))

    # Name-based duplicates (simple blocking by first letter)
    buckets: dict[str, list[Any]] = {}
    for it in no_domain:
        k = (it.name or "").strip()[:1].lower() or "_"
        buckets.setdefault(k, []).append(it)

    for _, group in buckets.items():
        n = len(group)
        for i in range(n):
            for j in range(i + 1, n):
                a, b = group[i], group[j]
                s = _score(a.name, b.name)
                if s >= threshold:
                    pairs.append(DedupPair(a.id, b.id, a.name, b.name, s, "name_similarity"))

    # sort + cut
    pairs.sort(key=lambda p: p.score, reverse=True)
    pairs = pairs[: max(0, min(limit_pairs, 500))]

    return [
        {
            "a_id": p.a_id,
            "b_id": p.b_id,
            "a_name": p.a_name,
            "b_name": p.b_name,
            "score": p.score,
            "reason": p.reason,
        }
        for p in pairs
    ]
