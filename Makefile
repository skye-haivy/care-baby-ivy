PYTHON ?= python3

.PHONY: run lint fmt test

run:
	UVICORN_WORKERS=1 uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

lint:
	ruff check .
	black --check .

fmt:
	ruff check --fix .
	black .

test:
	pytest -q

