#!/usr/bin/env bash
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

if [[ -x ".venv/bin/python" ]]; then
  PYTHON=".venv/bin/python"
else
  PYTHON="python"
fi

"$PYTHON" - <<'PY'
import importlib.util
import sys

required_modules = ["pytest", "fastapi", "sqlalchemy", "passlib", "jwt", "httpx"]
missing = [name for name in required_modules if importlib.util.find_spec(name) is None]

if missing:
    print("[local-ci] Missing dependencies:", ", ".join(missing), file=sys.stderr)
    print('[local-ci] Run: python -m pip install -e ".[dev]"', file=sys.stderr)
    sys.exit(1)
PY

echo "[local-ci] Running tests..."
"$PYTHON" -m pytest -q

echo "[local-ci] Running import smoke check..."
"$PYTHON" -c "from app.main import app; print(app.title)"

echo "[local-ci] OK"
