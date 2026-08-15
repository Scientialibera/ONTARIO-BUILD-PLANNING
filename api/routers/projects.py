from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from services.ontario_builds import OntarioBuildsService

router = APIRouter(prefix="/api/projects", tags=["Ontario Builds"])


def _filter(project: dict[str, Any], category: str | None, status: str | None, region: str | None, min_budget: float | None) -> bool:
    if category and category.lower() not in str(project.get("category") or "").lower():
        return False
    if status and status.lower() not in str(project.get("status") or "").lower():
        return False
    if region and region.lower() not in str(project.get("region") or "").lower():
        return False
    if min_budget is not None and float(project.get("budget") or 0) < min_budget:
        return False
    return True


@router.get("")
async def list_projects(
    category: str | None = None,
    status: str | None = None,
    region: str | None = None,
    min_budget: float | None = Query(default=None, ge=0),
    limit: int = Query(default=3000, ge=1, le=10000),
) -> dict[str, Any]:
    service = OntarioBuildsService()
    try:
        payload = await service.projects()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Ontario Builds data unavailable: {type(exc).__name__}") from exc
    filtered = [
        project for project in payload["projects"]
        if _filter(project, category, status, region, min_budget)
    ][:limit]
    return {**{k: v for k, v in payload.items() if k != "projects"}, "returned": len(filtered), "projects": filtered}


@router.get("/summary")
async def summary() -> dict[str, Any]:
    service = OntarioBuildsService()
    try:
        payload = await service.projects()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Ontario Builds data unavailable: {type(exc).__name__}") from exc
    projects = payload["projects"]
    categories = Counter(str(p.get("category") or "Unknown") for p in projects)
    statuses = Counter(str(p.get("status") or "Unknown") for p in projects)
    regions = Counter(str(p.get("region") or "Unknown") for p in projects)
    disclosed_budgets = [float(p["budget"]) for p in projects if p.get("budget")]
    years: defaultdict[str, int] = defaultdict(int)
    for project in projects:
        target = str(project.get("target_completion") or "")
        if len(target) >= 4 and target[:4].isdigit():
            years[target[:4]] += 1
    top_budget = sorted(
        (p for p in projects if p.get("budget")),
        key=lambda p: float(p["budget"]),
        reverse=True,
    )[:10]
    return {
        "source": payload["source"],
        "source_url": payload["source_url"],
        "project_count": len(projects),
        "geocoded_count": sum(p.get("latitude") is not None and p.get("longitude") is not None for p in projects),
        "disclosed_budget_total": sum(disclosed_budgets),
        "budget_disclosure_count": len(disclosed_budgets),
        "categories": categories.most_common(),
        "statuses": statuses.most_common(),
        "regions": regions.most_common(),
        "completion_years": sorted(years.items()),
        "top_budget_projects": top_budget,
        "method_note": "Budget total sums only publicly disclosed values in the source dataset and is not the province's full capital plan.",
    }
