#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=product-to67-rank-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$root/$out/launcher.exit"' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 25165824
printf '%s\n' 'Predetermined no-added-qubit continuation after frozen product53: exactly two seven-stage cycles ending67. Each cycle retained128/start,retained512/proxy,retained1024/start,plainANF512/proxy,retained128/proxy,retained512/start,retained1024/proxy. Pair64/product1M/contiguous split/three fresh flags per donor with disjoint reuse. Rankings depend only on complete source structure, never inputs or failure packets. Checkpoint60/67 both256 independent+256 structured anchored full quantum/classical/phase/scratch comparisons; final67 count fixed before all measurements. No packet-selected stopping, nonce or score claim. One thread24GiB address-space cap; preserve resource failures.' > "$out/DECLARATION.txt"
test "$(cat product-to53-20261016/launcher.exit)" = 0
cp product-to53-20261016/stage-53.manifest "$out/chain.manifest"
previous=product-to53-20261016/product-53-retained-1024.bin
stage=53
for cycle in 1 2;do
  for spec in retained:128:start retained:512:proxy retained:1024:start anf:512:proxy retained:128:proxy retained:512:start retained:1024:proxy;do
    stage=$((stage+1));IFS=: read -r mode cap rank <<< "$spec";name="$out/product-$stage-$mode-$cap-$rank"
    python3 /home/hclau/ecdsa_research/server-preflight.py > "$name-preflight.json"
    EXACT_MODE="cache-$mode" CACHE_SPLIT=1 CACHE_RANK="$rank" CACHE_ATOM_CAP="$cap" ANF_PAIR_CAP=64 CACHE_PRODUCT_CAP=1000000 /usr/bin/time -v ./target-flags/release/product_paired_diagnostic "$previous" "$name.bin" > "$name-generate.log" 2>&1
    if cmp -s "$previous" "$name.bin";then mapping==;else mapping="$name-generate.log";fi
    printf '%s %s\n' "$name.bin" "$mapping" >> "$out/chain.manifest"
    sha256sum "$name.bin" >> "$out/streams.sha256";previous="$name.bin"
  done
  cp "$out/chain.manifest" "$out/stage-$stage.manifest"
  for family in independent structured;do
    /usr/bin/time -v ./target-anchored-replay/release/product_paired_diagnostic tip/ops.bin "$previous" "+$out/stage-$stage.manifest" "$family" "$out/stage-$stage-$family.tsv" > "$out/stage-$stage-$family.log" 2>&1
  done
  python3 stream_resources.py "$previous" > "$out/stage-$stage-resources.jsonl"
done
