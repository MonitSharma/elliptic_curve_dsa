#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > refine.pid
trap 'rc=$?; echo "$rc" > refine.exit' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 62914560
python3 /home/hclau/ecdsa_research/server-preflight.py > refine-preflight.json
for name in cache-anf-128 cache-anf-512; do
  for family in independent structured; do
    /usr/bin/time -v ./target-replay/release/product_paired_diagnostic tip/ops.bin "$name.bin" "$name-generate.log" "$family" "$name-$family.tsv" > "$name-$family.log" 2>&1
  done
done
for cap in 1024 2048; do
  name=cache-anf-$cap
  python3 /home/hclau/ecdsa_research/server-preflight.py > "$name-preflight.json"
  EXACT_MODE=cache-anf CACHE_SPLIT=1 CACHE_RANK=density CACHE_ATOM_CAP=$cap ANF_PAIR_CAP=128 CACHE_PRODUCT_CAP=1000000 /usr/bin/time -v ./target-conditional/release/product_paired_diagnostic tip/ops.bin "$name.bin" > "$name-generate.log" 2>&1
  for family in independent structured; do
    /usr/bin/time -v ./target-replay/release/product_paired_diagnostic tip/ops.bin "$name.bin" "$name-generate.log" "$family" "$name-$family.tsv" > "$name-$family.log" 2>&1
  done
  sha256sum "$name.bin" > "$name.sha256"
done
name=anf-plus-cache
CACHE_SPLIT=1 CACHE_RANK=density CACHE_ATOM_CAP=128 CACHE_PRODUCT_CAP=1000000 /usr/bin/time -v ./target-conditional/release/product_paired_diagnostic anf-128.bin "$name.bin" > "$name-generate.log" 2>&1
for family in independent structured; do
  /usr/bin/time -v ./target-replay/release/product_paired_diagnostic anf-128.bin "$name.bin" "$name-generate.log" "$family" "$name-$family.tsv" > "$name-$family.log" 2>&1
done
