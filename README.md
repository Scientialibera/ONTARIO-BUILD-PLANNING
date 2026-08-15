# Ontario Build Planning

Ontario Build Planning is a public-data infrastructure intelligence application for exploring Ontario's capital-project portfolio and identifying upcoming procurement opportunities.

The application combines a province-wide project map with a Toronto-specific Procurement Radar. It is designed for infrastructure planners, engineering firms, contractors, advisory teams and anyone who needs to understand what is being built, where delivery activity is concentrated and which planned municipal projects may be approaching live procurement.

## Core capabilities

- Province-wide Ontario Builds project map with category, status, region and disclosed-budget filters
- Portfolio KPIs and completion-year analytics
- Project-level planning complexity screening based only on published metadata
- Toronto Capital Projects Pipeline ingestion for advance procurement visibility
- Toronto Bids ingestion for currently open competitive solicitations
- Explainable candidate matching between planned capital projects and live solicitations
- Curated Internet workspace for official source discovery, runtime source health and research guidance
- Runtime caching so public APIs are not repeatedly queried on every browser interaction
- No CI/CD configuration and no automatic workflows
- Local no-emoji policy checker under `scripts/check_no_emoji.py`

## Public data

The first release uses three official open datasets:

1. Ontario Builds: key infrastructure projects
   https://data.ontario.ca/dataset/ontario-builds-key-infrastructure-projects
2. City of Toronto Capital Projects Pipeline
   https://open.toronto.ca/dataset/capital-project-pipeline/
3. City of Toronto Bids Solicitations
   https://open.toronto.ca/dataset/tobids-all-open-solicitations/

See `docs/data-sources.md` for field-level details and model boundaries.

## Product views

### Provincial Portfolio

Loads the live Ontario Builds datastore and maps geocoded projects across the province. Select a project to inspect publicly disclosed budget, funding structure, target completion, ministry, category and an explainable planning-complexity score.

### Procurement Radar

Loads the City of Toronto's advance Capital Projects Pipeline and open Toronto Bids solicitations. It compares project descriptions, division and other available metadata to surface candidate relationships for analyst review.

### Analytics

Summarizes category mix, delivery stage, completion-year distribution and the largest publicly disclosed project budgets.

### Internet

Provides a searchable directory of the official government catalogues behind the product, shows whether portfolio and procurement sources connected during the current session, and explains how to verify decision-critical information.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python -m playwright install chromium
uvicorn api.main:app --reload --port 8123
```

Open `http://localhost:8123`. If that port is already in use, choose another available port, for example `make run PORT=8124`.

The application requires internet access to retrieve live public datasets. API responses are cached locally under `data/cache/` for the configured TTL.

## How to use

1. **Portfolio:** use category, status, region and disclosed-budget filters to narrow the map. Click a map marker to open its project detail panel, including the published metadata and planning-complexity explanation. Reset restores the full portfolio.
2. **Procurement Radar:** search planned work by text, or select **Candidate matches only** to focus on pipeline records with an explainable live-bid similarity match. Treat these as analyst leads, not confirmed procurement links.
3. **Analytics:** compare category and delivery-stage mix, target-completion distribution and the largest disclosed budgets. All totals exclude projects without a published budget.
4. **Internet:** search the curated official-source directory by topic, confirm runtime source health, then open authoritative records in a separate browser tab for verification.

## Product views

### Portfolio

![Portfolio filters and map](docs/screenshots/portfolio.png)

### Procurement Radar

![Procurement Radar search and candidate matches](docs/screenshots/procurement-radar.png)

### Analytics

![Portfolio analytics](docs/screenshots/analytics.png)

### Internet

![Official-source Internet research workspace](docs/screenshots/internet.png)

The orange numbered signals on each screenshot are explained in the [numbered product tour](docs/product-tour.md). The visual redesign was guided by a generated SaaS-specific [UI direction](docs/design/saas-ui-direction.png), then implemented as accessible HTML, CSS and JavaScript rather than shipping the mockup as a static image.

## Tests

```bash
pytest -q
python scripts/check_no_emoji.py
```

The Playwright browser suite starts an isolated local application server and intercepts changing public-data responses, so UI tests remain repeatable while live-source behavior stays covered by the service routes.

```bash
python -m playwright install chromium  # first time only
pytest -q tests/e2e
python scripts/capture_screenshots.py
```

`capture_screenshots.py` recreates all four numbered README images with deterministic illustrative data. It is useful whenever the interface changes.

## Docker

```bash
docker build -t ontario-build-planning .
docker run --rm -p 8080:8080 ontario-build-planning
```

## Method boundaries

Planning complexity is a screening index, not a prediction of delay or cost overrun. Procurement Radar matches are text-similarity candidates and are not authoritative links between a pipeline record and a solicitation. Budget aggregates include only values publicly disclosed in the source dataset.
