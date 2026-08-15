from __future__ import annotations

from datetime import date, datetime
from typing import Any


def _truthy(value: Any) -> bool:
    if value is None:
        return False
    text = str(value).strip().lower()
    return text not in {"", "no", "none", "n/a", "na", "false", "0"}


def _date(value: Any) -> date | None:
    text = str(value or "").strip()
    if not text:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            parsed = datetime.strptime(text[: len(fmt.replace('%', '')) + 4] if fmt != "%Y-%m-%d" else text[:10], fmt)
            return parsed.date()
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def planning_complexity(project: dict[str, Any], today: date | None = None) -> dict[str, Any]:
    today = today or date.today()
    score = 0
    reasons: list[str] = []

    status = str(project.get("status") or "").lower()
    category = str(project.get("category") or "").lower()
    budget = float(project.get("budget") or 0)
    completion = _date(project.get("target_completion"))

    if budget >= 500_000_000:
        score += 22
        reasons.append("Very large disclosed capital value")
    elif budget >= 100_000_000:
        score += 15
        reasons.append("Large disclosed capital value")
    elif budget >= 25_000_000:
        score += 8
        reasons.append("Material disclosed capital value")

    sources = sum(
        _truthy(project.get(key))
        for key in ("municipal_funding", "provincial_funding", "federal_funding", "other_funding")
    )
    if sources >= 3:
        score += 18
        reasons.append("Three or more disclosed funding sources")
    elif sources == 2:
        score += 10
        reasons.append("Multiple disclosed funding sources")

    if "planning" in status:
        score += 10
        reasons.append("Project remains in planning")
    elif "construction" in status:
        score += 4

    if completion:
        days = (completion - today).days
        if 0 <= days <= 365 and "planning" in status:
            score += 20
            reasons.append("Near-term target date while still in planning")
        elif days < 0 and "complete" not in status:
            score += 25
            reasons.append("Target completion date has passed")
    else:
        score += 8
        reasons.append("No target completion date disclosed")

    if any(term in category for term in ("transit", "transport")):
        score += 12
        reasons.append("Complex transportation delivery context")
    elif any(term in category for term in ("road", "bridge")):
        score += 9
        reasons.append("Road or bridge delivery context")
    elif any(term in category for term in ("health", "hospital")):
        score += 7
        reasons.append("Health infrastructure delivery context")

    if project.get("latitude") is None or project.get("longitude") is None:
        score += 4

    score = max(0, min(100, score))
    band = "low" if score < 30 else "moderate" if score < 55 else "high" if score < 75 else "very high"
    return {"score": score, "band": band, "reasons": reasons[:5]}
