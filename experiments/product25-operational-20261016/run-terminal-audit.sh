#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product25-operational-20261016
test ! -e ROOT_TERMINAL_AUDIT.json
echo $$ > terminal-audit.pid
trap 'rc=$?; echo "$rc" > terminal-audit.exit' EXIT
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > terminal-audit-preflight.json
python3 audit-terminal.py "$PWD" "$PWD/ROOT_TERMINAL_AUDIT.json"
