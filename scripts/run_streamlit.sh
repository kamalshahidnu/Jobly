#!/usr/bin/env bash
# Script to run Streamlit UI (works with Poetry or a plain venv)
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PORT="${PORT:-8501}"

echo "Starting Jobly Streamlit UI on port ${PORT}..."

cd "${ROOT_DIR}/backend"

if command -v poetry >/dev/null 2>&1; then
  exec poetry run streamlit run jobly/ui/streamlit/app.py --server.port="${PORT}"
fi

# If a local venv exists, activate it automatically.
if [[ -f ".venv/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
fi

# Provide a helpful error if deps aren't installed.
python -c "import streamlit" >/dev/null 2>&1 || {
  echo "Streamlit is not installed in the active environment."
  echo "From backend/: python -m venv .venv && source .venv/bin/activate && python -m pip install -U pip && python -m pip install -e ."
  exit 1
}

exec python -m streamlit run jobly/ui/streamlit/app.py --server.port="${PORT}"
