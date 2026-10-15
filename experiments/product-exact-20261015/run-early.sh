#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > early.pid
trap 'rc=$?; echo "$rc" > early.exit' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 62914560
python3 /home/hclau/ecdsa_research/server-preflight.py > early-preflight.json
EXACT_MODE=early EARLY_RESET_EVENT_MAP=early-event-map.txt /usr/bin/time -v ./target-conditional/release/product_paired_diagnostic tip/ops.bin early.bin > early-generate.log 2>&1
for family in independent structured; do
  /usr/bin/time -v ./target-replay/release/product_paired_diagnostic tip/ops.bin early.bin @early-event-map.txt "$family" "early-$family.tsv" > "early-$family.log" 2>&1
done
EXACT_MODE=compact ./target-conditional/release/product_paired_diagnostic early.bin early-compact.bin > early-compact-generate.log 2>&1
for rank in proxy density; do
  name=early-cache-$rank
  CACHE_SPLIT=1 CACHE_RANK=$rank CACHE_ATOM_CAP=128 CACHE_PRODUCT_CAP=1000000 /usr/bin/time -v ./target-conditional/release/product_paired_diagnostic early.bin "$name.bin" > "$name-generate.log" 2>&1
  for family in independent structured; do
    /usr/bin/time -v ./target-replay/release/product_paired_diagnostic early.bin "$name.bin" "$name-generate.log" "$family" "$name-$family.tsv" > "$name-$family.log" 2>&1
  done
done
sha256sum early.bin early-compact.bin early-cache-*.bin > early-streams.sha256
until test -f single.exit; do sleep 5; done
for name in early early-cache-proxy early-cache-density; do
  python3 /home/hclau/ecdsa_research/server-preflight.py > "$name-census-preflight.json"
  /usr/bin/time -v /home/hclau/ecdsa_research/failure-census-20261015/target/release/failure_census "$name.bin" product-exact-20261015 0 4096 12 "$name-census.jsonl" > "$name-census.out" 2> "$name-census.err"
done
