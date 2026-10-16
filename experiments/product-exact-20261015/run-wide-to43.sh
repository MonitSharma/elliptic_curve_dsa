#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=wide-to43-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$root/$out/launcher.exit"' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 41943040
printf '%s\n' 'Predetermined before measurements: exactly four seven-stage cycles after frozen wide15, ending43; retained128,retained512,retained1024,plainANF512,retained128,retained512,retained1024 each cycle; paircap64/productcap1M/density/split, existing Q1468 only, three private flags per donor. Anchored original MR words; independent added-cache MR stream. Checkpoints22/29/36/43. No stage or packet selection. One analysis thread,40GiB virtual-memory limit. Preserve resource failures.' > "$out/DECLARATION.txt"
while [ ! -f wide-compound-native.exit ]; do sleep 30; done
test "$(cat wide-compound-native.exit)" = 0
previous=wide-compound-20261016/wide-15-retained-512.bin
sha256sum "$previous" > "$out/input.sha256"
cp wide-compound-20261016/chain.manifest "$out/chain.manifest"
stage=15
for cycle in 1 2 3 4; do
  for spec in retained:128 retained:512 retained:1024 anf:512 retained:128 retained:512 retained:1024; do
    stage=$((stage+1));mode=${spec%:*};cap=${spec#*:};name="$out/wide-$stage-$mode-$cap"
    python3 /home/hclau/ecdsa_research/server-preflight.py > "$name-preflight.json"
    EXACT_MODE="cache-$mode" CACHE_SPLIT=1 CACHE_RANK=density CACHE_ATOM_CAP="$cap" ANF_PAIR_CAP=64 CACHE_PRODUCT_CAP=1000000 /usr/bin/time -v ./target-flags/release/product_paired_diagnostic "$previous" "$name.bin" > "$name-generate.log" 2>&1
    if cmp -s "$previous" "$name.bin"; then mapping==; else mapping="$name-generate.log"; fi
    printf '%s %s\n' "$name.bin" "$mapping" >> "$out/chain.manifest"
    sha256sum "$name.bin" >> "$out/streams.sha256"
    previous="$name.bin"
  done
  cp "$out/chain.manifest" "$out/stage-$stage.manifest"
  for family in independent structured; do
    /usr/bin/time -v ./target-anchored-replay/release/product_paired_diagnostic /home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin "$previous" "+$out/stage-$stage.manifest" "$family" "$out/stage-$stage-$family.tsv" > "$out/stage-$stage-$family.log" 2>&1
  done
  python3 stream_resources.py "$previous" > "$out/stage-$stage-resources.jsonl"
done
