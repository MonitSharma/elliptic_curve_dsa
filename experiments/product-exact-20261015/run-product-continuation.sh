#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=product-continuation-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$out/launcher.exit"' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 41943040
printf '%s\n' 'Fixed before continuation measurements: 14 additional stages after compact11; two cycles of retained128,retained512,retained1024,plainANF512,retained128,retained512,retained1024; paircap64/productcap1M/density/split, no added qubits, flags reused per donor. Anchor original MR words and separately draw added cache MR words. Checkpoint after each full cycle; do not stop or choose stage based on packet failures.' > "$out/DECLARATION.txt"
while [ ! -f flags-extended-20261016/launcher.exit ]; do sleep 30; done
test "$(cat flags-extended-20261016/launcher.exit)" = 0
test -x target-anchored-replay/release/product_paired_diagnostic
previous=flags-extended-20261016/product-11-retained-1024.bin
sha256sum "$previous" > "$out/input.sha256"
cp flags-extended-20261016/chain.manifest "$out/chain.manifest"
stage=11
for cycle in 1 2; do
  for spec in retained:128 retained:512 retained:1024 anf:512 retained:128 retained:512 retained:1024; do
    stage=$((stage+1));mode=${spec%:*};cap=${spec#*:};name="$out/product-$stage-$mode-$cap"
    python3 /home/hclau/ecdsa_research/server-preflight.py > "$name-preflight.json"
    EXACT_MODE="cache-$mode" CACHE_SPLIT=1 CACHE_RANK=density CACHE_ATOM_CAP="$cap" ANF_PAIR_CAP=64 CACHE_PRODUCT_CAP=1000000 /usr/bin/time -v ./target-flags/release/product_paired_diagnostic "$previous" "$name.bin" > "$name-generate.log" 2>&1
    if cmp -s "$previous" "$name.bin"; then mapping==; else mapping="$name-generate.log"; fi
    printf '%s %s\n' "$name.bin" "$mapping" >> "$out/chain.manifest"
    sha256sum "$name.bin" >> "$out/streams.sha256"
    previous="$name.bin"
  done
  cp "$out/chain.manifest" "$out/stage-$stage.manifest"
  for family in independent structured; do
    /usr/bin/time -v ./target-anchored-replay/release/product_paired_diagnostic tip/ops.bin "$previous" "+$out/stage-$stage.manifest" "$family" "$out/stage-$stage-$family.tsv" > "$out/stage-$stage-$family.log" 2>&1
  done
  python3 stream_resources.py "$previous" > "$out/stage-$stage-resources.jsonl"
done
