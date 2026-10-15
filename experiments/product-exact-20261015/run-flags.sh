#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=flags-chain-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$out/launcher.exit"' EXIT
source /home/hclau/.cargo/env
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 CARGO_BUILD_JOBS=4
ulimit -v 41943040
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/preflight.json"
python3 prepare_flags.py
CARGO_TARGET_DIR="$root/target-flags" cargo test --release --locked --offline --manifest-path flags-tool/Cargo.toml lazy_cache -- --test-threads=1 > "$out/native-tests.log" 2>&1
CARGO_TARGET_DIR="$root/target-flags" cargo build --release --locked --offline --manifest-path flags-tool/Cargo.toml > "$out/build.log" 2>&1
CARGO_TARGET_DIR="$root/target-flags-replay" cargo build --release --locked --offline --manifest-path flags-replay/Cargo.toml > "$out/replay-build.log" 2>&1
for track in product wide; do
  if [ "$track" = product ]; then previous=chain-retained.bin; original=tip/ops.bin; cp chain.manifest "$out/$track.manifest"; else previous=wide-chain-retained.bin; original=/home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin; cp wide-chain.manifest "$out/$track.manifest"; fi
  stage=0
  for spec in retained:128 retained:512 retained:1024 anf:512 retained:128 retained:512 retained:1024; do
    stage=$((stage+1));mode=${spec%:*};cap=${spec#*:};name="$out/$track-$stage-$mode-$cap"
    python3 /home/hclau/ecdsa_research/server-preflight.py > "$name-preflight.json"
    EXACT_MODE="cache-$mode" CACHE_SPLIT=1 CACHE_RANK=density CACHE_ATOM_CAP="$cap" ANF_PAIR_CAP=64 CACHE_PRODUCT_CAP=1000000 /usr/bin/time -v ./target-flags/release/product_paired_diagnostic "$previous" "$name.bin" > "$name-generate.log" 2>&1
    if cmp -s "$previous" "$name.bin"; then mapping==; else mapping="$name-generate.log"; fi
    printf '%s %s\n' "$name.bin" "$mapping" >> "$out/$track.manifest"
    sha256sum "$name.bin" >> "$out/$track.sha256"
    previous="$name.bin"
  done
  for family in independent structured; do
    /usr/bin/time -v ./target-flags-replay/release/product_paired_diagnostic "$original" "$previous" "+$out/$track.manifest" "$family" "$out/$track-$family.tsv" > "$out/$track-$family.log" 2>&1
  done
done
