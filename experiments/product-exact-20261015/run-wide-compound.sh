#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=wide-compound-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$out/launcher.exit"' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 41943040
test "$(cat follow-chain-20261016/wide.exit)" = 0
cp follow-chain-20261016/wide.manifest "$out/chain.manifest"
previous=follow-chain-20261016/wide-7-retained-1024.bin
stage=11
for spec in scratch:1024:64 unfold:128:64 affine:128:64 retained:512:256; do
  stage=$((stage+1));IFS=: read -r mode cap pairs <<< "$spec";name="$out/wide-$stage-$mode-$cap"
  python3 /home/hclau/ecdsa_research/server-preflight.py > "$name-preflight.json"
  case "$mode" in
    scratch) exe=target-scratch/release/product_paired_diagnostic; exact_mode=cache-retained; extra=8;;
    unfold) exe=target-unfold/release/product_paired_diagnostic; exact_mode=cache-retained; extra=0;;
    affine) exe=target-conditional/release/product_paired_diagnostic; exact_mode=cache; extra=0;;
    retained) exe=target-retained/release/product_paired_diagnostic; exact_mode=cache-retained; extra=0;;
  esac
  EXACT_MODE="$exact_mode" CACHE_SPLIT=1 CACHE_RANK=density CACHE_ATOM_CAP="$cap" ANF_PAIR_CAP="$pairs" CACHE_PRODUCT_CAP=1000000 CACHE_EXTRA_QUBITS="$extra" /usr/bin/time -v "$exe" "$previous" "$name.bin" > "$name-generate.log" 2>&1
  if cmp -s "$previous" "$name.bin"; then mapping==; else mapping="$name-generate.log"; fi
  printf '%s %s\n' "$name.bin" "$mapping" >> "$out/chain.manifest"
  sha256sum "$name.bin" >> "$out/streams.sha256"
  previous="$name.bin"
done
for family in independent structured; do
  /usr/bin/time -v ./target-replay/release/product_paired_diagnostic /home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin "$previous" "+$out/chain.manifest" "$family" "$out/wide-$family.tsv" > "$out/wide-$family.log" 2>&1
done
python3 stream_resources.py "$previous" > "$out/resources.jsonl"
