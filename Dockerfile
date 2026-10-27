# syntax=docker/dockerfile:1
# Multi-stage build: dependencies -> train model -> slim non-root runtime.

FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
# Copy requirements alone first so this layer is cached until deps change.
COPY requirements.txt .
RUN pip install -r requirements.txt

# --- Stage: train the model inside the build (reproducible, no host state) ---
FROM base AS trainer
ARG TRAIN_MODEL=random_forest
ARG MODEL_VERSION=dev
ENV TRAIN_MODEL=${TRAIN_MODEL} MODEL_VERSION=${MODEL_VERSION}
COPY params.yaml .
COPY src/ src/
RUN python -m src.prepare && python -m src.train

# --- Stage: runtime image, only what is needed to serve ---
FROM base AS runtime
ARG MODEL_VERSION=dev
LABEL org.opencontainers.image.title="wine-api" \
      org.opencontainers.image.version="${MODEL_VERSION}"
RUN useradd --system --uid 10001 --no-create-home appuser \
    && mkdir -p /app/logs && chown appuser /app/logs
COPY src/ src/
COPY --from=trainer /app/models/ models/
USER 10001
EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
CMD ["uvicorn", "src.serve:app", "--host", "0.0.0.0", "--port", "8000"]
