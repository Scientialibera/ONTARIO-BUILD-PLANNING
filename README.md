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

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn api.main:app --reload --port 8000
```

Open `http://localhost:8000`.

The application requires internet access to retrieve live public datasets. API responses are cached locally under `data/cache/` for the configured TTL.

## Tests

```bash
pytest -q
python scripts/check_no_emoji.py
```

## Docker

```bash
docker build -t ontario-build-planning .
docker run --rm -p 8080:8080 ontario-build-planning
```

## Method boundaries

Planning complexity is a screening index, not a prediction of delay or cost overrun. Procurement Radar matches are text-similarity candidates and are not authoritative links between a pipeline record and a solicitation. Budget aggregates include only values publicly disclosed in the source dataset.
