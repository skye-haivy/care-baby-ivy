# Care Baby Ivy — FastAPI Skeleton

Bootstrap FastAPI service with Dockerized Postgres, linting, and a healthcheck.

## Quickstart

1) Create your `.env` from the example and adjust values as needed:

```bash
cp .env.example .env
```

2) Run locally (dev):

```bash
python -m pip install --upgrade pip
pip install fastapi "uvicorn[standard]" pydantic sqlalchemy alembic psycopg2-binary python-dotenv pytest httpx ruff black
make run
```

Visit http://127.0.0.1:8000/health → `{ "status": "ok" }`

3) With Docker + Postgres:

```bash
docker compose up --build
```

API: http://127.0.0.1:8000/health

4) Lint, format, and test:

```bash
make lint
make fmt
make test
```

## Makefile targets

- `run`: Launches FastAPI via uvicorn.
- `lint`: Runs Ruff checks and Black in check mode.
- `fmt`: Formats with Ruff (fix) and Black.
- `test`: Runs pytest.

## Project layout

```
app/
  core/
    config.py
    db.py
  main.py
tests/
scripts/
taxonomy/
```

## Acceptance

- Compose boots; `/health` returns 200 with `{ "status": "ok" }`.
- `ruff` and `black` pass.
- Commit message: `chore: bootstrap FastAPI + dockerized postgres + healthcheck`.

## Git

```bash
git init
git add -A
git commit -m "chore: bootstrap FastAPI + dockerized postgres + healthcheck"
```
