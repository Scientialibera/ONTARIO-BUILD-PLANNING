from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from domain.matching import opportunity_matches
from services.toronto import TorontoService

router = APIRouter(prefix="/api/toronto", tags=["Toronto procurement"])


@router.get("/pipeline")
async def pipeline() -> dict[str, Any]:
    try:
        return await TorontoService().pipeline()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Toronto pipeline unavailable: {type(exc).__name__}") from exc


@router.get("/solicitations")
async def solicitations() -> dict[str, Any]:
    try:
        return await TorontoService().solicitations()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Toronto solicitations unavailable: {type(exc).__name__}") from exc


@router.get("/opportunity-radar")
async def opportunity_radar() -> dict[str, Any]:
    service = TorontoService()
    try:
        pipeline_payload = await service.pipeline()
        solicitation_payload = await service.solicitations()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Toronto procurement data unavailable: {type(exc).__name__}") from exc
    matches = opportunity_matches(pipeline_payload["projects"], solicitation_payload["solicitations"])
    matched = sum(bool(item["matches"]) for item in matches)
    return {
        "pipeline_total": len(pipeline_payload["projects"]),
        "open_solicitation_total": len(solicitation_payload["solicitations"]),
        "projects_with_candidate_matches": matched,
        "matches": matches,
        "method_note": "Candidate links are explainable text-similarity matches for analyst review. They are not authoritative procurement relationships.",
        "pipeline_source_url": pipeline_payload["source_url"],
        "solicitations_source_url": solicitation_payload["source_url"],
    }
