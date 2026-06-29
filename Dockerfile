# ThePricingLibrary backend — FastAPI (RAG generation + billing + AG-UI + platform API).
# Slim image: local-hashing embeddings, no torch. Deploy this on your VPS and point
# the frontend's VITE_TPL_RAG_API_URL at it.
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    TPL_DATA_DIR=/data \
    TPL_DB_PATH=/data/pricinglibrary_rag.sqlite3 \
    TPL_LLM_PROVIDER=template

WORKDIR /app

COPY requirements-docker.txt ./
RUN pip install --no-cache-dir -r requirements-docker.txt

COPY pricinglibrary_rag ./pricinglibrary_rag
COPY scripts ./scripts

# Persistent SQLite (platform data, entitlements, generations).
RUN mkdir -p /data
VOLUME ["/data"]

EXPOSE 8000

# Healthcheck hits the platform router (always available, no LLM needed).
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/platform/health').status==200 else 1)" || exit 1

CMD ["uvicorn", "pricinglibrary_rag.api:app", "--host", "0.0.0.0", "--port", "8000"]
