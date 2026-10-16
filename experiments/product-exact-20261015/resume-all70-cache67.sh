#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-exact-20261015
d=$r/all70-cache67-20261016
cd "$r"
echo $$ > "$d/cache-launcher.pid"
trap 'echo $? > "$d/cache-launcher.exit"' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 25165824
while ! python3 "$r/all70_resource_guard.py" 1 "$d/resume-resource-admission.jsonl"; do sleep 30; done
python3 "$r/resume_all70_cache67.py" > "$d/cache-chain.log" 2>&1
