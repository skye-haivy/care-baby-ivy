FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps for psycopg2-binary sometimes still require build tools on some bases; 
# slim usually works without, but be ready to add if needed.

RUN python -m pip install --upgrade pip

# Install runtime deps directly to avoid packaging overhead
RUN pip install fastapi "uvicorn[standard]" pydantic sqlalchemy alembic psycopg2-binary python-dotenv

# Copy application code
COPY app ./app
COPY alembic.ini ./alembic.ini

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
