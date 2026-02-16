FROM python:3.11-slim

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main --no-root

COPY app ./app
COPY core ./core
COPY rag ./rag
COPY llm ./llm

ENV PYTHONPATH=/app

EXPOSE 8000

# Cloud Run sets PORT=8080; fall back to 8000 for local/docker
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
