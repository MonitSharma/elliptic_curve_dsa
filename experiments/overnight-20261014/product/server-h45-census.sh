#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/overnight-20261014/product-h45-census
evidence=/home/hclau/ecdsa_research/overnight-20261014/product-evidence/h45-census
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/run.exit"; python3 ../research-receipt.py . "$evidence/receipt" --log "$evidence/run.log" --exit "$evidence/run.exit" --stream ops.bin; exit "$rc"' EXIT
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/overnight-20261014/product-h45-census-target
ulimit -v 16777216
. /home/hclau/.cargo/env
date -u
hostname
git rev-parse HEAD
git status --short
sha256sum src/point_add/y15_onefold.rs src/point_add/toffoli_carry_cleanup_v1.rs > "$evidence/source.sha256"
/usr/bin/time -v cargo build --offline --locked --release --bin build_circuit
sha256sum "$CARGO_TARGET_DIR/release/build_circuit" > "$evidence/native.sha256"
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit"
sha256sum ops.bin > "$evidence/stream.sha256"
date -u
