# Multi-stage build: resolve/install deps with uv in a builder stage, then
# copy only the resulting .venv + source into a slim runtime image.

FROM python:3.13-slim AS builder

RUN pip install --no-cache-dir uv

WORKDIR /app

# Install deps first (separate layer from the source copy below) so code
# changes don't invalidate the dependency-install cache layer.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .
RUN uv sync --frozen --no-dev


FROM python:3.13-slim AS runtime

RUN useradd --create-home --uid 1000 flowgard
WORKDIR /app

COPY --from=builder --chown=flowgard:flowgard /app /app
ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER flowgard

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
