#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > differential.pid
trap 'rc=$?; echo "$rc" > differential.exit' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 62914560
python3 /home/hclau/ecdsa_research/server-preflight.py > differential-preflight.json
for name in single-4 anf-128 xor-product; do
  for family in independent structured; do
    /usr/bin/time -v ./target-replay/release/product_paired_diagnostic tip/ops.bin "$name.bin" = "$family" "$name-$family.tsv" > "$name-$family.log" 2>&1
  done
done
