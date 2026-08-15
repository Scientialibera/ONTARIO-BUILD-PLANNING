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
from tests.e2e.test_application import PROJECTS, RADAR, SUMMARY  # noqa: E402


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
        }
        if path in responses:
            route.fulfill(content_type="application/json", body=json.dumps(responses[path]))
        else:
            route.continue_()

    page.route("**/api/**", fulfill)


def add_callout(page: Page, selector: str, text: str) -> None:
    page.evaluate(
        """({selector, text}) => {
          const rect = document.querySelector(selector).getBoundingClientRect();
          const note = document.createElement('div');
          note.className = 'screenshot-callout';
          note.textContent = text;
          note.style.left = `${Math.min(rect.right + 14, window.innerWidth - 250)}px`;
          note.style.top = `${Math.max(rect.top + 8, 88)}px`;
          document.body.append(note);
        }""",
        {"selector": selector, "text": text},
    )


def capture(page: Page, name: str, selector: str, text: str) -> None:
    page.add_style_tag(
        content="""
          .screenshot-callout { position:fixed; z-index:5000; width:235px; padding:10px 12px;
            color:#071018; background:#77f0c8; border:2px solid #d9fff3; border-radius:6px;
            box-shadow:0 8px 24px rgba(0,0,0,.4); font:700 12px/1.35 system-ui; }
          .screenshot-callout::before { content:''; position:absolute; left:-14px; top:17px;
            border-width:7px; border-style:solid; border-color:transparent #77f0c8 transparent transparent; }
        """
    )
    add_callout(page, selector, text)
    page.screenshot(path=OUTPUT / name, full_page=False)
    page.locator(".screenshot-callout").evaluate("node => node.remove()")


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
            capture(page, "portfolio.png", ".left-rail", "Use these filters to focus the provincial map.")
            page.get_by_role("tab", name="Procurement Radar").click()
            capture(page, "procurement-radar.png", ".table-toolbar", "Search the pipeline or show only candidate live-bid matches.")
            page.get_by_role("tab", name="Analytics").click()
            capture(page, "analytics.png", "#categoryBars", "Compare portfolio mix, delivery stage and disclosed capital value.")
            browser.close()
    finally:
        process.terminate()
        process.wait(timeout=10)


if __name__ == "__main__":
    main()
