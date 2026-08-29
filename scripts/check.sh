#!/usr/bin/env bash
set -e

echo "=== Running Flowguard Quality & Health Checks ==="

if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

echo "[1/2] Checking Python code style with Ruff..."
ruff check .

echo "[2/2] Running Pytest suite across all modules..."
pytest -v

echo "=== All checks passed! Repository is healthy and ready to push. ==="
