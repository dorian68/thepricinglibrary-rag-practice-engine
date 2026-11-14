# ThePricingLibrary backend — FastAPI (RAG generation + billing + AG-UI + platform API).
# Slim image: local-hashing embeddings, no torch. Deploy this on your VPS and point
# the frontend's VITE_TPL_RAG_API_URL at it.
FROM python:3.11-slim@sha256:a3ab0b966bc4e91546a033e22093cb840908979487a9fc0e6e38295747e49ac0

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    TPL_DATA_DIR=/data \
    TPL_DB_PATH=/data/pricinglibrary_rag.sqlite3 \
    TPL_ENVIRONMENT=production \
    TPL_LLM_PROVIDER=template

WORKDIR /app

COPY requirements-docker.txt ./
RUN pip install --no-cache-dir -r requirements-docker.txt

COPY pricinglibrary_rag ./pricinglibrary_rag
COPY scripts ./scripts

# Persistent SQLite (platform data, entitlements, generations). The production
# container runs without root privileges; the named volume inherits this owner.
RUN addgroup --system tpl && adduser --system --ingroup tpl tpl \
    && mkdir -p /data \
    && chown -R tpl:tpl /data /app
VOLUME ["/data"]

USER tpl

EXPOSE 8000

# Readiness is fail-closed: an image started without production auth/rate-limit
# configuration stays unhealthy and protected routes remain unavailable.
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/ready').status==200 else 1)" || exit 1

CMD ["uvicorn", "pricinglibrary_rag.api:app", "--host", "0.0.0.0", "--port", "8000"]
