FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

COPY shared shared
COPY services/cli services/cli
RUN pip install -e shared && pip install -e services/cli

ENTRYPOINT ["alphaforge"]
