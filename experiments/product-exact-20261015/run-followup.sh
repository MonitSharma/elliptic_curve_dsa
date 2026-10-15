#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > followup.pid
trap 'rc=$?; echo "$rc" > followup.exit' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 62914560
python3 /home/hclau/ecdsa_research/server-preflight.py > followup-preflight.json
EXACT_MODE=xor /usr/bin/time -v ./target-fuse/release/product_paired_diagnostic tip/ops.bin xor-product.bin > xor-product-generate.log 2>&1
EXACT_MODE=xor /usr/bin/time -v ./target-fuse/release/product_paired_diagnostic /home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin xor-wide.bin > xor-wide-generate.log 2>&1
for rank in proxy density; do
  name=semantic-128-$rank
  CACHE_SEMANTIC_END=1 CACHE_SPLIT=1 CACHE_RANK=$rank CACHE_ATOM_CAP=128 CACHE_PRODUCT_CAP=1000000 /usr/bin/time -v ./target-semantic/release/product_paired_diagnostic tip/ops.bin "$name.bin" > "$name-generate.log" 2>&1
done
until test -f split.exit; do sleep 5; done
for name in xor-product semantic-128-proxy semantic-128-density anf-128; do
  python3 /home/hclau/ecdsa_research/server-preflight.py > "$name-preflight.json"
  /usr/bin/time -v /home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census "$name.bin" product-exact-20261015 0 4096 12 "$name-census.jsonl" > "$name-census.out" 2> "$name-census.err"
  sha256sum "$name.bin" > "$name.sha256"
done
