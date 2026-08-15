from __future__ import annotations

from typing import Any
import httpx


class CkanError(RuntimeError):
    pass


class CkanClient:
    def __init__(self, base_url: str, timeout_seconds: float = 15) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    async def action(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.base_url}/api/3/action/{action}"
        async with httpx.AsyncClient(timeout=self.timeout_seconds, follow_redirects=True) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()
        if not payload.get("success"):
            raise CkanError(f"CKAN action failed: {action}")
        return payload["result"]

    async def datastore_search(self, resource_id: str, limit: int = 1000, offset: int = 0) -> dict[str, Any]:
        return await self.action(
            "datastore_search",
            {"resource_id": resource_id, "limit": limit, "offset": offset},
        )

    async def package_show(self, package_id: str) -> dict[str, Any]:
        return await self.action("package_show", {"id": package_id})
