.PHONY: install run test test-e2e screenshots no-emoji docker
install:
	python -m pip install -e ".[dev]"

run:
	uvicorn api.main:app --reload --port $(or $(PORT),8000)

test:
	pytest -q

test-e2e:
	pytest -q tests/e2e

screenshots:
	python scripts/capture_screenshots.py

no-emoji:
	python scripts/check_no_emoji.py

docker:
	docker build -t ontario-build-planning .
