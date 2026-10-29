#!/usr/bin/env bash
# Lance la suite de tests (hors VS Code). Arguments transmis à pytest, ex. : ./lancer-tests.sh -k api -x
set -e
cd "$(dirname "$0")"

if [ -x backend/.venv/bin/python ]; then
    PY=backend/.venv/bin/python
else
    PY=python3
fi

if ! "$PY" -c "import pytest, presidio_analyzer, flask" >/dev/null 2>&1; then
    echo "Installation des dépendances de test..."
    "$PY" -m pip install -r backend/requirements.txt -r backend/requirements-dev.txt
fi

exec "$PY" -m pytest "$@"
