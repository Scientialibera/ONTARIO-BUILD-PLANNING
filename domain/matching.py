from __future__ import annotations

from difflib import SequenceMatcher
import re
from typing import Any

STOPWORDS = {
    "and", "the", "for", "of", "to", "a", "an", "in", "on", "with", "at", "city", "toronto",
    "project", "services", "work", "construction", "capital", "contract", "supply", "including",
}


def normalize_text(value: Any) -> str:
    text = re.sub(r"[^a-z0-9 ]+", " ", str(value or "").lower())
    return re.sub(r"\s+", " ", text).strip()


def tokens(value: Any) -> set[str]:
    return {token for token in normalize_text(value).split() if len(token) >= 3 and token not in STOPWORDS}


def text_similarity(a: str, b: str) -> float:
    a_norm = normalize_text(a)
    b_norm = normalize_text(b)
    if not a_norm or not b_norm:
        return 0.0
    a_tokens = tokens(a_norm)
    b_tokens = tokens(b_norm)
    union = a_tokens | b_tokens
    jaccard = len(a_tokens & b_tokens) / len(union) if union else 0.0
    sequence = SequenceMatcher(None, a_norm, b_norm).ratio()
    return round((0.68 * jaccard) + (0.32 * sequence), 4)


def opportunity_matches(
    pipeline: list[dict[str, Any]],
    solicitations: list[dict[str, Any]],
    threshold: float = 0.34,
    max_matches_per_project: int = 3,
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for project in pipeline:
        p_text = " ".join(
            str(project.get(key) or "")
            for key in ("project", "description", "location", "division", "category")
        )
        scored: list[tuple[float, dict[str, Any]]] = []
        for solicitation in solicitations:
            s_text = " ".join(
                str(solicitation.get(key) or "")
                for key in ("description", "division", "category", "document_number")
            )
            score = text_similarity(p_text, s_text)
            if project.get("division") and solicitation.get("division"):
                if normalize_text(project["division"]) == normalize_text(solicitation["division"]):
                    score = min(1.0, score + 0.12)
            if score >= threshold:
                scored.append((score, solicitation))
        scored.sort(key=lambda item: item[0], reverse=True)
        output.append(
            {
                "pipeline_project": project,
                "matches": [
                    {"score": round(score, 3), "solicitation": solicitation}
                    for score, solicitation in scored[:max_matches_per_project]
                ],
            }
        )
    return output
