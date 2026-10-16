#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=wide-largecaps-20261016
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$root/$out/launcher.exit"' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 25165824
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/launch-preflight.json"
python3 run_wide_large_caps.py > "$out/chain.log" 2>&1
python3 freeze_wide_large_caps.py > "$out/freeze.log" 2>&1
