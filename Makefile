PYTHON ?= python3

.PHONY: run lint fmt test migrate upgrade downgrade

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

migrate:
	alembic revision --autogenerate -m "init child/tag/article tables"

upgrade:
	alembic upgrade head

downgrade:
	alembic downgrade -1
