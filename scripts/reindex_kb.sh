#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INPUT_DIR="${1:-${ROOT_DIR}/data/kb}"

export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"

python3 - <<'PY' "$INPUT_DIR"
import sys
from rag.reindex import reindex_knowledge_base

input_dir = sys.argv[1]
count = reindex_knowledge_base(input_dir)
print(f"Indexed chunks: {count}")
PY
