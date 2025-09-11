PYTHON ?= python3

.PHONY: run lint fmt test migrate upgrade downgrade seed synonyms-check test-docker

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

test-docker:
	@cid=$$(docker compose ps -q api); \
		docker compose exec -T api sh -lc 'rm -rf /app/tests /app/app /app/taxonomy /app/scripts && mkdir -p /app'; \
		docker cp app $$cid:/app/app; \
		docker cp taxonomy $$cid:/app/taxonomy; \
		docker cp scripts $$cid:/app/scripts; \
		docker cp tests $$cid:/app/tests; \
		docker compose exec -T api python scripts/seed_tags.py; \
		docker compose exec -T api sh -lc 'PYTHONPATH=/app pytest -q'
