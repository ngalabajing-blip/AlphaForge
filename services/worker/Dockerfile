FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY shared shared
COPY services/worker services/worker
RUN pip install -e shared && pip install -e services/worker

ENV PYTHONPATH=/app/services/worker/src:/app/shared/src
CMD ["celery", "-A", "alphaforge_worker.celery_app:celery_app", "worker", "--loglevel=INFO"]
