"""Create the annotated README screenshots using deterministic browser data."""

from __future__ import annotations

import json
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import httpx
from playwright.sync_api import Page, sync_playwright


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "screenshots"
sys.path.insert(0, str(ROOT))
from tests.e2e.test_application import INTERNET, PROJECTS, RADAR, SUMMARY  # noqa: E402


def start_server() -> tuple[subprocess.Popen[bytes], str]:
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
    for _ in range(50):
        try:
            if httpx.get(f"{url}/api/health", timeout=0.3).status_code == 200:
                return process, url
        except httpx.HTTPError:
            time.sleep(0.1)
    process.terminate()
    raise RuntimeError("Screenshot server did not start")


def mock_public_data(page: Page) -> None:
    def fulfill(route) -> None:
        path = urlparse(route.request.url).path
        responses = {
            "/api/projects": {"projects": PROJECTS, "returned": len(PROJECTS)},
            "/api/projects/summary": SUMMARY,
            "/api/toronto/opportunity-radar": RADAR,
            "/api/internet/sources": INTERNET,
        }
        if path in responses:
            route.fulfill(content_type="application/json", body=json.dumps(responses[path]))
        else:
            route.continue_()

    page.route("**/api/**", fulfill)


def add_marker(page: Page, selector: str, number: int, x: int = 10, y: int = 10) -> None:
    page.evaluate(
        """({selector, number, x, y}) => {
          const rect = document.querySelector(selector).getBoundingClientRect();
          const marker = document.createElement('div');
          marker.className = 'screenshot-marker';
          marker.textContent = String(number).padStart(2, '0');
          marker.style.left = `${rect.left + x}px`;
          marker.style.top = `${rect.top + y}px`;
          document.body.append(marker);
        }""",
        {"selector": selector, "number": number, "x": x, "y": y},
    )


def capture(page: Page, name: str, markers: list[tuple[str, int, int, int]]) -> None:
    page.add_style_tag(
        content="""
          .screenshot-marker { position:fixed; z-index:5000; width:30px; height:30px; display:grid;
            place-items:center; color:#fff; background:#c86818; border:3px solid #fff; border-radius:7px;
            box-shadow:0 5px 18px rgba(29,42,34,.35); font:800 10px/1 system-ui; }
        """
    )
    for selector, number, x, y in markers:
        add_marker(page, selector, number, x, y)
    page.screenshot(path=OUTPUT / name, full_page=False)
    page.locator(".screenshot-marker").evaluate_all("nodes => nodes.forEach(node => node.remove())")


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    process, url = start_server()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
            mock_public_data(page)
            page.goto(url)
            page.locator("#visibleCount").wait_for()
            capture(page, "portfolio.png", [(".left-rail", 1, 10, 10), ("#kpiStrip", 2, 4, 4), (".map-stage", 3, 16, 150), ("#projectDetail", 4, 10, 10)])
            page.get_by_role("tab", name="Procurement Radar").click()
            capture(page, "procurement-radar.png", [("#radarMetrics", 1, 4, 4), (".table-toolbar", 2, 10, 10), (".table-scroll", 3, 10, 10)])
            page.get_by_role("tab", name="Analytics").click()
            capture(page, "analytics.png", [("#categoryBars", 1, 2, 2), ("#statusBars", 2, 2, 2), ("#timelineBars", 3, 2, 2), ("#topBudgetList", 4, 2, 2)])
            page.get_by_role("tab", name="Internet").click()
            capture(page, "internet.png", [("#internetHealth", 1, 2, 2), (".internet-toolbar", 2, 10, 10), ("#internetSources", 3, 2, 2), ("#internetSignals", 4, 2, 2)])
            browser.close()
    finally:
        process.terminate()
        process.wait(timeout=10)


if __name__ == "__main__":
    main()
