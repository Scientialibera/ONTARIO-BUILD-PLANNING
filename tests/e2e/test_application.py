"""Browser journeys for the single-page application.

The app normally consumes changing public datasets.  These tests intercept only
those API calls so that UI coverage is stable and does not load public sources
during every test run.  The backend data adapters have separate unit coverage.
"""

from __future__ import annotations

import json
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import httpx
import pytest
from playwright.sync_api import Browser, Page, expect, sync_playwright


ROOT = Path(__file__).resolve().parents[2]

PROJECTS = [
    {
        "project": "Lakeshore Transit Extension",
        "category": "Transit",
        "status": "Planning",
        "region": "Greater Toronto Area",
        "community": "Toronto",
        "description": "New rapid transit connection along the lakeshore corridor.",
        "budget": 850_000_000,
        "target_completion": "2030-12-01",
        "supporting_ministry": "Transportation",
        "latitude": 43.65,
        "longitude": -79.38,
        "complexity": {"score": 82, "band": "very high", "reasons": ["Large disclosed budget"]},
    },
    {
        "project": "Northern Health Centre",
        "category": "Health care",
        "status": "Under construction",
        "region": "Northern Ontario",
        "community": "Sudbury",
        "description": "Regional hospital expansion.",
        "budget": 120_000_000,
        "target_completion": "2028-05-01",
        "supporting_ministry": "Health",
        "latitude": 46.49,
        "longitude": -80.99,
        "complexity": {"score": 54, "band": "moderate", "reasons": ["Multiple funding sources"]},
    },
]

SUMMARY = {
    "project_count": 2,
    "geocoded_count": 2,
    "disclosed_budget_total": 970_000_000,
    "budget_disclosure_count": 2,
    "categories": [["Transit", 1], ["Health care", 1]],
    "statuses": [["Planning", 1], ["Under construction", 1]],
    "regions": [["Greater Toronto Area", 1], ["Northern Ontario", 1]],
    "completion_years": [["2028", 1], ["2030", 1]],
    "top_budget_projects": PROJECTS,
}

RADAR = {
    "pipeline_total": 2,
    "open_solicitation_total": 1,
    "projects_with_candidate_matches": 1,
    "matches": [
        {
            "pipeline_project": {
                "project": "Lakeshore transit enabling works",
                "description": "Early civil works for the lakeshore transit extension.",
                "division": "Transportation Services",
                "procurement_window": "Q4 2026",
            },
            "matches": [{"score": 0.84, "solicitation": {"document_number": "RFP-2026-01", "description": "Lakeshore transit enabling civil works"}}],
        },
        {
            "pipeline_project": {
                "project": "Community centre roof renewal",
                "description": "Replace the roof at a community centre.",
                "division": "Facilities",
                "procurement_window": "Q1 2027",
            },
            "matches": [],
        },
    ],
}

INTERNET = {
    "sources": [
        {"id": "ontario-builds", "name": "Ontario Builds", "organization": "Government of Ontario", "kind": "PROVINCIAL DATA", "url": "https://data.ontario.ca/example", "coverage": "Projects, geography, status, budgets and funding", "cadence": "Quarterly", "topics": ["portfolio", "capital value"], "used_by": "Portfolio and Analytics"},
        {"id": "toronto-bids", "name": "Toronto Bids Solicitations", "organization": "City of Toronto", "kind": "LIVE SOLICITATIONS", "url": "https://open.toronto.ca/example", "coverage": "Open bids, deadlines, buyers and descriptions", "cadence": "Live", "topics": ["open bids", "deadlines"], "used_by": "Procurement Radar"},
    ],
    "signals": [
        {"title": "Start with source health", "detail": "Confirm the application connected before relying on counts."},
        {"title": "Open the official record", "detail": "Verify decision-critical fields at the source."},
    ],
}


@pytest.fixture(scope="session")
def app_url() -> str:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api.main:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    url = f"http://127.0.0.1:{port}"
    try:
        for _ in range(50):
            try:
                if httpx.get(f"{url}/api/health", timeout=0.3).status_code == 200:
                    break
            except httpx.HTTPError:
                time.sleep(0.1)
        else:
            raise RuntimeError("Test server did not start")
        yield url
    finally:
        process.terminate()
        process.wait(timeout=10)


@pytest.fixture(scope="session")
def browser() -> Browser:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        yield browser
        browser.close()


def mock_public_data(page: Page, *, portfolio_error: bool = False) -> None:
    def fulfill(route) -> None:
        path = urlparse(route.request.url).path
        if path == "/api/projects":
            if portfolio_error:
                route.fulfill(status=503, content_type="application/json", body=json.dumps({"detail": "Ontario source is temporarily rate limited"}))
            else:
                route.fulfill(content_type="application/json", body=json.dumps({"projects": PROJECTS, "returned": len(PROJECTS)}))
        elif path == "/api/projects/summary":
            route.fulfill(content_type="application/json", body=json.dumps(SUMMARY))
        elif path == "/api/toronto/opportunity-radar":
            route.fulfill(content_type="application/json", body=json.dumps(RADAR))
        elif path == "/api/internet/sources":
            route.fulfill(content_type="application/json", body=json.dumps(INTERNET))
        else:
            route.continue_()

    page.route("**/api/**", fulfill)


