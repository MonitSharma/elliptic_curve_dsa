#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=cached-witness-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$out/launcher.exit"' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 41943040
for track in product wide; do
  if [ "$track" = product ]; then previous=flags-extended-20261016/product-11-retained-1024.bin; original=tip/ops.bin; manifest=flags-extended-20261016/chain.manifest; else previous=wide-compound-20261016/wide-15-retained-512.bin; original=/home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin; manifest=wide-compound-20261016/chain.manifest; fi
  for cap in 128 512; do
    name="$out/$track-$cap"
    python3 /home/hclau/ecdsa_research/server-preflight.py > "$name-preflight.json"
    EXACT_MODE=context-witness CACHE_ATOM_CAP="$cap" ANF_PAIR_CAP=64 CACHE_PRODUCT_CAP=1000000 /usr/bin/time -v ./target-conditional/release/product_paired_diagnostic "$previous" "$name.bin" > "$name-generate.log" 2>&1
    sha256sum "$name.bin" >> "$out/streams.sha256"
    if cmp -s "$previous" "$name.bin"; then printf '%s\n' 'Byte-identical: no additional witness rewrite.' > "$name-STATUS.txt";continue; fi
    cp "$manifest" "$name.manifest";printf '%s %s\n' "$name.bin" = >> "$name.manifest"
    for family in independent structured; do
      /usr/bin/time -v ./target-anchored-replay/release/product_paired_diagnostic "$original" "$name.bin" "+$name.manifest" "$family" "$name-$family.tsv" > "$name-$family.log" 2>&1
    done
  done
done
