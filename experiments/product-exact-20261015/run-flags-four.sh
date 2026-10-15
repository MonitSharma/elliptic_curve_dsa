#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=flags-four-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$out/launcher.exit"' EXIT
source /home/hclau/.cargo/env
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 CARGO_BUILD_JOBS=4
ulimit -v 41943040
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/preflight.json"
python3 prepare_flags_four.py
CARGO_TARGET_DIR="$root/target-flags-four" cargo test --release --locked --offline --manifest-path flags-four-tool/Cargo.toml lazy_cache -- --test-threads=1 > "$out/native-tests.log" 2>&1
CARGO_TARGET_DIR="$root/target-flags-four" cargo build --release --locked --offline --manifest-path flags-four-tool/Cargo.toml > "$out/build.log" 2>&1
previous=tip/ops.bin
: > "$out/chain.manifest"
stage=0
for spec in retained:128 affine:128 anf:512 retained:512; do
  stage=$((stage+1));mode=${spec%:*};cap=${spec#*:};name="$out/product-$stage-$mode-$cap"
  python3 /home/hclau/ecdsa_research/server-preflight.py > "$name-preflight.json"
  EXACT_MODE="cache-$mode" CACHE_SPLIT=1 CACHE_RANK=density CACHE_ATOM_CAP="$cap" ANF_PAIR_CAP=64 CACHE_PRODUCT_CAP=1000000 /usr/bin/time -v ./target-flags-four/release/product_paired_diagnostic "$previous" "$name.bin" > "$name-generate.log" 2>&1
  if cmp -s "$previous" "$name.bin"; then mapping==; else mapping="$name-generate.log"; fi
  printf '%s %s\n' "$name.bin" "$mapping" >> "$out/chain.manifest"
  sha256sum "$name.bin" >> "$out/streams.sha256"
  previous="$name.bin"
done
for family in independent structured; do
  /usr/bin/time -v ./target-flags-replay/release/product_paired_diagnostic tip/ops.bin "$previous" "+$out/chain.manifest" "$family" "$out/product-$family.tsv" > "$out/product-$family.log" 2>&1
done
python3 stream_resources.py "$previous" > "$out/resources.jsonl"
