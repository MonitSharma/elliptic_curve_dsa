#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > chain.pid
trap 'rc=$?; echo "$rc" > chain.exit' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 62914560
python3 /home/hclau/ecdsa_research/server-preflight.py > chain-preflight.json
printf '%s %s\n' retained-128.bin retained-128-generate.log > chain.manifest
CACHE_SPLIT=1 CACHE_RANK=density CACHE_ATOM_CAP=128 CACHE_PRODUCT_CAP=1000000 /usr/bin/time -v ./target-conditional/release/product_paired_diagnostic retained-128.bin chain-old.bin > chain-old-generate.log 2>&1
printf '%s %s\n' chain-old.bin chain-old-generate.log >> chain.manifest
for family in independent structured; do
  /usr/bin/time -v ./target-replay/release/product_paired_diagnostic tip/ops.bin chain-old.bin +chain.manifest "$family" "chain-old-$family.tsv" > "chain-old-$family.log" 2>&1
done
EXACT_MODE=cache-anf CACHE_SPLIT=1 CACHE_RANK=density CACHE_ATOM_CAP=512 ANF_PAIR_CAP=64 CACHE_PRODUCT_CAP=1000000 /usr/bin/time -v ./target-conditional/release/product_paired_diagnostic chain-old.bin chain-anf.bin > chain-anf-generate.log 2>&1
printf '%s %s\n' chain-anf.bin chain-anf-generate.log >> chain.manifest
for family in independent structured; do
  /usr/bin/time -v ./target-replay/release/product_paired_diagnostic tip/ops.bin chain-anf.bin +chain.manifest "$family" "chain-anf-$family.tsv" > "chain-anf-$family.log" 2>&1
done
EXACT_MODE=cache-retained CACHE_SPLIT=1 CACHE_RANK=density CACHE_ATOM_CAP=512 ANF_PAIR_CAP=64 CACHE_PRODUCT_CAP=1000000 /usr/bin/time -v ./target-retained/release/product_paired_diagnostic chain-anf.bin chain-retained.bin > chain-retained-generate.log 2>&1
printf '%s %s\n' chain-retained.bin chain-retained-generate.log >> chain.manifest
for family in independent structured; do
  /usr/bin/time -v ./target-replay/release/product_paired_diagnostic tip/ops.bin chain-retained.bin +chain.manifest "$family" "chain-retained-$family.tsv" > "chain-retained-$family.log" 2>&1
done
sha256sum chain-*.bin > chain.sha256
