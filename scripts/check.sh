#!/usr/bin/env bash
# Local and dispatch check: install into a shared Python 3.12 venv, lint the tests, run them.
set -euo pipefail
cd "$(dirname "$0")/.."
V="${KB_CHECK_VENV:-$HOME/.cache/kb-check-venv}"
[ -x "$V/bin/python" ] || uv venv -q -p 3.12 "$V"
VIRTUAL_ENV="$V" uvx -q --from poetry==2.1.4 poetry install -q --no-interaction --no-root
uvx -q ruff@0.17.1 check tests
"$V/bin/python" -m pytest -q
