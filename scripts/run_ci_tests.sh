#!/usr/bin/env bash
set -e

# Ins Projekt-Root wechseln, egal wo das Skript liegt
cd "$(dirname "$0")/.."

# Sicherstellen, dass Test-Abhängigkeiten da sind
uv sync --group test

# Tests ausführen mit denselben Env-Variablen wie im CI
CI=true \
CRAWL4AI_VERBOSE=false \
SECURITY_TEST_MODE=mock \
PYTHONUNBUFFERED=1 \
CRAWL4AI_AVAILABLE=false \
uv run pytest --timeout=120 --cov=. --cov-report=xml --durations=20 -v --tb=short
