FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY docker ./docker

ENV PYTHONPATH=/app/src
ENV LUTHOR_POSTGRES_URL=postgresql://luthor:luthor@postgres:5432/luthor
ENV LUTHOR_CHROMA_HOST=chromadb
ENV LUTHOR_CHROMA_PORT=8000

EXPOSE 8080

CMD ["uvicorn", "luthor.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
