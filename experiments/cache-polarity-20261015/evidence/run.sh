#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/cache-polarity-20261015
old=/home/hclau/ecdsa_research/toffoli-readiness-20261015
base=/home/hclau/ecdsa_research/overnight-20261014/product-evidence/b3-baseline/run/ops.bin
echo $$ > "$root/run.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$root/run.exit"' EXIT
ulimit -v 33554432
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export CACHE_ATOM_CAP=128 CACHE_PRODUCT_CAP=1000000
python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/preflight.json"
python3 "$root/prepare.py" > "$root/prepare.log" 2>&1
export CARGO_TARGET_DIR="$root/analyzer-target"
cd "$root/analyzer"
cargo test --release --locked --offline -- --nocapture --test-threads=1 > "$root/tests.log" 2>&1
cargo build --release --locked --offline > "$root/build.log" 2>&1
/usr/bin/time -v "$CARGO_TARGET_DIR/release/product_paired_diagnostic" "$base" "$root/polarity.bin" > "$root/generation.log" 2>&1
sha256sum "$base" "$root/polarity.bin" "$CARGO_TARGET_DIR/release/product_paired_diagnostic" > "$root/streams.sha256"
export CARGO_TARGET_DIR="$root/replay-target"
cd "$root/replay"
cargo build --release --locked --offline > "$root/replay-build.log" 2>&1
for family in independent structured; do
    /usr/bin/time -v "$CARGO_TARGET_DIR/release/product_paired_diagnostic" "$base" "$root/polarity.bin" "$root/generation.log" "$family" "$root/$family.tsv" > "$root/$family.log" 2>&1
    cmp "$root/$family.tsv" "$old/wide-replay/$family.tsv"
done
sha256sum "$root"/*.log "$root"/*.tsv "$CARGO_TARGET_DIR/release/product_paired_diagnostic" > "$root/results.sha256"
