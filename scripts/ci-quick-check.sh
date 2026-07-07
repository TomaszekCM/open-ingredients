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

required_modules = ["fastapi", "sqlalchemy", "passlib", "jwt"]
missing = [name for name in required_modules if importlib.util.find_spec(name) is None]

if missing:
    print("[pre-commit] Missing dependencies:", ", ".join(missing), file=sys.stderr)
    print('[pre-commit] Run: python -m pip install -e .', file=sys.stderr)
    sys.exit(1)
PY

echo "[pre-commit] Running import smoke check..."
"$PYTHON" -c "from app.main import app; print(app.title)"

echo "[pre-commit] OK"
