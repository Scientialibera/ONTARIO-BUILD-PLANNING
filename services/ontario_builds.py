from __future__ import annotations

from typing import Any

from api.core import settings
from domain.scoring import planning_complexity
from services.cache import JsonCache
from services.ckan import CkanClient

ONTARIO_CKAN = "https://data.ontario.ca"
ONTARIO_BUILDS_RESOURCE_ID = "35dc5416-2b86-4a79-b3e6-acbfe004c81a"
SOURCE_URL = "https://data.ontario.ca/dataset/ontario-builds-key-infrastructure-projects"


def _number(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).replace("$", "").replace(",", "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _coordinate(value: Any, minimum: float, maximum: float) -> float | None:
    number = _number(value)
    if number is None or not minimum <= number <= maximum:
        return None
    return number


def normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    project = {
        "category": record.get("Category"),
        "supporting_ministry": record.get("Supporting Ministry"),
        "community": record.get("Community"),
        "project": record.get("Project"),
        "status": record.get("Status"),
        "target_completion": record.get("Target Completion Date"),
        "description": record.get("Description"),
        "result": record.get("Result"),
        "area": record.get("Area"),
        "region": record.get("Region"),
        "address": record.get("Address"),
        "postal_code": record.get("Postal Code"),
        "corridor": record.get("Highway / Transit Line"),
        "budget": _number(record.get("Estimated Total Budget ($)")),
        "municipal_funding": record.get("Municipal Funding"),
        "provincial_funding": record.get("Provincial Funding"),
        "federal_funding": record.get("Federal Funding"),
        "other_funding": record.get("Other Funding"),
        "website": record.get("Website"),
        "latitude": _coordinate(record.get("Latitude"), 41.0, 57.0),
        "longitude": _coordinate(record.get("Longitude"), -96.0, -74.0),
    }
    project["complexity"] = planning_complexity(project)
    return project


class OntarioBuildsService:
    def __init__(self) -> None:
        self.client = CkanClient(ONTARIO_CKAN, settings.http_timeout_seconds)
        self.cache = JsonCache(settings.cache_dir, settings.cache_ttl_seconds)

    async def projects(self) -> dict[str, Any]:
        cached = self.cache.get("ontario_builds")
        if cached is not None:
            cached["cache"] = "hit"
            return cached
        result = await self.client.datastore_search(
            ONTARIO_BUILDS_RESOURCE_ID,
            limit=settings.max_ontario_projects,
        )
        records = [normalize_record(record) for record in result.get("records", [])]
        payload = {
            "source": "Ontario Builds: key infrastructure projects",
            "source_url": SOURCE_URL,
            "source_mode": "live",
            "cache": "miss",
            "total": result.get("total", len(records)),
            "projects": records,
        }
        self.cache.put("ontario_builds", payload)
        return payload
