#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=flags-extended-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$out/launcher.exit"' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 41943040
while [ ! -f flags-four-20261016/launcher.exit ]; do sleep 30; done
test "$(cat flags-four-20261016/launcher.exit)" = 0
previous=flags-four-20261016/product-4-retained-512.bin
cp flags-four-20261016/chain.manifest "$out/chain.manifest"
stage=4
for spec in retained:128 retained:512 retained:1024 anf:512 retained:128 retained:512 retained:1024; do
  stage=$((stage+1));mode=${spec%:*};cap=${spec#*:};name="$out/product-$stage-$mode-$cap"
  python3 /home/hclau/ecdsa_research/server-preflight.py > "$name-preflight.json"
  EXACT_MODE="cache-$mode" CACHE_SPLIT=1 CACHE_RANK=density CACHE_ATOM_CAP="$cap" ANF_PAIR_CAP=64 CACHE_PRODUCT_CAP=1000000 /usr/bin/time -v ./target-flags/release/product_paired_diagnostic "$previous" "$name.bin" > "$name-generate.log" 2>&1
  if cmp -s "$previous" "$name.bin"; then mapping==; else mapping="$name-generate.log"; fi
  printf '%s %s\n' "$name.bin" "$mapping" >> "$out/chain.manifest"
  sha256sum "$name.bin" >> "$out/streams.sha256"
  previous="$name.bin"
done
for family in independent structured; do
  /usr/bin/time -v ./target-flags-replay/release/product_paired_diagnostic tip/ops.bin "$previous" "+$out/chain.manifest" "$family" "$out/product-$family.tsv" > "$out/product-$family.log" 2>&1
done
python3 stream_resources.py "$previous" > "$out/resources.jsonl"
python3 -c 'import json; r=json.loads(open("flags-extended-20261016/resources.jsonl").read());assert r["u16_physical_ids_supported"]'
