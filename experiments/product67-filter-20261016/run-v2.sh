#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/hclau/ecdsa_research/product67-filter-20261016
cd "$ROOT"
echo $$ > run-v2.pid
trap 'rc=$?; echo "$rc" > "$ROOT/run-v2.exit"' EXIT
test "$(cat run.exit)" = 1
test ! -e run-v2.exit
sha256sum --check binary-before-v2.sha256
python3 /home/hclau/ecdsa_research/server-preflight.py > preflight-v2.json
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 run.py > validation-and-timing-v2.log 2>&1
