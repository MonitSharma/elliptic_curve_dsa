#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-exact-20261015
d=$r/all70-native67-20261016
cd "$r"
mkdir -p "$d"
echo $$ > "$d/census-launcher.pid"
trap 'echo $? > "$d/census-launcher.exit"' EXIT
while [ ! -f "$d/launcher.exit" ]; do sleep 10; done
test "$(cat "$d/launcher.exit")" = 0
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 25165824
while ! python3 "$r/all70_resource_guard.py" 2 "$d/census-resource-admission.jsonl"; do sleep 30; done
python3 "$r/qualify_all70_fixed67.py" > "$d/qualification.log" 2>&1
