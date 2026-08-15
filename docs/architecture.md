# Architecture

## Product surfaces

1. Provincial Portfolio uses the Ontario Builds open dataset as the primary infrastructure inventory.
2. Procurement Radar combines the Toronto Capital Projects Pipeline with Toronto Bids Solicitations.
3. Analytics aggregates publicly disclosed category, status, completion and budget metadata.
4. Internet exposes a curated official-source directory and reflects runtime connectivity from the Portfolio and Procurement Radar.

## Runtime flow

Browser -> FastAPI -> public CKAN APIs -> normalized domain records -> local TTL cache -> browser.

The backend shields the frontend from source-specific field names and allows data-source changes to be isolated in service adapters.

## Deployment

The application has no CI/CD configuration. It can run locally with Uvicorn or in any container platform using the included Dockerfile. Runtime API cache files are stored under `data/cache/` and are gitignored.
