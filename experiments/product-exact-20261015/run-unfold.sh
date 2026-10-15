#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=unfold-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$out/launcher.exit"' EXIT
source /home/hclau/.cargo/env
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 CARGO_BUILD_JOBS=4
ulimit -v 41943040
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/preflight.json"
python3 prepare_unfold.py
CARGO_TARGET_DIR="$root/target-unfold" cargo test --release --locked --offline --manifest-path unfold-tool/Cargo.toml unfold_tests > "$out/native-tests.log" 2>&1
CARGO_TARGET_DIR="$root/target-unfold" cargo build --release --locked --offline --manifest-path unfold-tool/Cargo.toml > "$out/build.log" 2>&1
for track in wide product; do
  if [ "$track" = product ]; then previous=chain-retained.bin; original=tip/ops.bin; else previous=wide-chain-retained.bin; original=/home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin; fi
  for cap in 128 512 1024; do
    name="$out/$track-$cap"
    python3 /home/hclau/ecdsa_research/server-preflight.py > "$name-preflight.json"
    EXACT_MODE=cache-retained CACHE_SPLIT=1 CACHE_RANK=density CACHE_ATOM_CAP="$cap" ANF_PAIR_CAP=64 CACHE_PRODUCT_CAP=1000000 /usr/bin/time -v ./target-unfold/release/product_paired_diagnostic "$previous" "$name.bin" > "$name-generate.log" 2>&1
    if [ "$track" = product ]; then cp chain.manifest "$name.manifest"; else cp wide-chain.manifest "$name.manifest"; fi
    printf '%s %s\n' "$name.bin" "$name-generate.log" >> "$name.manifest"
    for family in independent structured; do
      /usr/bin/time -v ./target-replay/release/product_paired_diagnostic "$original" "$name.bin" "+$name.manifest" "$family" "$name-$family.tsv" > "$name-$family.log" 2>&1
    done
    sha256sum "$name.bin" >> "$out/streams.sha256"
  done
done
