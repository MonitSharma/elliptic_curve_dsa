#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > context.pid
trap 'rc=$?; echo "$rc" > context.exit' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 62914560
for cap in 16 32 128; do
  name=context-$cap
  python3 /home/hclau/ecdsa_research/server-preflight.py > "$name-preflight.json"
  EXACT_MODE=anf CACHE_ATOM_CAP=$cap ANF_PAIR_CAP=64 CACHE_PRODUCT_CAP=1000000 /usr/bin/time -v ./target-context/release/product_paired_diagnostic tip/ops.bin "$name.bin" > "$name-generate.log" 2>&1
  sha256sum "$name.bin" > "$name.sha256"
done
name=wide-context-128
python3 /home/hclau/ecdsa_research/server-preflight.py > "$name-preflight.json"
EXACT_MODE=anf CACHE_ATOM_CAP=128 ANF_PAIR_CAP=64 CACHE_PRODUCT_CAP=1000000 /usr/bin/time -v ./target-context/release/product_paired_diagnostic /home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin "$name.bin" > "$name-generate.log" 2>&1
sha256sum "$name.bin" > "$name.sha256"
