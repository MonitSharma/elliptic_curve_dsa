#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=cache-certificate-parallel-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$root/$out/launcher.exit"' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/preflight.json"
test -f cache-certificate-20261016/PLAN.json
python3 run_cache_certificate_parallel.py > "$out/chain.log" 2>&1
