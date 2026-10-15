#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
wide=/home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin
cd "$root"
echo $$ > wide-chain.pid
trap 'rc=$?; echo "$rc" > wide-chain.exit' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 41943040
python3 /home/hclau/ecdsa_research/server-preflight.py > wide-chain-preflight.json
printf '%s %s\n' wide-retained-128.bin wide-retained-128-generate.log > wide-chain.manifest
CACHE_SPLIT=1 CACHE_RANK=density CACHE_ATOM_CAP=128 CACHE_PRODUCT_CAP=1000000 /usr/bin/time -v ./target-conditional/release/product_paired_diagnostic wide-retained-128.bin wide-chain-old.bin > wide-chain-old-generate.log 2>&1
printf '%s %s\n' wide-chain-old.bin wide-chain-old-generate.log >> wide-chain.manifest
for family in independent structured; do
  /usr/bin/time -v ./target-replay/release/product_paired_diagnostic "$wide" wide-chain-old.bin +wide-chain.manifest "$family" "wide-chain-old-$family.tsv" > "wide-chain-old-$family.log" 2>&1
done
EXACT_MODE=cache-anf CACHE_SPLIT=1 CACHE_RANK=density CACHE_ATOM_CAP=512 ANF_PAIR_CAP=64 CACHE_PRODUCT_CAP=1000000 /usr/bin/time -v ./target-conditional/release/product_paired_diagnostic wide-chain-old.bin wide-chain-anf.bin > wide-chain-anf-generate.log 2>&1
printf '%s %s\n' wide-chain-anf.bin wide-chain-anf-generate.log >> wide-chain.manifest
for family in independent structured; do
  /usr/bin/time -v ./target-replay/release/product_paired_diagnostic "$wide" wide-chain-anf.bin +wide-chain.manifest "$family" "wide-chain-anf-$family.tsv" > "wide-chain-anf-$family.log" 2>&1
done
EXACT_MODE=cache-retained CACHE_SPLIT=1 CACHE_RANK=density CACHE_ATOM_CAP=512 ANF_PAIR_CAP=64 CACHE_PRODUCT_CAP=1000000 /usr/bin/time -v ./target-retained/release/product_paired_diagnostic wide-chain-anf.bin wide-chain-retained.bin > wide-chain-retained-generate.log 2>&1
printf '%s %s\n' wide-chain-retained.bin wide-chain-retained-generate.log >> wide-chain.manifest
for family in independent structured; do
  /usr/bin/time -v ./target-replay/release/product_paired_diagnostic "$wide" wide-chain-retained.bin +wide-chain.manifest "$family" "wide-chain-retained-$family.tsv" > "wide-chain-retained-$family.log" 2>&1
done
sha256sum wide-chain-*.bin > wide-chain.sha256
