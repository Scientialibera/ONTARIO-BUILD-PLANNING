# Ontario Build Planning

This repository combines Ontario infrastructure portfolio data with Toronto procurement data so an analyst can inspect active capital programs, filter projects by published attributes and review potential links between planned work and open solicitations. The application keeps source data, text matching and planning-complexity screening separate so a candidate procurement relationship is never presented as an authoritative match.

## Interface

### Portfolio

![Portfolio workspace](docs/screenshots/portfolio.png)

1. **Portfolio filters** constrain category, delivery status, region and minimum disclosed budget.
2. **Portfolio KPIs** report published records, geocoded records, total disclosed value and count of projects with a disclosed budget.
3. **Project map** plots geocoded projects; marker style encodes published status and disclosed-budget bands.
4. **Project detail** exposes the source fields for the selected record together with the metadata-based planning-complexity screen.

### Procurement Radar

![Procurement Radar workspace](docs/screenshots/procurement-radar.png)

1. **Radar KPIs** report planned pipeline records, current open bids and pipeline projects with at least one candidate match.
2. **Search and match controls** filter project, division and solicitation text or restrict the table to records with candidate matches.
3. **Opportunity table** places the planned project beside its strongest live-solicitation candidate and the calculated text-similarity score.

### Analytics

![Portfolio analytics](docs/screenshots/analytics.png)

1. **Category distribution** counts published projects by infrastructure sector.
2. **Delivery-stage distribution** uses the status field reported by the source dataset.
3. **Completion timeline** groups records by published target-completion year.
4. **Largest disclosed projects** ranks only projects that contain a published budget value.

### Source workspace

![Official source workspace](docs/screenshots/internet.png)

1. **Runtime source health** shows whether the portfolio and procurement services connected successfully during the active session.
2. **Official-source search** filters the curated source directory by organization, dataset and research topic.
3. **Source directory** records coverage, update cadence, relevant workspace and the official link for each source.
4. **Verification notes** state the checks required before using a candidate procurement relationship or portfolio value in a decision.

`docs/product-tour.md` contains the same numbered reference in a compact standalone format.

## Data model

The province-wide portfolio is loaded from Ontario Builds. Toronto procurement analysis combines the Capital Projects Pipeline with the current Toronto Bids solicitations feed. The application caches source responses under `data/cache/` so repeated browser operations do not re-query the public endpoints unnecessarily.

The portfolio view only aggregates disclosed budgets. Missing values are not inferred. Geocoding status is tracked separately so province-level counts do not silently depend on map coverage.

## Procurement matching

Procurement Radar uses published text and organizational fields to calculate candidate relationships between planned capital work and open solicitations. The result is an analyst lead rather than an authoritative project-to-tender key. A match must be checked against the official solicitation record before it is used commercially or operationally.

## Planning-complexity screen

The project-detail panel calculates a metadata-based planning-complexity score from published project attributes. The score is intended for portfolio triage. It is not a forecast of delay, cost overrun, procurement outcome or construction risk.

## Public sources

**Ontario Builds: key infrastructure projects**  
https://data.ontario.ca/dataset/ontario-builds-key-infrastructure-projects

**City of Toronto Capital Projects Pipeline**  
https://open.toronto.ca/dataset/capital-project-pipeline/

**City of Toronto Bids — all open solicitations**  
https://open.toronto.ca/dataset/tobids-all-open-solicitations/

`docs/data-sources.md` documents the fields used by each service and the source-specific boundaries.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python -m playwright install chromium
uvicorn api.main:app --reload --port 8123
```

Open `http://localhost:8123`. The application requires internet access for live public data and uses the configured cache TTL for repeated requests.

## Container

```bash
docker build -t ontario-build-planning .
docker run --rm -p 8080:8080 ontario-build-planning
```

## Model limits

Portfolio totals depend on what each source publishes and should not be interpreted as complete capital-program accounting when fields are missing. Planning complexity is a screening calculation based on metadata. Procurement Radar uses text similarity and published organizational fields, so it can produce false positives and false negatives; the official solicitation remains the source of record.