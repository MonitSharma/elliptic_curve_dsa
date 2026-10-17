#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=product-to179-rank-20261017
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$root/$out/launcher.exit"' EXIT
while [ ! -e product-to123-rank-20261017/launcher.exit ]; do sleep 60; done
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 25165824
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/launch-preflight.json"
python3 run_product179.py > "$out/chain.log" 2>&1
