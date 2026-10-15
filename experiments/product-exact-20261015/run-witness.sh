#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > witness.pid
trap 'rc=$?; echo "$rc" > witness.exit' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 62914560
until test -f original.exit; do sleep 5; done
test "$(cat original.exit)" = 0
for cap in 128 512 2048; do
  name=witness-$cap
  python3 /home/hclau/ecdsa_research/server-preflight.py > "$name-preflight.json"
  EXACT_MODE=both CACHE_ATOM_CAP=$cap CACHE_PRODUCT_CAP=2000000 /usr/bin/time -v ./target-witness/release/product_paired_diagnostic tip/ops.bin "$name.bin" > "$name-generate.log" 2>&1
  sha256sum "$name.bin" > "$name.sha256"
done
