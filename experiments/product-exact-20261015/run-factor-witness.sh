#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=factor-witness-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$root/$out/launcher.exit"' EXIT
printf '%s\n' 'Predetermined exact live-witness CCXtoCX only: factorarity256/512/1024 with ANFatomcap128/pair64/productcap1M on original4b and original5a. No extra qubits/classical/MR; every changed row logged and independently reconstructed; all other56-byte records identical. Same originalMR words in anchored independent/structured256shots. No scored claim or nonce/packet selection. One thread/20GiB virtual limit; analysis waits product53/wide43/weightedmodel terminal for memory.' > "$out/DECLARATION.txt"
source /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 20971520
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/build-preflight.json"
python3 prepare_factor_witness.py > "$out/prepare.log" 2>&1
FACTOR_CAP=256 CARGO_TARGET_DIR="$root/target-factor-witness" cargo test --manifest-path factor-witness-tool/Cargo.toml --release --locked --offline --bin product_paired_diagnostic interned_anf_retained::anf_tests -- --test-threads=1 > "$out/factor-native-tests.log" 2>&1
CARGO_TARGET_DIR="$root/target-factor-witness" cargo build --manifest-path factor-witness-tool/Cargo.toml --release --locked --offline --bin product_paired_diagnostic > "$out/build.log" 2>&1
while [ ! -f product-to53-20261016/launcher.exit ] || [ ! -f wide-to43-20261016/launcher.exit ] || [ ! -f guard-cache-weighted-20261016/launcher.exit ]; do sleep 30; done
for family in product wide; do
  if [ "$family" = product ]; then input=tip/ops.bin;else input=/home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin;fi
  for cap in 256 512 1024; do
    name="$out/$family-$cap"
    python3 /home/hclau/ecdsa_research/server-preflight.py > "$name-preflight.json"
    EXACT_MODE=witness-only-retained FACTOR_CAP="$cap" CACHE_ATOM_CAP=128 ANF_PAIR_CAP=64 CACHE_PRODUCT_CAP=1000000 /usr/bin/time -v ./target-factor-witness/release/product_paired_diagnostic "$input" "$name.bin" > "$name-generate.log" 2>&1
    python3 certify_witness_rows.py "$input" "$name.bin" "$name-generate.log" > "$name-certificate.json"
    for packet in independent structured; do
      /usr/bin/time -v ./target-anchored-replay/release/product_paired_diagnostic "$input" "$name.bin" = "$packet" "$name-$packet.tsv" > "$name-$packet.log" 2>&1
    done
    python3 stream_resources.py "$name.bin" > "$name-resources.jsonl"
  done
done
