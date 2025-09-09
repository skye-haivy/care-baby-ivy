PYTHON ?= python3

.PHONY: run lint fmt test migrate upgrade downgrade seed synonyms-check

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

seed:
	docker compose exec -T api python scripts/seed_tags.py

synonyms-check:
	docker compose exec -T api python -m scripts.check_synonyms