@pytest.fixture
def page(browser: Browser) -> Page:
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    page = context.new_page()
    page_errors: list[str] = []
    page.on("pageerror", lambda error: page_errors.append(str(error)))
    mock_public_data(page)
    yield page
    assert page_errors == []
    context.close()


def test_portfolio_filters_and_project_detail(page: Page, app_url: str) -> None:
    page.goto(app_url)
    expect(page.get_by_text("Live public data / 2 records")).to_be_visible()
    expect(page.locator("#visibleCount")).to_have_text("2")
    expect(page.locator(".kpi-card")).to_have_count(4)

    page.locator("#categoryFilter").select_option("Transit")
    expect(page.locator("#visibleCount")).to_have_text("1")
    # The map deliberately uses Leaflet's canvas renderer for the large live
    # portfolio, so click the marker's projected coordinate rather than a DOM
    # element. The container retains the Leaflet instance for diagnostics.
    map_box = page.locator("#map").bounding_box()
    assert map_box is not None
    page.wait_for_timeout(300)
    point = page.evaluate("""() => {
      const map = document.querySelector('#map')._ontarioBuildMap;
      return map.latLngToContainerPoint([43.65, -79.38]);
    }""")
    page.mouse.click(map_box["x"] + point["x"], map_box["y"] + point["y"])
    expect(page.locator("#projectDetail")).to_contain_text("Lakeshore Transit Extension")
    expect(page.locator("#projectDetail")).to_contain_text("82/100 - very high")

    page.get_by_role("button", name="Clear").click()
    expect(page.locator("#visibleCount")).to_have_text("2")


def test_radar_and_analytics_views_are_filterable(page: Page, app_url: str) -> None:
    page.goto(app_url)
    expect(page.locator("#visibleCount")).to_have_text("2")

    page.get_by_role("tab", name="Procurement Radar").click()
    expect(page.locator("#tab-radar")).to_have_attribute("aria-selected", "true")
    expect(page.locator("#radarBody tr")).to_have_count(2)
    page.locator("#radarMatchFilter").select_option("matched")
    expect(page.locator("#radarBody tr")).to_have_count(1)
    page.locator("#radarSearch").fill("no such project")
    expect(page.locator("#radarBody")).to_contain_text("No pipeline projects match these filters.")

    page.get_by_role("tab", name="Analytics").click()
    expect(page.locator("#categoryBars")).to_contain_text("Transit")
    expect(page.locator("#topBudgetList")).to_contain_text("Lakeshore Transit Extension")


def test_internet_workspace_searches_curated_official_sources(page: Page, app_url: str) -> None:
    page.goto(app_url)
    expect(page.locator("#visibleCount")).to_have_text("2")
    page.get_by_role("tab", name="Internet").click()
    expect(page.locator("#workspaceTitle")).to_have_text("Internet research")
    expect(page.locator(".source-card")).to_have_count(2)
    expect(page.locator("#internetHealth")).to_contain_text("Connected")
    page.locator("#internetSearch").fill("deadlines")
    expect(page.locator(".source-card")).to_have_count(1)
    expect(page.locator("#internetSources")).to_contain_text("Toronto Bids Solicitations")
    expect(page.locator(".source-link-button")).to_have_attribute("target", "_blank")
    page.locator("#internetSearch").fill("unrelated query")
    expect(page.locator("#internetSources")).to_contain_text("No official sources match that search.")


def test_portfolio_failure_does_not_hide_procurement_radar(browser: Browser, app_url: str) -> None:
    context = browser.new_context(viewport={"width": 1280, "height": 800})
    page = context.new_page()
    mock_public_data(page, portfolio_error=True)
    page.goto(app_url)
    expect(page.get_by_text("Ontario Builds unavailable")).to_be_visible()
    expect(page.get_by_role("alert")).to_contain_text("temporarily rate limited")
    page.get_by_role("tab", name="Procurement Radar").click()
    expect(page.locator("#radarBody")).to_contain_text("Lakeshore transit enabling works")
    context.close()


def test_mobile_layout_has_no_page_width_overflow(browser: Browser, app_url: str) -> None:
    context = browser.new_context(viewport={"width": 390, "height": 844})
    page = context.new_page()
    mock_public_data(page)
    page.goto(app_url)
    expect(page.locator("#visibleCount")).to_have_text("2")
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    page.get_by_role("tab", name="Procurement Radar").click()
    expect(page.locator("#radarBody")).to_contain_text("Community centre roof renewal")
    context.close()
