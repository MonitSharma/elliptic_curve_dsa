#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=repair53-native-20261016
echo $$ > "$out/census-launcher.pid"
trap 'rc=$?; echo "$rc" > "$root/$out/census-launcher.exit"' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/census-admission-preflight.json"
python3 run_repair53_census.py > "$out/census-qualification.log" 2>&1
