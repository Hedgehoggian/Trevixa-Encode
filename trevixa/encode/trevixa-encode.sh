#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"

if [[ ! -d "${VENV_DIR}" ]]; then
  if command -v python3.14 >/dev/null 2>&1; then
    python3.14 -m venv "${VENV_DIR}"
  else
    python3 -m venv "${VENV_DIR}"
  fi
fi

source "${VENV_DIR}/bin/activate"

MODE="${1:---cli}"
if [[ "${MODE}" == "--cli" ]]; then
  shift || true
  exec python "${ROOT_DIR}/python/main.py" --cli --interactive "$@"
elif [[ "${MODE}" == "--gui" ]]; then
  shift || true
  if [[ -x "${ROOT_DIR}/build/trevixa-encode" ]]; then
    exec "${ROOT_DIR}/build/trevixa-encode" --gui "$@"
  else
    echo "C++ GUI binary not built yet. Build with CMake first." >&2
    exit 1
  fi
else
  echo "Usage: trevixa-encode.sh [--cli|--gui]" >&2
  exit 1
fi
