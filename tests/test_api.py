from fastapi.testclient import TestClient

from api.main import app
from services.ontario_builds import OntarioBuildsService
from services.toronto import TorontoService


def test_project_routes_filter_and_summarize_cached_service_payload(monkeypatch):
    payload = {
        "source": "fixture",
        "source_url": "https://example.test/source",
        "projects": [
            {"project": "Transit build", "category": "Transit", "status": "Planning", "region": "East", "budget": 200_000_000, "target_completion": "2030-01-01", "latitude": 43.6, "longitude": -79.4},
            {"project": "Hospital build", "category": "Health", "status": "Complete", "region": "North", "budget": None, "target_completion": "2024-01-01", "latitude": None, "longitude": None},
        ],
    }

    async def projects(_self):
        return payload

    monkeypatch.setattr(OntarioBuildsService, "projects", projects)
    client = TestClient(app)

    filtered = client.get("/api/projects", params={"category": "transit", "min_budget": 100_000_000}).json()
    assert filtered["returned"] == 1
    assert filtered["projects"][0]["project"] == "Transit build"

    summary = client.get("/api/projects/summary").json()
    assert summary["project_count"] == 2
    assert summary["geocoded_count"] == 1
    assert summary["disclosed_budget_total"] == 200_000_000
    assert summary["completion_years"] == [["2024", 1], ["2030", 1]]


def test_public_source_errors_become_service_unavailable(monkeypatch):
    async def unavailable(_self):
        raise RuntimeError("upstream rate limited")

    monkeypatch.setattr(OntarioBuildsService, "projects", unavailable)
    response = TestClient(app).get("/api/projects")
    assert response.status_code == 503
    assert "data unavailable" in response.json()["detail"]


def test_radar_joins_the_two_toronto_payloads(monkeypatch):
    async def pipeline(_self):
        return {"projects": [{"project": "Watermain replacement", "description": "Replace trunk watermain", "division": "Toronto Water"}], "source_url": "https://example.test/pipeline"}

    async def solicitations(_self):
        return {"solicitations": [{"document_number": "RFP-1", "description": "Trunk watermain replacement", "division": "Toronto Water"}], "source_url": "https://example.test/bids"}

    monkeypatch.setattr(TorontoService, "pipeline", pipeline)
    monkeypatch.setattr(TorontoService, "solicitations", solicitations)
    response = TestClient(app).get("/api/toronto/opportunity-radar")
    assert response.status_code == 200
    assert response.json()["projects_with_candidate_matches"] == 1
    assert response.json()["matches"][0]["matches"][0]["solicitation"]["document_number"] == "RFP-1"


def test_internet_source_directory_is_official_and_actionable():
    response = TestClient(app).get("/api/internet/sources")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["sources"]) >= 4
    assert all(source["url"].startswith("https://") for source in payload["sources"])
    assert {source["organization"] for source in payload["sources"]} >= {"Government of Ontario", "City of Toronto"}
    assert payload["signals"]
