FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY shared shared
COPY services/ml services/ml
RUN pip install -e shared && pip install -e services/ml

ENV PYTHONPATH=/app/services/ml/src:/app/shared/src
CMD ["python", "-m", "alphaforge_ml.main"]
