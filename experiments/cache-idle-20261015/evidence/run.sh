#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/cache-idle-20261015
old=/home/hclau/ecdsa_research/toffoli-readiness-20261015
base=/home/hclau/ecdsa_research/overnight-20261014/product-evidence/b3-baseline/run/ops.bin
echo $$ > "$root/run.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$root/run.exit"' EXIT
ulimit -v 33554432
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export CARGO_TARGET_DIR="$root/target"
python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/preflight.json"
python3 "$root/prepare.py" > "$root/prepare.log" 2>&1
cd "$root/analyzer"
cargo test --release --locked --offline -- --nocapture --test-threads=1 > "$root/tests.log" 2>&1
cargo build --release --locked --offline > "$root/build.log" 2>&1
for config in 32-200000 128-1000000; do
    export CACHE_ATOM_CAP="${config%-*}" CACHE_PRODUCT_CAP="${config#*-}"
    /usr/bin/time -v "$CARGO_TARGET_DIR/release/product_paired_diagnostic" "$base" "$root/$config.bin" > "$root/$config-generation.log" 2>&1
    sha256sum "$root/$config.bin" > "$root/$config-stream.sha256"
    if test "$config" = 32-200000; then cmp "$root/$config.bin" "$old/candidate-b3-cache-v1/ops.bin"; fi
done
sha256sum "$base" "$CARGO_TARGET_DIR/release/product_paired_diagnostic" "$old/wide-replay/paired_diagnostic" > "$root/inputs.sha256"
for family in independent structured; do
    /usr/bin/time -v "$old/wide-replay/paired_diagnostic" "$base" "$root/128-1000000.bin" "$root/128-1000000-generation.log" "$family" "$root/$family.tsv" > "$root/$family.log" 2>&1
    cmp "$root/$family.tsv" "$old/wide-replay/$family.tsv"
done
sha256sum "$root"/*.log "$root"/*.tsv > "$root/results.sha256"
