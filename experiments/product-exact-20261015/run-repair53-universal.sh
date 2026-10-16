#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=repair53-universal-20261016
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$root/$out/launcher.exit"' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
test "$(cat wide-largecaps-20261016/launcher.exit)" = 0
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/launch-preflight.json"
python3 audit_repair53.py run > "$out/chain.log" 2>&1
