#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=scratch-v2-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$out/launcher.exit"' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 CARGO_BUILD_JOBS=4
source /home/hclau/.cargo/env
ulimit -v 41943040
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/preflight.json"
python3 prepare_scratch.py
CARGO_TARGET_DIR="$root/target-scratch" cargo test --release --locked --offline --manifest-path scratch-tool/Cargo.toml scratch_tests > "$out/native-tests.log" 2>&1
CARGO_TARGET_DIR="$root/target-scratch" cargo build --release --locked --offline --manifest-path scratch-tool/Cargo.toml > "$out/build.log" 2>&1
for cap in 128 512 1024 2048; do
  name="$out/wide-$cap-extra8"
  python3 /home/hclau/ecdsa_research/server-preflight.py > "$name-preflight.json"
  EXACT_MODE=cache-retained CACHE_SPLIT=1 CACHE_RANK=density CACHE_ATOM_CAP="$cap" ANF_PAIR_CAP=64 CACHE_PRODUCT_CAP=1000000 CACHE_EXTRA_QUBITS=8 /usr/bin/time -v ./target-scratch/release/product_paired_diagnostic wide-chain-retained.bin "$name.bin" > "$name-generate.log" 2>&1
  cp wide-chain.manifest "$name.manifest"
  printf '%s %s\n' "$name.bin" "$name-generate.log" >> "$name.manifest"
  for family in independent structured; do
    /usr/bin/time -v ./target-replay/release/product_paired_diagnostic /home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin "$name.bin" "+$name.manifest" "$family" "$name-$family.tsv" > "$name-$family.log" 2>&1
  done
  sha256sum "$name.bin" >> "$out/streams.sha256"
done
