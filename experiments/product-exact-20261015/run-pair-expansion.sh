#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=pair-expansion-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$out/launcher.exit"' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 41943040
for track in wide product; do
  if [ "$track" = product ]; then previous=chain-retained.bin; original=tip/ops.bin; else previous=wide-chain-retained.bin; original=/home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin; fi
  for pairs in 256 1024; do
    for cap in 128 512; do
      name="$out/$track-$pairs-$cap"
      python3 /home/hclau/ecdsa_research/server-preflight.py > "$name-preflight.json"
      EXACT_MODE=cache-retained CACHE_SPLIT=1 CACHE_RANK=density CACHE_ATOM_CAP="$cap" ANF_PAIR_CAP="$pairs" CACHE_PRODUCT_CAP=1000000 /usr/bin/time -v ./target-retained/release/product_paired_diagnostic "$previous" "$name.bin" > "$name-generate.log" 2>&1
      if [ "$track" = product ]; then cp chain.manifest "$name.manifest"; else cp wide-chain.manifest "$name.manifest"; fi
      if cmp -s "$previous" "$name.bin"; then mapping==; else mapping="$name-generate.log"; fi
      printf '%s %s\n' "$name.bin" "$mapping" >> "$name.manifest"
      for family in independent structured; do
        /usr/bin/time -v ./target-replay/release/product_paired_diagnostic "$original" "$name.bin" "+$name.manifest" "$family" "$name-$family.tsv" > "$name-$family.log" 2>&1
      done
      sha256sum "$name.bin" >> "$out/streams.sha256"
    done
  done
done
