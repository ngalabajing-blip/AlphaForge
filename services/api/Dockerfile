FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY shared/pyproject.toml shared/
COPY shared/src shared/src
COPY services/api/pyproject.toml services/api/
COPY services/api/src services/api/src
COPY services/api/alembic services/api/alembic
COPY services/api/alembic.ini services/api/alembic.ini

RUN pip install -e shared && pip install -e services/api

ENV PYTHONPATH=/app/services/api/src:/app/shared/src
EXPOSE 8000
CMD ["uvicorn", "alphaforge_api.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
