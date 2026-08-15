from __future__ import annotations

from datetime import datetime, timezone
import re
from typing import Any

from api.core import settings
from services.cache import JsonCache
from services.ckan import CkanClient, CkanError

TORONTO_CKAN = "https://ckan0.cf.opendata.inter.prod-toronto.ca"
PIPELINE_PACKAGE = "capital-project-pipeline"
SOLICITATIONS_RESOURCE_ID = "f676f46c-de76-4e94-bba7-0a3951aa0603"
PIPELINE_SOURCE_URL = "https://open.toronto.ca/dataset/capital-project-pipeline/"
SOLICITATIONS_SOURCE_URL = "https://open.toronto.ca/dataset/tobids-all-open-solicitations/"


def _key(record: dict[str, Any], *needles: str) -> Any:
    for key, value in record.items():
        normalized = re.sub(r"[^a-z0-9]", "", key.lower())
        if all(needle in normalized for needle in needles):
            return value
    return None


def normalize_pipeline_record(record: dict[str, Any]) -> dict[str, Any]:
    project = _key(record, "project", "name") or _key(record, "project") or _key(record, "contract")
    description = _key(record, "description") or _key(record, "scope")
    division = _key(record, "division") or _key(record, "asset", "owner") or _key(record, "client")
    location = _key(record, "location") or _key(record, "street") or _key(record, "ward")
    procurement = _key(record, "procurement") or _key(record, "tender") or _key(record, "forecast")
    category = _key(record, "category") or _key(record, "type") or _key(record, "program")
    budget = _key(record, "budget") or _key(record, "estimate") or _key(record, "value")
    return {
        "project": str(project or "Planned capital project"),
        "description": description,
        "division": division,
        "location": location,
        "procurement_window": procurement,
        "category": category,
        "budget_text": budget,
        "raw": record,
    }


def normalize_solicitation(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "document_number": record.get("Document Number"),
        "rfx_type": record.get("RFx (Solicitation) Type"),
        "noip_type": record.get("NOIP (Notice of Intended Procurement) Type"),
        "issue_date": record.get("Issue Date"),
        "submission_deadline": record.get("Submission Deadline"),
        "category": record.get("High Level Category"),
        "description": record.get("Solicitation Document Description"),
        "division": record.get("Division"),
        "buyer_name": record.get("Buyer Name"),
        "buyer_email": record.get("Buyer Email"),
        "buyer_phone": record.get("Buyer Phone Number"),
        "wards": record.get("Wards"),
    }


def is_open_solicitation(record: dict[str, Any]) -> bool:
    value = record.get("submission_deadline")
    if not value:
        return True
    text = str(value).replace("Z", "+00:00")
    try:
        deadline = datetime.fromisoformat(text)
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        return deadline >= datetime.now(timezone.utc)
    except ValueError:
        return True


class TorontoService:
    def __init__(self) -> None:
        self.client = CkanClient(TORONTO_CKAN, settings.http_timeout_seconds)
        self.cache = JsonCache(settings.cache_dir, settings.cache_ttl_seconds)

    async def pipeline(self) -> dict[str, Any]:
        cached = self.cache.get("toronto_pipeline")
        if cached is not None:
            cached["cache"] = "hit"
            return cached
        package = await self.client.package_show(PIPELINE_PACKAGE)
        resources = [resource for resource in package.get("resources", []) if resource.get("datastore_active")]
        if not resources:
            raise CkanError("Toronto Capital Projects Pipeline has no active datastore resource")
        preferred = next(
            (
                resource for resource in resources
                if "capital project pipeline" in str(resource.get("name", "")).lower()
                and str(resource.get("format", "")).lower() not in {"xlsx", "pdf"}
            ),
            resources[0],
        )
        result = await self.client.datastore_search(preferred["id"], limit=5000)
        records = [normalize_pipeline_record(record) for record in result.get("records", [])]
        payload = {
            "source": "City of Toronto Capital Projects Pipeline",
            "source_url": PIPELINE_SOURCE_URL,
            "source_mode": "live",
            "cache": "miss",
            "resource_id": preferred["id"],
            "total": result.get("total", len(records)),
            "projects": records,
        }
        self.cache.put("toronto_pipeline", payload)
        return payload

    async def solicitations(self) -> dict[str, Any]:
        cached = self.cache.get("toronto_solicitations")
        if cached is not None:
            cached["cache"] = "hit"
            return cached
        result = await self.client.datastore_search(
            SOLICITATIONS_RESOURCE_ID,
            limit=settings.max_toronto_solicitations,
        )
        normalized = [normalize_solicitation(record) for record in result.get("records", [])]
        open_records = [record for record in normalized if is_open_solicitation(record)]
        payload = {
            "source": "City of Toronto Bids Solicitations",
            "source_url": SOLICITATIONS_SOURCE_URL,
            "source_mode": "live",
            "cache": "miss",
            "total": len(open_records),
            "solicitations": open_records,
        }
        self.cache.put("toronto_solicitations", payload)
        return payload
