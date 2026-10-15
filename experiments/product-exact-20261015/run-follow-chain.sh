#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=follow-chain-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$out/launcher.exit"' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 41943040
one_track() {
  track=$1
  echo "$BASHPID" > "$out/$track.pid"
  if [ "$track" = product ]; then
    original=tip/ops.bin; previous=chain-retained.bin
    cp chain.manifest "$out/$track.manifest"
  else
    original=/home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin
    previous=wide-chain-retained.bin
    cp wide-chain.manifest "$out/$track.manifest"
  fi
  stage=0
  for spec in retained:128 retained:512 retained:1024 anf:512 retained:128 retained:512 retained:1024; do
    stage=$((stage+1)); mode=${spec%:*}; cap=${spec#*:}
    name="$out/$track-$stage-$mode-$cap"
    python3 /home/hclau/ecdsa_research/server-preflight.py > "$name-preflight.json"
    if [ "$mode" = retained ]; then
      exe=target-retained/release/product_paired_diagnostic
    else
      exe=target-conditional/release/product_paired_diagnostic
    fi
    EXACT_MODE="cache-$mode" CACHE_SPLIT=1 CACHE_RANK=density CACHE_ATOM_CAP="$cap" ANF_PAIR_CAP=64 CACHE_PRODUCT_CAP=1000000 /usr/bin/time -v "$exe" "$previous" "$name.bin" > "$name-generate.log" 2>&1
    printf '%s %s\n' "$name.bin" "$name-generate.log" >> "$out/$track.manifest"
    sha256sum "$name.bin" >> "$out/$track.sha256"
    previous="$name.bin"
  done
  for family in independent structured; do
    /usr/bin/time -v ./target-replay/release/product_paired_diagnostic "$original" "$previous" "+$out/$track.manifest" "$family" "$out/$track-$family.tsv" > "$out/$track-$family.log" 2>&1
  done
  echo 0 > "$out/$track.exit"
}
one_track product > "$out/product-launcher.log" 2>&1 &
product_pid=$!
one_track wide > "$out/wide-launcher.log" 2>&1 &
wide_pid=$!
wait "$product_pid"
wait "$wide_pid"
