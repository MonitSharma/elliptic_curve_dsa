#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > context-witness.pid
trap 'rc=$?; echo "$rc" > context-witness.exit' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 62914560
for cap in 128 512; do
  name=context-witness-$cap
  python3 /home/hclau/ecdsa_research/server-preflight.py > "$name-preflight.json"
  EXACT_MODE=context-witness CACHE_ATOM_CAP=$cap ANF_PAIR_CAP=64 CACHE_PRODUCT_CAP=1000000 /usr/bin/time -v ./target-conditional/release/product_paired_diagnostic tip/ops.bin "$name.bin" > "$name-generate.log" 2>&1
  sha256sum "$name.bin" > "$name.sha256"
done
EXACT_MODE=context-witness CACHE_ATOM_CAP=128 ANF_PAIR_CAP=64 CACHE_PRODUCT_CAP=1000000 /usr/bin/time -v ./target-conditional/release/product_paired_diagnostic /home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin wide-context-witness.bin > wide-context-witness-generate.log 2>&1
sha256sum wide-context-witness.bin > wide-context-witness.sha256
