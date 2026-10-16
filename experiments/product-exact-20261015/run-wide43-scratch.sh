#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=wide43-scratch-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$out/launcher.exit"' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 25165824
printf '%s\n' 'Predetermined: independent additional retained-ANF cache pass on frozen wide43,16 offered fresh quantum scratch slots, atomcaps128/512/1024/2048, pair256/product1M/density/split. All four preserved, no circuit/nonce packet tuning. Original wide43 unchanged; exact native scratch proof applies, complete operation reconstruction and512 anchored value/phase/scratch comparisons required. Extra width allowed only for Toffoli research. One thread24GiB virtual memory; no native score claim.' > "$out/DECLARATION.txt"
test "$(cat wide-to43-20261016/launcher.exit)" = 0
input=wide-to43-20261016/wide-43-retained-1024.bin
for cap in 128 512 1024 2048; do
  name="$out/wide43-$cap"
  python3 /home/hclau/ecdsa_research/server-preflight.py > "$name-preflight.json"
  EXACT_MODE=cache-retained CACHE_SPLIT=1 CACHE_RANK=density CACHE_ATOM_CAP="$cap" ANF_PAIR_CAP=256 CACHE_PRODUCT_CAP=1000000 CACHE_EXTRA_QUBITS=16 /usr/bin/time -v ./target-scratch/release/product_paired_diagnostic "$input" "$name.bin" > "$name-generate.log" 2>&1
  if cmp -s "$input" "$name.bin";then mapping==;else mapping="$name-generate.log";fi
  cp wide-to43-20261016/stage-43.manifest "$name.manifest"
  printf '%s %s\n' "$name.bin" "$mapping" >> "$name.manifest"
  sha256sum "$name.bin" > "$name.sha256"
  for family in independent structured;do
    /usr/bin/time -v ./target-anchored-replay/release/product_paired_diagnostic /home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin "$name.bin" "+$name.manifest" "$family" "$name-$family.tsv" > "$name-$family.log" 2>&1
  done
  python3 stream_resources.py "$name.bin" > "$name-resources.jsonl"
done
