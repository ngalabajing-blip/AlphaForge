FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY shared shared
COPY services/auditor services/auditor
RUN pip install -e shared && pip install -e services/auditor

ENV PYTHONPATH=/app/services/auditor/src:/app/shared/src
CMD ["python", "-m", "alphaforge_auditor.main"]
