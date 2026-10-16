#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-exact-20261015
d=$r/all70-cache67-20261016
echo $$ > "$d/cache-launcher.pid"
trap 'echo $? > "$d/cache-launcher.exit"' EXIT
while [ ! -f "$d/base-launcher.exit" ]; do sleep 5; done
test "$(cat "$d/base-launcher.exit")" = 0
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 25165824
python3 "$r/run_all70_cache67.py" > "$d/cache-chain.log" 2>&1
