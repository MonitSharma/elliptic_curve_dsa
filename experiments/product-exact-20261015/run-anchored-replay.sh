#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=anchored-replay-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$out/launcher.exit"' EXIT
source /home/hclau/.cargo/env
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 CARGO_BUILD_JOBS=4
ulimit -v 41943040
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/preflight.json"
python3 prepare_anchored_replay.py
CARGO_TARGET_DIR="$root/target-anchored-replay" cargo build --release --locked --offline --manifest-path anchored-replay/Cargo.toml > "$out/build.log" 2>&1
one() {
  name=$1; original=$2; final=$3; manifest=$4
  for family in independent structured; do
    /usr/bin/time -v ./target-anchored-replay/release/product_paired_diagnostic "$original" "$final" "+$manifest" "$family" "$out/$name-$family.tsv" > "$out/$name-$family.log" 2>&1
  done
}
wide=/home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin
one product-four tip/ops.bin chain-retained.bin chain.manifest
one product-eleven tip/ops.bin follow-chain-20261016/product-7-retained-1024.bin follow-chain-20261016/product.manifest
one product-four-flags tip/ops.bin flags-four-20261016/product-4-retained-512.bin flags-four-20261016/chain.manifest
one wide-four "$wide" wide-chain-retained.bin wide-chain.manifest
one wide-eleven "$wide" follow-chain-20261016/wide-7-retained-1024.bin follow-chain-20261016/wide.manifest
for cap in 128 512 1024 2048; do
  one "wide-scratch-$cap" "$wide" "scratch-v2-20261016/wide-$cap-extra8.bin" "scratch-v2-20261016/wide-$cap-extra8.manifest"
done
for cap in 128 512 1024; do
  if [ -f "unfold-20261016/wide-$cap.bin" ]; then one "wide-unfold-$cap" "$wide" "unfold-20261016/wide-$cap.bin" "unfold-20261016/wide-$cap.manifest"; fi
done
for pairs in 256 1024; do
  for cap in 128 512; do
    if [ -f "pair-expansion-20261016/wide-$pairs-$cap.bin" ]; then one "wide-pairs-$pairs-$cap" "$wide" "pair-expansion-20261016/wide-$pairs-$cap.bin" "pair-expansion-20261016/wide-$pairs-$cap.manifest"; fi
  done
done
