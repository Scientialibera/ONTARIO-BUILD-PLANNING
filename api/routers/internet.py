from __future__ import annotations

from typing import Any

from fastapi import APIRouter


router = APIRouter(prefix="/api/internet", tags=["Internet research"])


@router.get("/sources")
def sources() -> dict[str, Any]:
    """Return the curated official-source directory used by the research UI."""
    return {
        "sources": [
            {
                "id": "ontario-builds",
                "name": "Ontario Builds",
                "organization": "Government of Ontario",
                "kind": "PROVINCIAL DATA",
                "url": "https://data.ontario.ca/dataset/ontario-builds-key-infrastructure-projects",
                "coverage": "Projects, geography, status, budgets and funding",
                "cadence": "Quarterly",
                "topics": ["portfolio", "capital value", "project status"],
                "used_by": "Portfolio and Analytics",
            },
            {
                "id": "toronto-pipeline",
                "name": "Toronto Capital Projects Pipeline",
                "organization": "City of Toronto",
                "kind": "PROCUREMENT PIPELINE",
                "url": "https://open.toronto.ca/dataset/capital-project-pipeline/",
                "coverage": "Planned capital procurements and sourcing windows",
                "cadence": "Periodic",
                "topics": ["pipeline", "planned work", "sourcing"],
                "used_by": "Procurement Radar",
            },
            {
                "id": "toronto-bids",
                "name": "Toronto Bids Solicitations",
                "organization": "City of Toronto",
                "kind": "LIVE SOLICITATIONS",
                "url": "https://open.toronto.ca/dataset/tobids-all-open-solicitations/",
                "coverage": "Open bids, deadlines, buyers and descriptions",
                "cadence": "Live",
                "topics": ["open bids", "solicitations", "deadlines"],
                "used_by": "Procurement Radar",
            },
            {
                "id": "infrastructure-ontario",
                "name": "Infrastructure Ontario Projects",
                "organization": "Infrastructure Ontario",
                "kind": "MARKET CONTEXT",
                "url": "https://www.infrastructureontario.ca/en/what-we-do/projectssearch/",
                "coverage": "Major projects, delivery models and market updates",
                "cadence": "Ongoing",
                "topics": ["major projects", "delivery model", "market update"],
                "used_by": "Analyst context",
            },
        ],
        "signals": [
            {"title": "Start with source health", "detail": "Confirm the application connected before relying on counts or matches."},
            {"title": "Open the official record", "detail": "Use the source link when a decision needs field-level verification."},
            {"title": "Check update cadence", "detail": "Quarterly portfolios and live solicitations represent different time horizons."},
            {"title": "Respect model boundaries", "detail": "Similarity matches and complexity scores are screening aids, not predictions."},
        ],
        "method_note": "The directory is curated to official government sources used or documented by Ontario Build Planning.",
    }
