#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=guard-cache-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$root/$out/launcher.exit"' EXIT
source /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 41943040
printf '%s\n' 'Predetermined before measurement: exactBoolean BDD models classical conditions (snapshotted pushes, conditional bit updates, fresh HMR variables) to rank/filter cache proposals by sum(probability)-union(probability). Uniform probabilities for classical input bits are selection heuristics only. No simulator packets inform selection. Existing exact retained ANF cache rewrite, compact flags, no extra qubits. Separately test cap128/512/1024 starting from immutable original4b and frozen wide15, density/split/pair64/product1M. Each result requires full original-to-final anchored reconstruction on independent and structured256shots; no scored claim or nonce search.' > "$out/DECLARATION.txt"
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/build-preflight.json"
python3 prepare_guard_cache.py > "$out/prepare.log" 2>&1
CARGO_TARGET_DIR="$root/target-guard-cache" cargo test --manifest-path guard-cache-tool/Cargo.toml --release --locked --offline --bin product_paired_diagnostic guard_bdd -- --test-threads=1 > "$out/bdd-native-tests.log" 2>&1
CARGO_TARGET_DIR="$root/target-guard-cache" cargo test --manifest-path guard-cache-tool/Cargo.toml --release --locked --offline --bin product_paired_diagnostic lazy_cache_retained -- --test-threads=1 > "$out/cache-native-tests.log" 2>&1
CARGO_TARGET_DIR="$root/target-guard-cache" cargo build --manifest-path guard-cache-tool/Cargo.toml --release --locked --offline --bin product_paired_diagnostic > "$out/build.log" 2>&1
for family in product wide; do
  if [ "$family" = product ]; then
    original=tip/ops.bin;input="$original";prefix=empty
  else
    original=/home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin
    input=wide-compound-20261016/wide-15-retained-512.bin;prefix=wide-compound-20261016/chain.manifest
  fi
  for cap in 128 512 1024; do
    name="$out/$family-$cap"
    python3 /home/hclau/ecdsa_research/server-preflight.py > "$name-preflight.json"
    EXACT_MODE=cache-retained CACHE_SPLIT=1 CACHE_RANK=density CACHE_ATOM_CAP="$cap" ANF_PAIR_CAP=64 CACHE_PRODUCT_CAP=1000000 /usr/bin/time -v ./target-guard-cache/release/product_paired_diagnostic "$input" "$name.bin" > "$name-generate.log" 2>&1
    if [ "$prefix" = empty ]; then : > "$name.manifest"; else cp "$prefix" "$name.manifest"; fi
    if cmp -s "$input" "$name.bin"; then mapping==; else mapping="$name-generate.log"; fi
    printf '%s %s\n' "$name.bin" "$mapping" >> "$name.manifest"
    sha256sum "$name.bin" > "$name.sha256"
    for packet in independent structured; do
      /usr/bin/time -v ./target-anchored-replay/release/product_paired_diagnostic "$original" "$name.bin" "+$name.manifest" "$packet" "$name-$packet.tsv" > "$name-$packet.log" 2>&1
    done
    python3 stream_resources.py "$name.bin" > "$name-resources.jsonl"
  done
done
