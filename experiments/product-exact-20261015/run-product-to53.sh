#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=product-to53-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$out/launcher.exit"' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 41943040
printf '%s\n' 'Predetermined before continuation measurements: exactly four seven-stage cycles after frozen25, ending53; each cycle retained128,retained512,retained1024,plainANF512,retained128,retained512,retained1024; paircap64/productcap1M/density/split, no added qubits, three private flags per donor with disjoint leases. Anchored original MR words, independent added-cache MR words. Checkpoints32/39/46/53. No failure-based stopping or stage selection. One symbolic thread,40GiB address-space limit; preserve resource failures.' > "$out/DECLARATION.txt"
while [ ! -f product25-native-generate.log ]; do
  if [ -f product25-native.exit ]; then test "$(cat product25-native.exit)" = 0; fi
  sleep 30
done
test "$(cat product-continuation-20261016/launcher.exit)" = 0
previous=product-continuation-20261016/product-25-retained-1024.bin
sha256sum "$previous" > "$out/input.sha256"
cp product-continuation-20261016/stage-25.manifest "$out/chain.manifest"
stage=25
for cycle in 1 2 3 4; do
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
