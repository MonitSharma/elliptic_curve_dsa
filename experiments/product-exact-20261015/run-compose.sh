#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > compose.pid
trap 'rc=$?; echo "$rc" > compose.exit' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 62914560
for order in old-anf anf-old; do
  python3 /home/hclau/ecdsa_research/server-preflight.py > "compose-$order-preflight.json"
  if test "$order" = old-anf; then
    input=split-128-density.bin
    EXACT_MODE=cache-anf CACHE_SPLIT=1 CACHE_RANK=density CACHE_ATOM_CAP=512 ANF_PAIR_CAP=64 CACHE_PRODUCT_CAP=1000000 /usr/bin/time -v ./target-conditional/release/product_paired_diagnostic "$input" "compose-$order.bin" > "compose-$order-generate.log" 2>&1
  else
    input=cache-anf-512.bin
    CACHE_SPLIT=1 CACHE_RANK=density CACHE_ATOM_CAP=128 CACHE_PRODUCT_CAP=1000000 /usr/bin/time -v ./target-conditional/release/product_paired_diagnostic "$input" "compose-$order.bin" > "compose-$order-generate.log" 2>&1
  fi
  for family in independent structured; do
    /usr/bin/time -v ./target-replay/release/product_paired_diagnostic "$input" "compose-$order.bin" "compose-$order-generate.log" "$family" "compose-$order-$family.tsv" > "compose-$order-$family.log" 2>&1
  done
  sha256sum "compose-$order.bin" > "compose-$order.sha256"
done
