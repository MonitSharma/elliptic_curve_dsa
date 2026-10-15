#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > conditional.pid
trap 'rc=$?; echo "$rc" > conditional.exit' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 62914560
for cap in 32 128; do
  for rank in proxy density; do
    name=conditional-$cap-$rank
    python3 /home/hclau/ecdsa_research/server-preflight.py > "$name-preflight.json"
    CACHE_CONDITIONAL_DONOR=1 CACHE_SPLIT=1 CACHE_RANK=$rank CACHE_ATOM_CAP=$cap CACHE_PRODUCT_CAP=1000000 /usr/bin/time -v ./target-conditional/release/product_paired_diagnostic tip/ops.bin "$name.bin" > "$name-generate.log" 2>&1
    sha256sum "$name.bin" > "$name.sha256"
  done
done
for cap in 128 512; do
  name=cache-anf-$cap
  python3 /home/hclau/ecdsa_research/server-preflight.py > "$name-preflight.json"
  EXACT_MODE=cache-anf CACHE_SPLIT=1 CACHE_RANK=density CACHE_ATOM_CAP=$cap ANF_PAIR_CAP=64 CACHE_PRODUCT_CAP=1000000 /usr/bin/time -v ./target-fuse/release/product_paired_diagnostic tip/ops.bin "$name.bin" > "$name-generate.log" 2>&1
  sha256sum "$name.bin" > "$name.sha256"
done
until test -f followup.exit; do sleep 5; done
for name in conditional-32-proxy conditional-32-density conditional-128-proxy conditional-128-density cache-anf-128 cache-anf-512; do
  python3 /home/hclau/ecdsa_research/server-preflight.py > "$name-preflight.json"
  /usr/bin/time -v /home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census "$name.bin" product-exact-20261015 0 4096 12 "$name-census.jsonl" > "$name-census.out" 2> "$name-census.err"
done
