#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/hclau/ecdsa_research/dirty-fanout-20261016
cd "$ROOT"
echo $$ > factor.pid
trap 'rc=$?; echo "$rc" > "$ROOT/factor.exit"' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > factor-preflight.json
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 factor-census.py > factor.log 2>&1
