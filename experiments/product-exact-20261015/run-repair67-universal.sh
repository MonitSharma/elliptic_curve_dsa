#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=repair67-universal-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$root/$out/launcher.exit"' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/launch-preflight.json"
python3 audit_repair67.py run > "$out/chain.log" 2>&1
