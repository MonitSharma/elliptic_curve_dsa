#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > retained-census.pid
trap 'rc=$?; echo "$rc" > retained-census.exit' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 62914560
for name in retained-128 retained-512; do
  until test -f "$name.sha256"; do sleep 5; done
  python3 /home/hclau/ecdsa_research/server-preflight.py > "$name-census-preflight.json"
  /usr/bin/time -v /home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census "$name.bin" product-exact-20261015 0 4096 10 "$name-census.jsonl" > "$name-census.out" 2> "$name-census.err"
done
