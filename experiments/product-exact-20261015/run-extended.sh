#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
wide=/home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin
cd "$root"
echo $$ > extended.pid
trap 'rc=$?; echo "$rc" > extended.exit' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 41943040
cp /home/hclau/ecdsa_research/wide-cache-20261015/evidence/parent-census.jsonl wide-original-census.jsonl
for name in retained-1024 wide-retained-128 wide-retained-512; do
  if test "$name" = retained-1024; then input=tip/ops.bin; cap=1024; else input=$wide; cap=${name##*-}; fi
  python3 /home/hclau/ecdsa_research/server-preflight.py > "$name-preflight.json"
  set +e
  EXACT_MODE=cache-retained CACHE_SPLIT=1 CACHE_RANK=density CACHE_ATOM_CAP=$cap ANF_PAIR_CAP=64 CACHE_PRODUCT_CAP=1000000 /usr/bin/time -v ./target-retained/release/product_paired_diagnostic "$input" "$name.bin" > "$name-generate.log" 2>&1
  rc=$?; echo "$rc" > "$name-generate.exit"
  set -e
  if test "$rc" != 0; then continue; fi
  for family in independent structured; do
    /usr/bin/time -v ./target-replay/release/product_paired_diagnostic "$input" "$name.bin" "$name-generate.log" "$family" "$name-$family.tsv" > "$name-$family.log" 2>&1
  done
  sha256sum "$name.bin" > "$name.sha256"
done
until test -f retained-census.exit; do sleep 5; done
for name in retained-1024 wide-retained-128 wide-retained-512; do
  if ! test -f "$name.sha256"; then continue; fi
  if test "$name" = retained-1024; then label=product-exact-20261015; else label=wide-cache-paired-v1; fi
  python3 /home/hclau/ecdsa_research/server-preflight.py > "$name-census-preflight.json"
  /usr/bin/time -v /home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census "$name.bin" "$label" 0 4096 10 "$name-census.jsonl" > "$name-census.out" 2> "$name-census.err"
done
